from sqlalchemy import Column, DateTime, DECIMAL, ForeignKey, func, String
import uuid
from src.utils.db import Base

class BalanceModel(Base):
  __tablename__ = "balance"

  id = Column(
    String, 
    primary_key=True, 
    default=lambda: str(uuid.uuid4()),
    nullable=False
  )
  name = Column(String, nullable=False)
  amount = Column(DECIMAL(10,2), nullable=False)
  created_at = Column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
  )
  updated_at = Column(DateTime(timezone=True), nullable=True)
  user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)