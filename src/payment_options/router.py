from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from src.utils.db import get_db
from src.utils.auth.authentication import is_authenticated
from src.auth.models import UsersModel
from src.payment_options.schema import PaymentOptionsCreateSchema, PaymentOptionsResponseSchema, PaymentOptionsUpdateSchema
from src.payment_options import controller

payment_options_routes = APIRouter(prefix="/payment_options")
session_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[UsersModel, Depends(is_authenticated)]

# create payment option
@payment_options_routes.post(
    "/add",
    response_model=PaymentOptionsResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_payment_option(
  body: PaymentOptionsCreateSchema,
  session: session_dependency,
  user: user_dependency
):
  return await controller.create_payment_option(body, session, user)

# get all payment options
@payment_options_routes.get(
    "/",
    response_model=List[PaymentOptionsResponseSchema],
    status_code=status.HTTP_200_OK
  )
async def get_all_payment_options(
  session: session_dependency,
  user:user_dependency
):
  return await controller.get_all_payment_options(session, user)

# get payment option by id
@payment_options_routes.get("/{id}", response_model=PaymentOptionsResponseSchema, status_code=status.HTTP_200_OK)
async def get_payment_option_by_id(
  id: str,
  session: session_dependency,
  user: user_dependency
):
  return await controller.get_payment_option_by_id(id, session, user)

# update payment option by id
@payment_options_routes.put("/update/{id}")
async def update_payment_option_by_id(
  id: str,
  body: PaymentOptionsUpdateSchema,
  session: session_dependency,
  user: user_dependency
):
  return await controller.update_payment_option_by_id(id, body, session, user)

# delete payment option by id
@payment_options_routes.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_option_by_id(id: str, session: session_dependency, user: user_dependency):
  return await controller.delete_payment_option_by_id(id, session, user)
