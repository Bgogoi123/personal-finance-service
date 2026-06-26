from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from src.roles import controller
from src.roles.schema import RolesCreateSchema, RolesResponseSchema
from src.auth.models import UsersModel
from src.utils.db import get_db
from src.utils.auth.authentication import is_authenticated

roles_routes = APIRouter(prefix="/roles")
session_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[UsersModel, Depends(is_authenticated)]

# [[Hide]] Create role
@roles_routes.post(
    "/add",
    response_model=RolesResponseSchema,
    response_model_exclude={"updated_at"},
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    body: RolesCreateSchema, 
    session: session_dependency, 
    user: user_dependency
): 
  return await controller.create_role(body, session)

#  Get all roles
@roles_routes.get("/", response_model=List[RolesResponseSchema], status_code=status.HTTP_200_OK )
async def get_all_roles(session: session_dependency, user: user_dependency):
  return await controller.get_all_roles(session)

# [[Hide]] Get role by id
@roles_routes.get("/{id}", response_model=RolesResponseSchema, status_code=status.HTTP_200_OK)
async def get_roles_by_id(id: str, session: session_dependency, user: user_dependency):
  return await controller.get_roles_by_id(id, session)

# [[Hide]] Update role by id
@roles_routes.put("/update/{id}", response_model=RolesResponseSchema, status_code=status.HTTP_201_CREATED)
async def update_role_by_id(id: str, body: RolesCreateSchema, session: session_dependency, user: user_dependency):
  return await controller.update_role_by_id(id, body, session)

# [[Hide]] Delete role by id
@roles_routes.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_by_id(id: str, session: session_dependency, user: user_dependency):
  return await controller.delete_role_by_id(id, session)