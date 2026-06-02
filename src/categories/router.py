from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from src.categories.models import CategoriesModel
from src.categories.schema import CategoryResponseSchema, CreateCategorySchema
from src.categories import controller
from src.auth.models import UsersModel
from src.utils.db import get_db
from src.utils.auth.authentication import is_authenticated

categories_routes = APIRouter(prefix="/categories")

# Create Category
@categories_routes.post(
  "/add",
  response_model=CategoryResponseSchema,
  status_code=status.HTTP_201_CREATED
)
def create_category(
  body: CreateCategorySchema,
  session: Session = Depends(get_db),
  user: UsersModel = Depends(is_authenticated)
):
  return controller.create_category(body, session)

# Fetch All Categories
@categories_routes.get("/", response_model=List[CategoryResponseSchema], status_code=status.HTTP_200_OK)
def get_all_categories(session: Session = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return controller.get_all_categories(session)

# Fetch A Category by ID
@categories_routes.get("/{id}", response_model=CategoryResponseSchema, status_code=status.HTTP_200_OK)
def get_category_by_id(id: int, session = Depends(get_db), user = Depends(is_authenticated)):
  return controller.get_category_by_id(id, session)

# Update A Category by ID
@categories_routes.put("/update/{id}", response_model=CategoryResponseSchema, status_code=status.HTTP_201_CREATED)
def update_category_by_id(id: int, body: CreateCategorySchema, session = Depends(get_db), user = Depends(is_authenticated)):
  return controller.update_category_by_id(id, body, session)

# Delete A Category by ID
@categories_routes.delete("/delete/{id}")
def delete_category_by_id(id: int, session = Depends(get_db), user = Depends(is_authenticated)):
  return controller.delete_category_by_id(id, session)