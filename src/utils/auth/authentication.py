from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import jwt
from src.auth.models import UsersModel
from src.auth.schema import LoginSchema, RenewTokenResponseSchema
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

async def create_auth_tokens(user_id: str, session: AsyncSession, is_renew: bool = False,) -> dict : 
  user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))

  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid User ID!")
  
  # Create Access Token
  access_token_expiry_time = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRY_MINUTES)
  access_token = jwt.encode({"_id": str(user.id), "username": user.username, "exp": access_token_expiry_time}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

  if is_renew:
    return { "access_token": access_token }

  # Create Refresh Token only if is_renew == True.
  refresh_token_expiry_days = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS)
  refresh_token = jwt.encode({"_id": str(user.id), "username": user.username, "exp": refresh_token_expiry_days, "refresh": True }, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  
  return { "access_token": access_token, "refresh_token": refresh_token }
