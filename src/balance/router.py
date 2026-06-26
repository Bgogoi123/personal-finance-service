from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from src.utils.db import get_db
from src.utils.auth.authentication import is_authenticated
from src.auth.models import UsersModel
from src.balance.models import BalanceModel
from src.balance.schema import BalanceCreateSchema, BalanceResponseSchema
from src.balance import controller

balance_routes = APIRouter(prefix="/balance")
session_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[UsersModel, Depends(is_authenticated)]

# create balance per each user
@balance_routes.post("/add", response_model=BalanceResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_balance(body: BalanceCreateSchema, session: session_dependency, user: user_dependency):
  return await controller.create_balance(body, session, user)

# get balance by id for current user
@balance_routes.get("/{id}", response_model=BalanceResponseSchema, status_code=status.HTTP_200_OK)
async def get_balance_by_id(id: str, body: BalanceCreateSchema, session: session_dependency, user: user_dependency ):
  return await controller.get_balance_by_id(id, body, session, user)

# update balance by id for current user
@balance_routes.put("/update/{id}", response_model=BalanceResponseSchema, status_code=status.HTTP_201_CREATED)
async def update_balance_by_id(id: str, body: BalanceCreateSchema,  session: session_dependency, user: user_dependency ):
  return await controller.update_balance_by_id(id, body, session, user)

# delete balance by id for current user
@balance_routes.delete("/delete/{id}")
async def delete_balance_by_id(id: str, session: session_dependency, user: user_dependency ):
  return await controller.delete_balance_by_id(id, session, user)