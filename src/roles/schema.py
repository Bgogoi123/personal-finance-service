from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

ROLE_TYPE = Literal["default", "admin"]

# not sending created_at and updated_at from client to backend.
class RolesCreateSchema(BaseModel):
  name: str
  type: ROLE_TYPE = "default"

class RolesResponseSchema(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str
  type: str
  created_at : datetime
  updated_at: Optional[datetime] = None
