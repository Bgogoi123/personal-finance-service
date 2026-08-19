from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional
from datetime import datetime

PAYMENT_TYPE = Literal["Cash", "Credit Card",
                       "Debit Card", "Mobile Banking App", "Other", "UPI"]


class PaymentOptionsCreateSchema(BaseModel):
    name: str
    payment_type: str = "Cash"


class PaymentOptionsUpdateSchema(BaseModel):
    name: Optional[str] = None
    payment_type: Optional[str] = None


class PaymentOptionsResponseSchema(BaseModel):
    # This configuration tells Pydantic to read data using object attributes (e.g., obj.id)
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    payment_type: str
    created_at: datetime
    updated_at: datetime | None = None
