from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from src.payment_options.models import PaymentOptionsModel
from src.payment_options.schema import PaymentOptionsResponseSchema, PaymentOptionsCreateSchema, PaymentOptionsUpdateSchema
from src.auth.models import UsersModel

# create payment option
async def create_payment_option(body: PaymentOptionsCreateSchema, session: AsyncSession, user: UsersModel ) -> PaymentOptionsResponseSchema:
  if not body.name.strip() or body.name.strip() == "":
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Category Name.")

  payment_option = PaymentOptionsModel(
    name = body.name,
    payment_type = body.payment_type,
    user_id = user.id
  )

  try:
    session.add(payment_option)
    await session.commit()
    await session.refresh(payment_option)
    return payment_option
  except SQLAlchemyError as err:
    await session.rollback()
    print("Error while Creating Payment Option :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")

# get all payment options
async def get_all_payment_options(session: AsyncSession, user: UsersModel) -> List[PaymentOptionsResponseSchema] :
  try: 
    stmt = select(PaymentOptionsModel).where(PaymentOptionsModel.user_id == user.id)
    options = await session.scalars(stmt)

    if not options:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, 
          detail=f"No Payment Options Found."
      )
    return options
  
  except SQLAlchemyError as err:
    print("Error while fetching all categories :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server. Please try again later.")

# get payment option by id
async def get_payment_option_by_id(
  id: str,
  session: AsyncSession,
  user: UsersModel
) -> PaymentOptionsModel:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Option Id.")
  
  try:
    stmt = select(PaymentOptionsModel).where(PaymentOptionsModel.id == id, PaymentOptionsModel.user_id == user.id)
    option = await session.scalar(stmt)

    if not option:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, 
          detail=f"Option Not Found."
      )
    return option

  except SQLAlchemyError as err:
    print("Error while fetching category by id :: ", err)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong in the server. Please try again later.")

# update payment option by id
async def update_payment_option_by_id(
  id: str,
  body: PaymentOptionsUpdateSchema,
  session: AsyncSession,
  user: UsersModel
) -> PaymentOptionsResponseSchema :
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Option ID.")
  
  try:
    stmt = select(PaymentOptionsModel).where(PaymentOptionsModel.id == id, PaymentOptionsModel.user_id == user.id)
    option = await session.scalar(stmt)

    if not option:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found.")

    if body.name is not None : option.name = body.name
    if body.payment_type is not None : option.payment_type = body.payment_type

    if hasattr(option, "updated_at"):
      option.updated_at = datetime.now()

    await session.commit()
    await session.refresh(option)
    return option
  except SQLAlchemyError as err:
    await session.rollback()
    print("Error while Updating Payment Option :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")

# delete payment option by id
async def delete_payment_option_by_id(id: str, session: AsyncSession, user: UsersModel) -> dict:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Option ID.")
  
  try:
    stmt = select(PaymentOptionsModel).where(PaymentOptionsModel.id == id, PaymentOptionsModel.user_id == user.id)
    option = await session.scalar(stmt)

    if not option:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment Option Not Found.")
    
    await session.delete(option)
    await session.commit()
    return None
  
  except SQLAlchemyError as err:
    await session.rollback()
    print("Error while deleting payment option :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server, please try again later.")
  