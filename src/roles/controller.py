from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from src.roles.schema import RolesCreateSchema, RolesResponseSchema
from src.roles.models import RolesModel

# Create a role
def create_role(body: RolesCreateSchema, session: Session) -> RolesResponseSchema | HTTPException:
  data = body.model_dump()

  # create an object of the RolesModel class, and pass this object to postgreSQL Database.
  role = RolesModel(role_name = data["role_name"])

  try:
    session.add(role) # Moves the object data to the pending state, until the next flush, at which point they will move to the persistent state.
    session.commit() # Saves the data into db tables.
    session.refresh(role) # Updates the object with the fresh data that's bin created in the database and fetches the server-generated created_at back into the object.

    return RolesResponseSchema.model_validate(role)
  except SQLAlchemyError as e:
    print("Error in creating role: ", e)
    raise HTTPException(500, "Something went wrong on the server, please try again later.")

# Get all roles
def get_all_roles(session: Session) -> List[RolesResponseSchema] | HTTPException :
  try:
    roles = session.query(RolesModel).all()
    return roles
  except SQLAlchemyError as err:
    print("Error while fetching all roles :: ", err )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No rules found.")
  
# Get a role by ID
def get_roles_by_id(id: int, session: Session) -> RolesResponseSchema | HTTPException:
  try:
    role = session.query(RolesModel).get(id)
    return role
  except SQLAlchemyError as err:
    print("Error while fetching role by id :: ", err)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {id} not found.")

# Update a role by ID
def update_role_by_id(id: int, body: RolesCreateSchema, session: Session) -> RolesResponseSchema | HTTPException:
  data = body.model_dump()
  role = session.query(RolesModel).filter(RolesModel.id==id).first()

  if(role):
    for key, value in data.items():
      setattr(role, key, value)
    
    setattr(role, "updated_at", datetime.now())

    try:
      session.commit()
      session.refresh(role)
      return RolesResponseSchema.model_validate(role)
    except SQLAlchemyError as e:
      print(f"Error while updating role with ID {id} ::", e)
      raise HTTPException(500, "Something went wrong in the server. Please try again later.")
  
  raise HTTPException(404, f"Role with ID {id} not found.")

# Delete a role by ID
def delete_role_by_id(id: int, session: Session) -> None | HTTPException:
  role = session.query(RolesModel).filter(RolesModel.id == id).first()

  if(role):
    session.delete(role)
    session.commit()

    return None
  
  raise HTTPException(404, f"Role with ID {id} Not Found.")