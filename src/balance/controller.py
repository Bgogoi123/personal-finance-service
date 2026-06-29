from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.balance.schema import BalanceCreateSchema, BalanceResponseSchema
from src.balance.models import BalanceModel
from src.auth.models import UsersModel

# create balance per each user 
async def create_balance(body: BalanceCreateSchema, session: AsyncSession, user: UsersModel) -> BalanceResponseSchema:
  try:
    # check if balance exist for the current user. if exist, prevent creation.
    existing_balance = await session.scalar(select(BalanceModel).where(BalanceModel.user_id == user.id))
    if existing_balance:
      raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The user have already created a balance.")
    
    balance_name = body.name
    if not body.name:
      user_name = await session.scalar(select(UsersModel.name).where(UsersModel.id == user.id))
      if not user_name:
        balance_name = "Default Balance"
      else:
        balance_name = f"{user_name}'s Balance"

    balance = BalanceModel(name = balance_name, amount = body.amount, user_id = user.id)
    session.add(balance)
    await session.commit()
    await session.refresh(balance)
    return balance

  except IntegrityError as err:
    # This handles Foreign Key failures or Unique Constraint violations
    await session.rollback()
    print(f"Database integrity violation: {err}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Data validation failed at database level."
    )

  except SQLAlchemyError as err:
    # This catches any other generic database issues (connection lost, timeouts)
    await session.rollback()
    print(f"Generic database error: {err}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Something went wrong in the server, please try again later."
    )

# get balance of current user
async def get_current_user_balance(session: AsyncSession, user: UsersModel) -> BalanceResponseSchema:
  try:
    balance = await session.scalar(select(BalanceModel).where(BalanceModel.user_id == user.id))
    if not balance:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User balance record not found. Please create a balance profile.")
    return balance
  
  except SQLAlchemyError as err:
    print(f"Error while fetching balance for id {id} :: {err}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong at the server, please try again later.")

# update balance by id for current user 
async def update_balance_by_id(id: str, body: BalanceCreateSchema, session: AsyncSession, user: UsersModel) -> BalanceResponseSchema:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Balance ID!")
  
  try:
    current_balance = await session.scalar(select(BalanceModel).where(BalanceModel.id == id, BalanceModel.user_id == user.id))
    if not current_balance:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balance Not Found!")
    
    updated_data = body.model_dump()
    for key, value in updated_data.items():
      if value is not None:
        setattr(current_balance, key, value)

    current_balance.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(current_balance)
    return current_balance

  except SQLAlchemyError as error:
    await session.rollback()
    print(f"Error while updating balance with id {id} :: {error}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong at the server, please try again later.")

# delete balance by id for current user
async def delete_balance_by_id(id: str, session: AsyncSession, user: UsersModel) -> dict:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Balance ID.")
  
  try:
    balance = await session.scalar(select(BalanceModel).where(BalanceModel.id==id))
    if not balance:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balance Not Found.")
    
    await session.delete(balance)
    await session.commit()
    return None
    
  except SQLAlchemyError as err:
    await session.rollback()
    print(f"Error while Deleting Balance with ID {id} :: {err}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong at the server, please try again later.")