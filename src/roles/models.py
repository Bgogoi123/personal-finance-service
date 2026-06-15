from sqlalchemy import Column, Integer, String, DateTime, func
from src.utils.db import Base
import uuid

class RolesModel(Base):
  __tablename__ = "roles"

  id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
  name = Column(String, nullable=False, unique=True)
  created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # DB generates the value on INSERT
        nullable=False
    )
  updated_at = Column(
        DateTime(timezone=True),
        nullable=True  # NULL until the role is actually updated
    )