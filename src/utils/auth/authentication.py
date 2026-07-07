from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import jwt
from ua_parser import UserAgent
from user_agents import parse

from src.auth.models import UsersModel, RefreshTokensModel
from src.auth.schema import DeviceDetails
from src.utils.settings import settings
from src.utils.db import get_db


security_scheme = HTTPBearer()

async def is_authenticated(
  credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
  session: AsyncSession = Depends(get_db)
):
  token = credentials.credentials.split(" ")[1]

  try:
    data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
  except jwt.ExpiredSignatureError as error:
    print("ExpiredSignatureError :: ", error)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired. Please renew.")
  except jwt.InvalidTokenError as err:
    print("Invalid Token Error :: ", err)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token.")
  
  if data.get("refresh") is True:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Access Token!")

  user_id = data.get("_id")
  user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))

  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are Not Authorized!")
  
  return user

def get_client_details(client: UserAgent):
  device_type = "Mobile" if client.is_mobile else "Tablet" if client.is_tablet else "PC"
  device_brand = client.device.brand or "Generic"
  device_model = client.device.model or "Device"
  device_name = f"{device_brand} {device_model}".strip()
  os_name = client.os.family
  os_version = client.os.version_string
  operating_system = f"{os_name} {os_version}"
  browser = client.get_browser()

  device_details = DeviceDetails(
    device_type = device_type, 
    device_name = device_name, 
    operating_system = operating_system, 
    browser = browser
  )

  return device_details


async def create_auth_tokens(user_id: str, session: AsyncSession, request: Request, is_renew: bool = False, refresh_token : str = None, device_details: dict = None) -> dict : 
  user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))

  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid User ID!")
  
  # Create Access Token
  access_token_expiry_time = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRY_MINUTES)
  access_token = jwt.encode({"_id": str(user.id), "username": user.username, "exp": access_token_expiry_time}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

  if is_renew and refresh_token:
    # check if refresh_token is valid.
    try:
      token = await session.scalar(select(RefreshTokensModel).where(RefreshTokensModel.token == refresh_token))
      db_expires_at = token.expires_at

      if db_expires_at.tzinfo is None:
        db_expires_at = db_expires_at.replace(tzinfo = timezone.utc)


      if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Refresh Token!")
      elif token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token Expired! Please login to continue.")
      else:
        return { "access_token": access_token }
      
    except SQLAlchemyError as error:
      print(f"Error while fetching Refresh token with token: {refresh_token} ::: {error}")
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")

  # Create Refresh Token only if is_renew == False.
  refresh_token_expiry_days = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS)
  refresh_token = jwt.encode({"_id": str(user.id), "username": user.username, "exp": refresh_token_expiry_days, "refresh": True }, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

  client_ip = request.client.host if request.client else "Unknown"
  client = parse(request.headers.get("user-agent"))
  client_details = get_client_details(client)
  client_details.ip_address = client_ip

  # store at refresh_tokens table.
  try: 
    token = RefreshTokensModel(token = refresh_token, expires_at = refresh_token_expiry_days, device_info = str(client_details), user_id = user_id )
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return { "access_token": access_token, "refresh_token": refresh_token }

  except SQLAlchemyError as error: 
    await session.rollback()
    print(f"Error while saving Refresh token :: {error}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")
  
  
