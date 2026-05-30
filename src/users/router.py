from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import Union
from src.users import controller
from src.utils.db import get_db
from src.users.schema import CreateUserSchema, UserDataResponse, LoginSchema
from src.users.models import UsersModel

user_routes = APIRouter(prefix="/user")

@user_routes.post("/register", response_model=UserDataResponse, response_model_exclude={"updated_at"}, status_code=status.HTTP_201_CREATED)
def user_registration(body: CreateUserSchema, session: Session = Depends(get_db) ):
  return controller.user_registration(body, session)

@user_routes.post("/login", status_code=status.HTTP_202_ACCEPTED)
def user_login(body: LoginSchema, session: Session = Depends(get_db)):
  return controller.user_login(body, session)

@user_routes.get("/is_auth", response_model=UserDataResponse, response_model_exclude={"updated_at"}, status_code=status.HTTP_200_OK)
def is_auth(request: Request, session: Session = Depends(get_db)):
  return controller.is_authenticated(request, session)

@user_routes.post("/refresh_token", status_code=status.HTTP_200_OK)
def refresh_token(refresh_token: str, ):
  return None

@user_routes.get("/{id}", response_model=UserDataResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(id: int, session: Session = Depends(get_db)):
  return controller.get_user_by_id(id, session)

@user_routes.put("/update/{id}", response_model=UserDataResponse, status_code=status.HTTP_201_CREATED)
def update_user_by_id(id: int, body: CreateUserSchema, session: Session = Depends(get_db)):
  return controller.update_user_by_id(id, body, session)

@user_routes.delete("/delete/{id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(id: int, session: Session = Depends(get_db)):
  return controller.delete_user_by_id(id, session)
