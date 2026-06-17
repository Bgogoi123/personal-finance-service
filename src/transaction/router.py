from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.transaction.schema import TransactionCreateSchema, TransactionUpdateSchema, TransactionResponseSchema
from src.transaction import controller
from src.auth.models import UsersModel
from src.utils.db import get_db
from src.utils.auth.authentication import is_authenticated

transaction_routes = APIRouter(prefix="/transactions")

# create transaction
@transaction_routes.post(
  "/add",
  response_model=TransactionResponseSchema,
  status_code=status.HTTP_201_CREATED
)
async def create_transaction(body: TransactionCreateSchema, session: AsyncSession = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return await controller.create_transaction(body, session, user)

# get all transactions
@transaction_routes.get("/", response_model=List[TransactionResponseSchema], status_code=status.HTTP_200_OK)
async def get_all_transactions(session : AsyncSession = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return await controller.get_all_transactions(session, user)

# get transaction by id
@transaction_routes.get("/{id}", response_model=TransactionResponseSchema, status_code=status.HTTP_200_OK)
async def get_transaction_by_id(id: str, session: AsyncSession = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return await controller.get_transaction_by_id(id, session, user)

# update transaction by id
@transaction_routes.put("/update/{id}", response_model=TransactionResponseSchema, status_code=status.HTTP_201_CREATED)
async def update_transaction_by_id(id: str, body: TransactionUpdateSchema, session: AsyncSession = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return await controller.update_transaction_by_id(id, body, session, user)

# delete transaction by id
@transaction_routes.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction_by_id(id: str, session: AsyncSession = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return await controller.delete_transaction_by_id(id, session, user)