from sqlalchemy import Column, String, DateTime, func, ForeignKey, UUID
import uuid
from src.utils.db import Base

class PaymentOptionsModel(Base):
  __tablename__ = "payment_options"

  id = Column(
    String,
    primary_key=True,
    default=lambda: str(uuid.uuid4()), # Generates a unique string per row
    nullable=False
  )
  name = Column(String, nullable=False)
  payment_type = Column(String, nullable=False)
  created_at = Column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
  )
  updated_at = Column(
      DateTime(timezone=True),
      nullable=True  # NULL until the role is actually updated
  )
  user_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)