from pydantic import BaseModel, ConfigDict
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