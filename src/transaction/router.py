from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
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
# get transaction by id
# update transaction by id
# delete transaction by id