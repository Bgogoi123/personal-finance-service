from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.transaction.schema import TransactionCreateSchema, TransactionUpdateSchema, TransactionResponseSchema
from src.transaction.models import TransactionsModel
from src.auth.models import UsersModel

# create transaction
async def create_transaction(body: TransactionCreateSchema, session: AsyncSession, user: UsersModel) -> TransactionResponseSchema:
  if not body.transaction_title.strip() or body.transaction_title.strip() == "":
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid title provided for the transaction.")

  transaction = TransactionsModel(transaction_title=body.transaction_title, transaction_type=body.transaction_type, amount=body.amount, note=body.note, user_id = user.id)

  print("BODY BEFORE SENDING :: ", body)

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
# get transaction by id
# update transaction by id
# delete transaction by id

# {
#   "title": "Appartment Electric Bill",
#   "transaction_type": "expense",
#   "amount": 2089.18,
#   "category_id": "2d044f3b-6176-4e93-8898-53c179599b91",
#   "payment_option_id": "75c98222-1001-4ace-b3fb-2254423bba96",
# }