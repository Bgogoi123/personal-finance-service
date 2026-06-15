from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select
from typing import List
from datetime import datetime
from src.roles.schema import RolesCreateSchema, RolesResponseSchema
from src.roles.models import RolesModel

# Create a role
async def create_role(body: RolesCreateSchema, session: AsyncSession) -> RolesResponseSchema:
  if not body.name.strip() or body.name.strip() == "":
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Role Name.")

  role = RolesModel(name = body.name)

  try:  
    session.add(role) # Moves the object data to the pending state, until the next flush, at which point they will move to the persistent state.
    await session.commit() # Saves the data into db tables.
    await session.refresh(role) # Updates the object with the fresh data that's bin created in the database and fetches the server-generated created_at back into the object.
    return role
  
  except SQLAlchemyError as e:
    await session.rollback()
    print("Error in creating role: ", e)
    raise HTTPException(500, "Something went wrong on the server, please try again later.")

# Get all roles
async def get_all_roles(session: AsyncSession) -> List[RolesResponseSchema]:
  try:
    roles = await session.scalars(select(RolesModel))

    if not roles:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No roles found.")
    
    return roles
  except SQLAlchemyError as err:
    print("Error while fetching all roles :: ", err )
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server. Please try again later.")
  
# Get a role by ID
async def get_roles_by_id(id: str, session: AsyncSession) -> RolesResponseSchema:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Role Id.")

  try:
    role = await session.scalar(select(RolesModel).where(RolesModel.id==id))
    if not role:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    return role
  except SQLAlchemyError as err:
    print("Error while fetching role by id :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server. Please try again later.")

# Update a role by ID
async def update_role_by_id(id: str, body: RolesCreateSchema, session: AsyncSession) -> RolesResponseSchema:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Role ID.")

  try:
    role = await session.scalar(select(RolesModel).where(RolesModel.id == id))
    if not role:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")
    
    update_data = body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    for key, value in update_data.items():
      setattr(role, key, value)

    role.updated_at = datetime.now()

    await session.commit()
    await session.refresh(role)
    return role
  except SQLAlchemyError as e:
    await session.rollback()
    print(f"Error while updating role with ID {id} ::", e)
    raise HTTPException(500, "Something went wrong in the server. Please try again later.")

# Delete a role by ID
async def delete_role_by_id(id: str, session: AsyncSession) -> None:
  if not id:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Role ID.")
  
  try:
    option = await session.scalar(select(RolesModel).where(RolesModel.id == id))

    if not option:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role Not Found.")
    
    await session.delete(option)
    await session.commit()
    return None
  
  except IntegrityError as err:
    await session.rollback()
    print(f"Integrity violation while deleting role {id}: {err}")
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Cannot delete this role because it is currently assigned to one or more users."
    )

  except SQLAlchemyError as err:
    session.rollback()
    print("Error while deleting role :: ", err)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server, please try again later.")
  