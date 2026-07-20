from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
import uuid
from src.utils.db import Base

class UsersModel(Base):
  __tablename__ = "users"

  id = Column(
    String,
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
    nullable=False
  )
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
  role_id = Column(String, ForeignKey("roles.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)

class RefreshTokensModel(Base):
  __tablename__ = "refresh_tokens"

  id = Column(
    String,
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
    nullable=False
  )
  token = Column(String, unique=True, nullable=False, index=True)
  expires_at = Column(DateTime(timezone=True), nullable=False)
  device_info = Column(JSON, nullable=True)
  user_id = Column(ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)