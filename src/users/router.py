from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.users import controller
from src.utils.db import get_db
from src.users.schema import CreateUserSchema, UserDataResponse
from src.users.models import UsersModel

user_routes = APIRouter(prefix="/users")

@user_routes.post("/add", response_model=UserDataResponse, response_model_exclude={"updated_at"}, status_code=status.HTTP_201_CREATED)
def create_user(body: CreateUserSchema, session: Session = Depends(get_db) ):
  return controller.create_user(body, session)

@user_routes.get("/{id}", response_model=UserDataResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(id: int, session: Session = Depends(get_db)):
  return controller.get_user_by_id(id, session)

@user_routes.put("/update/{id}", response_model=UserDataResponse, status_code=status.HTTP_201_CREATED)
def update_user_by_id(id: int, body: CreateUserSchema, session: Session = Depends(get_db)):
  return controller.update_user_by_id(id, body, session)

@user_routes.delete("/delete/{id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(id: int, session: Session = Depends(get_db)):
  return controller.delete_user_by_id(id, session)