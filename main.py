from fastapi import FastAPI
from src.roles.router import roles_routes
from src.auth.router import auth_routes
from src.categories.router import categories_routes
from src.payment_options.router import payment_options_routes
from src.transaction.router import transaction_routes

app = FastAPI()
app.include_router(roles_routes, tags=["Roles"])
app.include_router(auth_routes, tags=["Auth"])
app.include_router(categories_routes, tags=["Categories"])
app.include_router(payment_options_routes, tags=["Payment Options"])
app.include_router(transaction_routes, tags=["Transactions"])
