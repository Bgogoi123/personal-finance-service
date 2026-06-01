from fastapi import APIRouter, Depends, Security, status, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Union
from src.auth import controller
from src.utils.db import get_db
from src.auth.schema import CreateUserSchema, UserDataResponse, LoginSchema
from src.auth.models import UsersModel
from src.utils.auth.authentication import is_authenticated

# auth_header = APIKeyHeader(name="X-SECRET", scheme_name="secret-header")
auth_routes = APIRouter(prefix="/auth")

@auth_routes.post("/register", response_model=UserDataResponse, response_model_exclude={"updated_at"}, status_code=status.HTTP_201_CREATED)
def user_registration(body: CreateUserSchema, session: Session = Depends(get_db) ):
  return controller.user_registration(body, session)

@auth_routes.post("/login", status_code=status.HTTP_202_ACCEPTED)
def user_login(body: LoginSchema, session: Session = Depends(get_db)):
  return controller.user_login(body, session)

@auth_routes.post("/renew-access-token", status_code=status.HTTP_200_OK)
def renew_access_token(refresh_token: str, session: Session = Depends(get_db)):
  return controller.renew_access_token(refresh_token, session)

@auth_routes.get(
    "/profile/{id}",
    response_model=UserDataResponse,
    response_model_exclude={"updated_at"},
    status_code=status.HTTP_200_OK
  )
def get_user_profile_by_id(id: int, session=Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return controller.get_user_by_id(id, session)

@auth_routes.put("/update/{id}", response_model=UserDataResponse, status_code=status.HTTP_201_CREATED)
def update_user_by_id(id: int, body: CreateUserSchema, session: Session = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return controller.update_user_by_id(id, body, session)

@auth_routes.delete("/delete/{id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(id: int, session: Session = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return controller.delete_user_by_id(id, session)
