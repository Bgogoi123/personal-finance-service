from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class CreateUserSchema(BaseModel):
  name: str
  phone_number: str
  email: str
  username: str
  password: str
  role_id: int

class UserDataResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
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