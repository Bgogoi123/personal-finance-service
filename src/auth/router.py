from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from src.auth import controller
from src.utils.db import get_db
from src.auth.schema import ChangePasswordSchema, LoginSchema, UserCreateSchema, UserResponseSchema, UserUpdateSchema
from src.auth.models import UsersModel
from src.utils.auth.authentication import allow_all, allow_admin

auth_routes = APIRouter(prefix="/auth")
session_dependency = Annotated[AsyncSession, Depends(get_db)]


# Public Routes


@auth_routes.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def user_login(body: LoginSchema, session: session_dependency, request: Request):
    return await controller.user_login(body, session, request)


@auth_routes.post("/renew-access-token", status_code=status.HTTP_200_OK)
async def renew_access_token(session: session_dependency, request: Request, refresh_token: str = Header(None, alias='Refresh-Token'), user_id: str = Header(None, alias="User-ID")):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Authorization Header Layout.")

    return await controller.renew_access_token(refresh_token, user_id, session, request)


# Protected Routes


@auth_routes.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(session: session_dependency, user: UsersModel = Depends(allow_all), refresh_token: str = Header(None, alias="Refresh-Token")):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Authorization Header Layout.")

    return await controller.logout(refresh_token, session, user)


@auth_routes.post("/logout-other-devices", status_code=status.HTTP_204_NO_CONTENT)
async def logout_from_other_devices(session: session_dependency, user: UsersModel = Depends(allow_all), refresh_token: str = Header(None, alias="Refresh-Token")):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Authorization Header Layout.")

    return await controller.logout_from_other_devices(refresh_token, session, user)
