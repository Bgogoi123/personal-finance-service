from sqlalchemy import Column, DateTime, DECIMAL, Float, ForeignKey, func, Integer, String
import uuid
from src.utils.db import Base

class TransactionsModel(Base):
  __tablename__ = "transactions"

  id = Column(
    String, 
    primary_key=True, 
    default=lambda: str(uuid.uuid4()),
    nullable=False
  )
  transaction_title = Column(String, nullable=False)
  transaction_type = Column(String, nullable=False)
  amount = Column(DECIMAL(10,2), nullable=False)
  note = Column(String, nullable=True)
  created_at = Column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
  )
  updated_at = Column(DateTime(timezone=True), nullable=True)
  category_id = Column(String, ForeignKey("categories.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
  user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
  payment_option_id = Column(String, ForeignKey("payment_options.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
