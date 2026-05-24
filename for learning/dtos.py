from pydantic import BaseModel

#  DTO --> Data Transfer Object (Data Validation)

class ProductDTO(BaseModel):
  id: int
  title: str
  price: int = 0 #Optional (if no value sent, default 0 value will be set)
  count: int = 0 #Optional (if no value sent, default 0 value will be set)