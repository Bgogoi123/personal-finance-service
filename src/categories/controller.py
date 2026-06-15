from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from typing import List
from src.auth.models import UsersModel
from src.categories.schema import CategoryCreateSchema, CategoryResponseSchema, CategoryUpdateSchema
from src.categories.models import CategoriesModel

# Create a Category
async def create_category(body: CategoryCreateSchema, session: AsyncSession, user: UsersModel) -> CategoryResponseSchema:
  if not body.name.strip() or body.name.strip() == "":
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Category Name.")

  category = CategoriesModel(name = body.name, color = body.color, user_id = user.id)

  try:
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category
  except SQLAlchemyError as err:
    await session.rollback()
    print("Error while Creating Category :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")
  
# Fetch All Categories
async def get_all_categories(session: AsyncSession, user: UsersModel) -> List[CategoryResponseSchema]:
  try: 
    categories = await session.scalars(select(CategoriesModel).where(CategoriesModel.user_id == user.id))

    if not categories:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, 
          detail="Couldn't fetch categories."
      )
    
    return categories
      
  except SQLAlchemyError as err:
    print("Error while fetching all categories :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server. Please try again later.")
  
# Fetch A Category by ID
async def get_category_by_id(id: str, session: AsyncSession, user: UsersModel) -> CategoryResponseSchema:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Category Id.")
  
  try:
    stmt = select(CategoriesModel).where(CategoriesModel.id == id, CategoriesModel.user_id == user.id)
    category = await session.scalar(stmt)

    if not category:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, 
          detail="Category Not Found."
      )
    return category
  
  except SQLAlchemyError as err:
    print("Error while fetching category by id :: ", err)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong in the server. Please try again later.")

# Update A Category by ID
async def update_category_by_id(id: str, body: CategoryUpdateSchema, session: AsyncSession, user: UsersModel) -> CategoryResponseSchema:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Category ID.")

  try: 
    stmt = select(CategoriesModel).where(CategoriesModel.id == id, CategoriesModel.user_id == user.id)
    category = await session.scalar(stmt)

    if not category:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    
    update_data = body.model_dump(exclude_unset=True) # ensures we only loop through fields provided in the request body

    # Security Guard: Prevent altering ownership or ID during an update.
    update_data.pop("id", None)
    update_data.pop("user_id", None)

    if body.name is not None : category.name = body.name
    if body.color is not None : category.color = body.color

    print("UPDATING CATAGORY ::: ", category.name, category.color)
    

    # for key, value in update_data.items():
    #   setattr(category, key, value)

    await session.commit()
    await session.refresh(category)
    return category
  except SQLAlchemyError as er:
    await session.rollback() # Reverts DB state so the session isn't poisoned.
    print("Error while Updating Category :: ", er)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")
    
# Delete A Category by ID
async def delete_category_by_id(id: str, session: AsyncSession, user: UsersModel) -> dict:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Category ID.")
  
  try:
    stmt = select(CategoriesModel).where(CategoriesModel.id == id, CategoriesModel.user_id == user.id)
    category = await session.scalar(stmt)

    if not category:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    
    await session.delete(category)
    await session.commit()
    return None
  
  except SQLAlchemyError as error:
    await session.rollback()
    print("Error while deleting category :: ", error )
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")
  