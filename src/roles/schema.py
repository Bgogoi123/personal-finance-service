from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# not sending created_at and updated_at from client to backend.
class RolesCreateSchema(BaseModel):
  role_name: str

class RolesResponseSchema(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  role_name: str
  created_at : datetime
  updated_at: Optional[datetime] = None
