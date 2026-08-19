from fastapi import FastAPI
from src.assitance.router import assistance_routes
from src.auth.router import auth_routes
from src.balance.router import balance_routes
from src.categories.router import categories_routes
from src.payment_options.router import payment_options_routes
from src.roles.router import roles_routes
from src.transaction.router import transaction_routes
from src.users.router import user_routes

app = FastAPI()
app.include_router(auth_routes, tags=["Auth"])
app.include_router(roles_routes, tags=["Roles"])
app.include_router(user_routes, tags=["Users"])
app.include_router(balance_routes, tags=["Balance"])
app.include_router(categories_routes, tags=["Categories"])
app.include_router(payment_options_routes, tags=["Payment Options"])
app.include_router(transaction_routes, tags=["Transactions"])
app.include_router(assistance_routes, tags=["AI Assistance"])
