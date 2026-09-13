from pydantic import BaseModel
from datetime import datetime

from src.transaction.schema import TRANSACTION_TYPE


class SummaryGeneratorPayloadSchema(BaseModel):
    date: datetime | None = None


class MetricsSchema(BaseModel):
    total_income: float
    total_expense: float


class CategoryExpensesSchema(BaseModel):
    category_name: str
    total_spent: float
    transaction_count: int


class TopLargestTransactionSchema(BaseModel):
    category_name: str
    note: str
    transaction_type: TRANSACTION_TYPE
    amount: float
    payment_mode: str
    date: datetime


class PaymentModeExpensesSchema(BaseModel):
    category_name: str
    payment_mode: str
    amount: float
    date: datetime


class AggregatedDataSchema(BaseModel):
    metrics: MetricsSchema
    category_expenses: list[CategoryExpensesSchema]
    top_largest_transactions: list[TopLargestTransactionSchema]
    expenses_by_payment_mode: list[PaymentModeExpensesSchema]


class SummaryNarrationSchema(BaseModel):
    headline: str
    summary: str
    top_insight: str


class SummaryResponseSchema(BaseModel):
    aggregated_data: AggregatedDataSchema
    narration: SummaryNarrationSchema
