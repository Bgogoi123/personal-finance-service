from fastapi import APIRouter, Depends
from src.roles import controller
from src.roles.schema import RolesCreateSchema
from src.utils.db import get_db

roles_routes = APIRouter(prefix="/roles")

@roles_routes.post("/add")
def create_role(body: RolesCreateSchema, db = Depends(get_db)): 
  # Here, "db" is a parameter that "Depends On" the result of "get_db" function.
  # The "Depends" function is likely used for handling dependencies and obtaining values dynamically.

  return controller.create_role(body, db)

@roles_routes.get("/")
def get_roles(db = Depends(get_db)):
  return controller.get_roles(db)

@roles_routes.get("/{id}")
def get_roles_by_id(id: int, db = Depends(get_db)):
  return controller.get_roles_by_id(id, db)

@roles_routes.put("/update/{id}")
def update_role_by_id(id: int, body: RolesCreateSchema, db = Depends(get_db)):
  return controller.update_role_by_id(id, body, db)