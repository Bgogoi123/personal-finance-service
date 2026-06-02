from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from src.categories.schema import CreateCategorySchema, CategoryResponseSchema
from src.categories.models import CategoriesModel

# Create a Category
def create_category(body: CreateCategorySchema, session: Session) -> CategoryResponseSchema | HTTPException:
  category = CategoriesModel(name = body.name, user_id = body.user_id)

  if not body.name.strip() or body.name.strip() == "":
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Category Name.")

  if(body.color):
    setattr(category, "color", body.color)

  try:
    session.add(category)
    session.commit()
    session.refresh(category)

    return CategoryResponseSchema.model_validate(category)
  except SQLAlchemyError as err:
    print("Error while Creating Category :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")
  
# Fetch All Categories
def get_all_categories(session: Session) -> List[CategoryResponseSchema] | HTTPException :
  try: 
    categories = session.query(CategoriesModel).all()
    return categories
  except SQLAlchemyError as error:
    print("Error while fetching all categories :: ", error)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No categories found.")
  
# Fetch A Category by ID
def get_category_by_id(id: int, session: Session) -> CategoryResponseSchema | HTTPException :
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid User Id.")

  try:
    category = session.query(CategoriesModel).get(id)
    return category
  except SQLAlchemyError as err:
    print("Error while fetching category by id :: ", err)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID {id} not found.")

# Update A Category by ID
def update_category_by_id(id: int, body: CreateCategorySchema, session: Session) -> CategoryResponseSchema | HTTPException :
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Category ID.")
  
  category = session.query(CategoriesModel).filter(CategoriesModel.id==id).first()

  if not category:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

  for key, value in body.model_dump().items():
    setattr(category, key, value)

  try: 
    session.commit()
    session.refresh(category)
    return CategoryResponseSchema.model_validate(category)
  except SQLAlchemyError as er:
    print("Error while Updating Category :: ", er)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")
    
# Delete A Category by ID
def delete_category_by_id(id: int, session: Session) -> None | HTTPException :
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Category ID.")

  try:
    category = session.query(CategoriesModel).filter(CategoriesModel.id == id).first()

    if category:
      try:
        session.delete(category)
        session.commit()
        return None
      except SQLAlchemyError as error:
        print("Error while deleting category :: ", error )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")
  except SQLAlchemyError as err: 
    print("Error while fetching category to delete :: ", err)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")





  if(role):
    session.delete(role)
    session.commit()

    return None
  
  raise HTTPException(404, f"Role with ID {id} Not Found.") 