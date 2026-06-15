from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List 
from src.categories.schema import CategoryResponseSchema, CategoryCreateSchema, CategoryUpdateSchema
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
async def create_category(
  body: CategoryCreateSchema,
  session: AsyncSession = Depends(get_db),
  user: UsersModel = Depends(is_authenticated)
):
  return await controller.create_category(body, session, user)

# Fetch All Categories
@categories_routes.get("/", response_model=List[CategoryResponseSchema], status_code=status.HTTP_200_OK)
async def get_all_categories(session: AsyncSession = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return await controller.get_all_categories(session, user)

# Fetch A Category by ID
@categories_routes.get("/{id}", response_model=CategoryResponseSchema, status_code=status.HTTP_200_OK)
async def get_category_by_id(id: str, session: AsyncSession = Depends(get_db), user: UsersModel = Depends(is_authenticated)):
  return await controller.get_category_by_id(id, session, user)

# Update A Category by ID
@categories_routes.put("/update/{id}", response_model=CategoryUpdateSchema, status_code=status.HTTP_201_CREATED)
async def update_category_by_id(id: str, body: CategoryUpdateSchema, session: AsyncSession = Depends(get_db), user = Depends(is_authenticated)):
  return await controller.update_category_by_id(id, body, session, user)

# Delete A Category by ID
@categories_routes.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_by_id(id: str, session: AsyncSession = Depends(get_db), user = Depends(is_authenticated)):
  return await controller.delete_category_by_id(id, session, user)