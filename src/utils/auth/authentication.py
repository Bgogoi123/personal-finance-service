from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import jwt
from user_agents import parse

from src.auth.models import UsersModel, RefreshTokensModel
from src.utils.settings import settings
from src.utils.db import get_db

security_scheme = HTTPBearer()


async def is_authenticated(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    try:
        data = jwt.decode(token, settings.SECRET_KEY,
                          algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError as error:
        print("ExpiredSignatureError :: ", error)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has expired. Please renew.")
    except jwt.InvalidTokenError as err:
        print("Invalid Token Error :: ", err)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token.")

    if data.get("refresh") is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Access Token!")

    user_id = data.get("_id")
    # user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))

    # 'Joinedload' ensures user.role is loaded in 1 query.
    # SQL Equivalent is:
    # "SELECT users.*, roles.* FROM users LEFT OUTER JOIN roles ON roles.id = users.role_id;"
    stmt = select(UsersModel).options(joinedload(
        UsersModel.role)).where(UsersModel.id == user_id)
    user = await session.scalar(stmt)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are Not Authorized!")

    return user


async def create_auth_tokens(
    user_id: str,
    session: AsyncSession,
    request: Request,
    is_renew: bool = False,
    refresh_token: str = None,
) -> dict:
    user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid User ID!")

    # Create Access Token
    access_token_expiry_time = datetime.now(
        timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES)
    access_token = jwt.encode(
        {
            "_id": str(user.id), "username": user.username,
            "exp": access_token_expiry_time
        },
        settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    # Renew Access Token
    if is_renew and refresh_token:
        # check if refresh_token is valid.
        try:
            token = await session.scalar(select(RefreshTokensModel).where(
                RefreshTokensModel.token == refresh_token
            ))

            if not token:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Refresh Token!")

            if token.expires_at.tzinfo is None:
                token.expires_at = token.expires_at.replace(
                    tzinfo=timezone.utc)
            elif token.expires_at < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh Token Expired! Please login to continue."
                )
            else:
                return {"access_token": access_token}

        except SQLAlchemyError as error:
            print(
                f"Error while fetching Refresh token with token: {refresh_token} ::: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong on the server, please try again later."
            )

    # Create Refresh Token only if is_renew == False.
    refresh_token_expiry_days = datetime.now(
        timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS)
    refresh_token = jwt.encode(
        {
            "_id": str(user.id),
            "username": user.username,
            "exp": refresh_token_expiry_days,
            "refresh": True
        },
        settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    # Destructure Client's Device Details
    client_ip = request.client.host if request.client else "Unknown"
    client = parse(request.headers.get("user-agent"))
    device_type = "Mobile" if client.is_mobile else "Tablet" if client.is_tablet else "PC"
    device_name = f"{client.device.brand or "Generic"} {client.device.model or "Device"}".strip()
    operating_system = f"{client.os.family} {client.os.version_string}"
    browser = client.get_browser()

    client_details = {
        "ip_address": client_ip,
        "device_type": device_type,
        "device_name": device_name,
        "operating_system": operating_system,
        "browser": browser
    }

    # print("client details ::: ", client_details)

    refresh_token_expiry_days = datetime.now(
        timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS)
    refresh_token = jwt.encode(
        {
            "_id": str(user.id),
            "username": user.username,
            "exp": refresh_token_expiry_days,
            "refresh": True
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    # store at refresh_tokens table.
    try:
        stmt = (select(RefreshTokensModel).where(
            RefreshTokensModel.user_id == user_id,
            RefreshTokensModel.device_info["operating_system"].as_string(
            ) == client_details["operating_system"],
            RefreshTokensModel.device_info["browser"].as_string(
            ) == client_details["browser"]
        ))
        existing_session = await session.scalar(stmt)

        if existing_session:
            # Replace the old token with the new one instead of adding a row
            existing_session.token = refresh_token
            existing_session.expires_at = refresh_token_expiry_days

            await session.commit()
            await session.refresh(existing_session)
            return {"access_token": access_token, "refresh_token": refresh_token}
        else:
            # Create a completely new session row
            token = RefreshTokensModel(
                token=refresh_token,
                expires_at=refresh_token_expiry_days,
                device_info=client_details,
                user_id=user_id
            )
            session.add(token)
            await session.commit()
            await session.refresh(token)
            return {"access_token": access_token, "refresh_token": refresh_token}

    except SQLAlchemyError as error:
        await session.rollback()
        print(f"Error while saving Refresh token :: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong on the server, please try again later."
        )


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: UsersModel = Depends(is_authenticated)) -> UsersModel:
        # Check if the user's role type matches allowed roles
        if user.role.type not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )
        return user


allow_admin = RoleChecker(["admin"])
allow_all = RoleChecker(["admin", "default"])
