
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal

CATEGORY_COLOR_PALETTE = Literal["#EAE4E9", "#FFF1E6", "#FDE2E4", "#FAD2E1", "#E2ECE9", "#BEE1E6", "#F0EFEB", "#DFE7FD", "#CDDAFD" ]

class CreateCategorySchema(BaseModel):
  name: str
  color: CATEGORY_COLOR_PALETTE = "#EAE4E9"
  user_id: int

class CategoryResponseSchema(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  name: str
  color: CATEGORY_COLOR_PALETTE
  created_at : datetime