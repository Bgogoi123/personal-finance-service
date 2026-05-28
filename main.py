from fastapi import FastAPI
from src.utils.db import Base, engine
from src.roles.router import roles_routes
from src.users.router import user_routes

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(roles_routes, tags=["Roles"])
app.include_router(user_routes, tags=["Users"])