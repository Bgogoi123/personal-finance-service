from sqlalchemy import Column, String, DateTime, func, ForeignKey
import uuid
from src.utils.db import Base

class CategoriesModel(Base):
  __tablename__ = "categories"

  id = Column(
    String,
    primary_key=True,
    default=lambda: str(uuid.uuid4()), # Generates a unique string per row
    nullable=False
  )
  name = Column(String, nullable=False)
  color = Column(String, nullable=False) # EAE4E9
  created_at = Column(
      DateTime(timezone=True),
      server_default=func.now(),  # DB generates the value on INSERT
      nullable=False
  )
  user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)