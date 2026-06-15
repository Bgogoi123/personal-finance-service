from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal, Optional

CATEGORY_COLOR_PALETTE = Literal["#EAE4E9", "#FFF1E6", "#FDE2E4", "#FAD2E1", "#E2ECE9", "#BEE1E6", "#F0EFEB", "#DFE7FD", "#CDDAFD" ]

class CategoryCreateSchema(BaseModel):
  name: str
  color: CATEGORY_COLOR_PALETTE = "#EAE4E9"

class CategoryUpdateSchema(BaseModel):
  name: Optional[str] = None
  color: Optional[CATEGORY_COLOR_PALETTE] = None

class CategoryResponseSchema(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str
  color: CATEGORY_COLOR_PALETTE
  created_at : datetime