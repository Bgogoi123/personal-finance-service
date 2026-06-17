from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone
from src.transaction.schema import TransactionCreateSchema, TransactionUpdateSchema, TransactionResponseSchema
from src.transaction.models import TransactionsModel
from src.auth.models import UsersModel

# create transaction
async def create_transaction(body: TransactionCreateSchema, session: AsyncSession, user: UsersModel) -> TransactionResponseSchema:
  if not body.transaction_title.strip() or body.transaction_title.strip() == "":
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid title provided for the transaction.")

  transaction = TransactionsModel(
    transaction_title=body.transaction_title, 
    transaction_type=body.transaction_type, 
    amount=body.amount, 
    note=body.note, 
    category_id=body.category_id,
    payment_option_id=body.payment_option_id,
    user_id = user.id
  )

  try:
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction
  except SQLAlchemyError as err:
    await session.rollback()
    print("Error in creating transaction :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server, please try again later.")

# get all transactions
async def get_all_transactions(session: AsyncSession, user: UsersModel)-> List[TransactionResponseSchema]:
  try:
    transactions = await session.scalars(select(TransactionsModel).where(TransactionsModel.user_id==user.id))
    if not transactions:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Transactions Found.")
    return transactions
  except SQLAlchemyError as err:
    print("Error while fetching all transactions :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong at the server, please try again later.")

# get transaction by id
async def get_transaction_by_id(id: str, session: AsyncSession, user: UsersModel) -> TransactionResponseSchema:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Transaction ID.")
  
  try:
    transaction = await session.scalar(select(TransactionsModel).where(TransactionsModel.id == id, TransactionsModel.user_id == user.id))
    if not transaction:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction Details Not Found.")
    return transaction  

  except SQLAlchemyError as err:
    print(f"Error while fetching transaction by ID {id} :: {err}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong at the server, please try again later.")

# update transaction by id
async def update_transaction_by_id(id: str, body: TransactionUpdateSchema, session: AsyncSession, user: UsersModel) -> TransactionResponseSchema:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Transaction ID!")
  
  try:
    transaction = await session.scalar(select(TransactionsModel).where(TransactionsModel.id == id, TransactionsModel.user_id == user.id))
    if not transaction: 
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction Not Found!")
    
    update_data = body.model_dump()
    for key, val in update_data.items():
      if val is not None:
        setattr(transaction, key, val)

    transaction.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(transaction)
    return transaction
  
  except SQLAlchemyError as error:
    await session.rollback()
    print(f"Error while updating transaction with id {id} :: {error}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong at the server, please try again later.")

# delete transaction by id
async def delete_transaction_by_id(id: str, session: AsyncSession, user: UsersModel)->TransactionResponseSchema:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Transaction ID!")
  
  try:
    transaction = await session.scalar(select(TransactionsModel).where(TransactionsModel.id == id, TransactionsModel.user_id == user.id))
    if not transaction:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction Not Found!")
    
    await session.delete(transaction)
    await session.commit()
    return None

  except SQLAlchemyError as err:
    await session.rollback()
    print(f"Error while Deleting transaction with ID {id} :: {err}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong at the server, please try again later.")


