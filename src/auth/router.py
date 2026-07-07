from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from user_agents import parse

from src.auth import controller
from src.utils.db import get_db
from src.auth.schema import UserCreateSchema, UserUpdateSchema, UserResponseSchema, LoginSchema
from src.auth.models import UsersModel
from src.utils.auth.authentication import is_authenticated

auth_routes = APIRouter(prefix="/auth")
session_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[UsersModel, Depends(is_authenticated)]

@auth_routes.post("/register", response_model=UserResponseSchema, response_model_exclude={"updated_at"}, status_code=status.HTTP_201_CREATED)
async def user_registration(body: UserCreateSchema, session: session_dependency):
  return await controller.user_registration(body, session)

@auth_routes.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def user_login(body: LoginSchema, session: session_dependency, request : Request):
  return await controller.user_login(body, session, request)

@auth_routes.post("/renew-access-token", status_code=status.HTTP_200_OK)
async def renew_access_token(refresh_token: str, session: session_dependency, request: Request):
  return await controller.renew_access_token(refresh_token, session, request)

@auth_routes.get(
    "/profile/{id}",
    response_model=UserResponseSchema,
    response_model_exclude={"updated_at"},
    status_code=status.HTTP_200_OK
  )
async def get_profile_info(session: session_dependency, user: user_dependency):
  return await controller.get_profile_info(session, user)

@auth_routes.put("/update/{id}", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def update_profile(body: UserUpdateSchema, session: session_dependency, user: user_dependency):
  return await controller.update_profile(body, session, user)

@auth_routes.delete("/delete/{id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(session: session_dependency, user: user_dependency):
  return await controller.delete_account(session, user)
