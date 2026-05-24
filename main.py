from fastapi import FastAPI
from src.utils.db import Base, engine
from src.roles.router import roles_routes

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(roles_routes)