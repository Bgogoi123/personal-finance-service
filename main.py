from fastapi import FastAPI
from src.utils.db import Base, engine
from src.roles.router import roles_routes
from src.auth.router import auth_routes
from src.categories.router import categories_routes

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(roles_routes, tags=["Roles"])
app.include_router(auth_routes, tags=["Auth"])
app.include_router(categories_routes, tags=["Categories"])
