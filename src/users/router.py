from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from src.users import controller
from src.utils.db import get_db
from src.auth.schema import ChangePasswordSchema, UserResponseSchema, UserUpdateSchema
from src.auth.models import UsersModel
from src.utils.auth.authentication import allow_all, allow_admin

user_routes = APIRouter(prefix="/users")
session_dependency = Annotated[AsyncSession, Depends(get_db)]


# Protected Routes


@user_routes.get(
    "/users",
    response_model=List[UserResponseSchema],
    status_code=status.HTTP_200_OK
)
async def get_all_users(session: session_dependency, _: UsersModel = Depends(allow_admin)):
    return controller.get_all_users(session)


@user_routes.get(
    "/info/{id}",
    response_model=UserResponseSchema,
    response_model_exclude={"updated_at"},
    status_code=status.HTTP_200_OK
)
async def get_user_info(session: session_dependency, user: UsersModel = Depends(allow_all)):
    return await controller.get_user_info(session, user)


@user_routes.put(
    "/update/{id}",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def update_user(
    body: UserUpdateSchema,
    session: session_dependency,
        user: UsersModel = Depends(allow_all)
):
    return await controller.update_user(body, session, user)


@user_routes.put("/change-password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(
    body: ChangePasswordSchema,
    session: session_dependency,
    user: UsersModel = Depends(allow_all),
):
    return await controller.change_password(session, user, body)


@user_routes.delete(
    "/delete/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    session: session_dependency,
    user: UsersModel = Depends(allow_all)
):
    return await controller.delete_user(session, user)
