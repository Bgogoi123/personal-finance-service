from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from src.utils.db import Base

class UsersModel(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False)
  email = Column(String, nullable=False, unique=True)
  phone_number = Column(String, nullable=False, unique=True)
  username = Column(String, nullable=False, unique=True)
  password = Column(String, nullable=False, unique=True)
  created_at = Column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
  )
  updated_at = Column(
      DateTime(timezone=True),
      nullable=True  # NULL until the role is actually updated
  )
  role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)