from typing import Optional
from pydantic import BaseModel, Field


class ExtractedTransactionSchema(BaseModel):
    is_complete: bool = Field(
        description="True only if title, type, amount, category, "
        "and payment method were all found.")
    missing_info_message: Optional[str] = Field(
        default=None, description="A polite clarifying question "
        "listing exactly what's missing. Must be null if is_complete is True")
    title: str
    transaction_type: str = Field(description="'income' or 'expense'")
    amount: float
    category: str
    payment_option: str = Field(
        description="e.g. 'UPI', 'Cash', 'HDFC Credit Card'")
    payment_type: str = Field(
        description="Broad classification of the payment_option, one of: "
        "'Cash', 'Card', 'Digital', 'Bank Transfer', 'Other'"
    )
    note: str


class UserMessageSchema(BaseModel):
    message: str
