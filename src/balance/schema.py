from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from typing import Optional

class BalanceCreateSchema(BaseModel):
  name: Optional[str] = None
  amount: Decimal = Decimal("0.00")

class BalanceResponseSchema(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str # Send a default name from backend (if no name provided while creating), like "Iseop's Balance"
  amount: Decimal
  created_at: datetime
  updated_at: datetime | None = None
