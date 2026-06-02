from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from src.utils.db import Base

class CategoriesModel(Base):
  __tablename__ = "categories"

  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False)
  color = Column(String, nullable=False) # EAE4E9
  created_at = Column(
      DateTime(timezone=True),
      server_default=func.now(),  # DB generates the value on INSERT
      nullable=False
  )
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)