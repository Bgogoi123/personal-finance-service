from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from src.roles import controller
from src.roles.schema import RolesCreateSchema, RolesResponseSchema
from src.auth.models import UsersModel
from src.utils.db import get_db
from src.utils.auth.authentication import is_authenticated

roles_routes = APIRouter(prefix="/roles")

@roles_routes.post(
    "/add",
    response_model=RolesResponseSchema,
    response_model_exclude={"updated_at"},
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    body: RolesCreateSchema, 
    session: Session = Depends(get_db), 
    user: UsersModel = Depends(is_authenticated)
): 
  return controller.create_role(body, session)

@roles_routes.get("/", response_model=List[RolesResponseSchema], status_code=status.HTTP_200_OK )
def get_all_roles(session: Session = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return controller.get_all_roles(session)

@roles_routes.get("/{id}", response_model=RolesResponseSchema, status_code=status.HTTP_200_OK)
def get_roles_by_id(id: int, session: Session = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return controller.get_roles_by_id(id, session)

@roles_routes.put("/update/{id}", response_model=RolesResponseSchema, status_code=status.HTTP_201_CREATED)
def update_role_by_id(id: int, body: RolesCreateSchema, session: Session = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return controller.update_role_by_id(id, body, session)

@roles_routes.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role_by_id(id: int, session: Session = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return controller.delete_role_by_id(id, session)