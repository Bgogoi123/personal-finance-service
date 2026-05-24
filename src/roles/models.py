from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, func
from src.utils.db import Base

class RolesModel(Base):
  __tablename__ = "roles"

  id = Column(Integer, primary_key=True, autoincrement=True)
  role_name = Column(String, nullable=False, unique=True)
  created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # DB generates the value on INSERT
        nullable=False
    )
  updated_at = Column(
        DateTime(timezone=True),
        nullable=True  # NULL until the role is actually updated
    )