import re
from fastapi import HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import jwt

from src.auth.schema import LoginSchema, RenewTokenResponseSchema
from src.auth.models import UsersModel, RefreshTokensModel
from src.utils.auth.passwords import verify_password
from src.utils.settings import settings
from src.utils.auth.authentication import create_auth_tokens

USERNAME_REGEX = r"^[a-zA-Z0-9_]+$"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PASSWORD_REGEX = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
PHONE_REGEX = r"^\+?[0-9\s\-()]{7,15}$"

PASSWORD_RULE_MESSAGE = "Password should be atleast 8 characters in length, atleast one lower case letter, atleast one upper case letter, atleast one digit, atleast one special character (#?!@$%^&*-)."


async def user_login(body: LoginSchema, session: AsyncSession, request: Request) -> LoginSchema:
    identifier = body.identifier.strip()

    if re.fullmatch(EMAIL_REGEX, identifier):
        key = "email"
    elif re.fullmatch(PHONE_REGEX, identifier):
        key = "phone_number"
    elif re.fullmatch(USERNAME_REGEX, identifier):
        key = "username"
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Identifier.")

    if not re.fullmatch(PASSWORD_REGEX, body.password.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_RULE_MESSAGE)

    try:
        user = await session.scalar(select(UsersModel).where(getattr(UsersModel, key) == identifier))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid {key} or password.")

        # Delete expired tokens for the current user
        await session.execute(delete(RefreshTokensModel).where(RefreshTokensModel.user_id == user.id, RefreshTokensModel.expires_at < datetime.now(timezone.utc)))
        await session.commit()

        if not verify_password(body.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password.")

        tokens = await create_auth_tokens(user.id, session, request)
        return tokens

    except SQLAlchemyError as error:
        print(f"Error while Login :: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong on the server, please try again later.")


async def renew_access_token(refresh_token: str, user_id: str, session: AsyncSession, request: Request) -> RenewTokenResponseSchema:
    try:
        if user_id:
            # Check if user actually exist.
            user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found.")

            # Delete all expired tokens for this user from DB.
            await session.execute(delete(RefreshTokensModel).where(RefreshTokensModel.user_id == user_id, RefreshTokensModel.expires_at < datetime.now(timezone.utc)))
            await session.commit()

        # Cryptographically verify the refresh token
        data = jwt.decode(refresh_token, settings.SECRET_KEY,
                          algorithms=[settings.ALGORITHM])

        # Ensure if it's actually a Refresh token.
        if not data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh Token.")

        # Ensure token belongs to the logged-in user.
        user_id_jwt = data.get("_id")
        if not user_id_jwt == user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Token doesn't belong to the current user.")

        # Check if token exist in DB
        db_token = await session.scalar(select(RefreshTokensModel).where(RefreshTokensModel.token == refresh_token, RefreshTokensModel.user_id == user.id))
        if not db_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Refresh token has been revoked or logged out.")

        # Generate Access Token
        return await create_auth_tokens(user.id, session, request, True, refresh_token)

    except jwt.PyJWKError as error:
        print("Error while decoding refresh token :: ", error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh Token.")

    except jwt.ExpiredSignatureError as expErr:
        print("Error while decoding refresh token :: ", expErr)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh Token has expired. Please log in again.")

    except SQLAlchemyError as err:
        await session.rollback()
        print(f"Error in deleting tokens while renewing-access-token : {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong in the server. Please try again later.")


async def logout(refresh_token: str, session: AsyncSession, user: UsersModel):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Refresh Token.")

    try:
        token = await session.scalar(select(RefreshTokensModel).where(RefreshTokensModel.token == refresh_token, RefreshTokensModel.user_id == user.id))
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Refresh Token!")

        await session.delete(token)
        await session.commit()
        return None

    except SQLAlchemyError as error:
        print(f"Error while Logout :: {error}")
        raise HTTPException(
            500, f"Something went wrong in the server, please try again later.")


async def logout_from_other_devices(refresh_token: str, session: AsyncSession, user: UsersModel):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Refresh Token.")

    try:
        await session.execute(delete(RefreshTokensModel).where(RefreshTokensModel.token != refresh_token, RefreshTokensModel.user_id == user.id))
        await session.commit()
        return None

    except SQLAlchemyError as err:
        print(f"Error while Logging out from other devices :: {err}")
        await session.rollback()
        raise HTTPException(
            500, f"Something went wrong in the server, please try again later.")
