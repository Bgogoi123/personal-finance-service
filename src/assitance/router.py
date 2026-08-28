from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.assitance.schema import UserMessageSchema
from src.assitance.graph import assistance_graph
from src.auth.models import UsersModel
from src.utils.db import get_db
from src.utils.auth.authentication import allow_all


assistance_routes = APIRouter(prefix="/assistance")


@assistance_routes.post("/transaction-entry", status_code=status.HTTP_201_CREATED)
async def run_transaction_assistance(payload: UserMessageSchema, session: AsyncSession = Depends(get_db), user: UsersModel = Depends(allow_all)):
    config = {"configurable": {
              "thread_id": str(user.id),
              "session": session,
              "user": user
              }
              }

    result = await assistance_graph.ainvoke(
        {"user_input": payload.message}, config=config)

    print(f"MESSSS::: : {result["final_response"]}")
    return {"response": result["final_response"]}
