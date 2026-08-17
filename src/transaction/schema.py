from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Literal, Optional

TRANSACTION_TYPE = Literal["income", "expense"]


class TransactionCreateSchema(BaseModel):
    title: str
    type: TRANSACTION_TYPE = "expense"
    amount: Decimal = Decimal("0.00")
    note: str = None
    category_id: str
    payment_option_id: str


class TransactionUpdateSchema(BaseModel):
    title: Optional[str] = None
    type: Optional[TRANSACTION_TYPE] = None
    amount: Optional[Decimal] = None
    note: Optional[str] = None
    category_id: Optional[str] = None
    payment_option_id: Optional[str] = None


class TransactionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    type: TRANSACTION_TYPE
    amount: Decimal
    note: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
