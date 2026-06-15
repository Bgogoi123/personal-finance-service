from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class UserCreateSchema(BaseModel):
  name: str
  phone_number: str
  email: str
  username: str
  password: str
  role_id: str

class UserUpdateSchema(BaseModel):
  name: Optional[str] = None
  phone_number: Optional[str] = None
  email: Optional[str] = None
  username: Optional[str] = None
  role_id: Optional[str] = None

class UserResponseSchema(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str
  username: str
  email: str
  phone_number: str
  updated_at: Optional[datetime] = None

class LoginSchema(BaseModel):
  identifier: str = Field(..., description="Can be username, email, or phone number")
  password: str

class LoginResponseSchema(BaseModel):
  access_token: str
  refresh_token: str

class RenewTokenResponseSchema(BaseModel):
  access_token: str