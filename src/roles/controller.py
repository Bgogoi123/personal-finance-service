from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from src.roles.schema import RolesCreateSchema, RolesResponseSchema
from src.roles.models import RolesModel

def create_role(body: RolesCreateSchema, db: Session) -> RolesResponseSchema:
  data = body.model_dump()

  # create an object of the RolesModel class, and pass this object to postgreSQL Database.
  role = RolesModel(role_name = data["role_name"])

  db.add(role) # Moves the object data to the pending state, until the next flush, at which point they will move to the persistent state.
  db.commit() # Saves the data into db tables.
  db.refresh(role) # Updates the object with the fresh data that's bin created in the database and fetches the server-generated created_at back into the object.

  return {
    "status": 200, "data": RolesResponseSchema.model_validate(role), "message": "Role created."
  }

def get_roles(db: Session):
  roles = db.query(RolesModel).all()

  return {
    "status": 200, "data": roles, "message": "Roles fetched."
  }
  
def get_roles_by_id(id: int, db: Session):
  role = db.query(RolesModel).get(id)

  if not(role):
    raise HTTPException(404, f"Role with ID {id} not found.")

  return {
    "status": 200, "data": role, "message": f"Role details for ID {id}."
  }

def update_role_by_id(id: int, body: RolesCreateSchema, db: Session) -> RolesResponseSchema:
  data = body.model_dump()
  role = db.query(RolesModel).filter(RolesModel.id==id).first()

  if(role):
    for key, value in data.items():
      setattr(role, key, value)
    setattr(role, "updated_at", datetime.now())
    
    db.commit()
    db.refresh(role)
  
  return {
    "status": 200, 
    "data": RolesResponseSchema.model_validate(role),
    "message": f"Role with ID {id} was updated successfully."
  }


