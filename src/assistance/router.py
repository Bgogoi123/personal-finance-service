from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import UsersModel
from src.utils.db import get_db
from src.utils.auth.authentication import allow_all

# Imports for Transaction Assistant
from src.assistance.transaction_entry.schema import UserMessageSchema
from src.assistance.transaction_entry.graph import assistance_graph

# Imports for Summary Generator
# from src.assistance.summary_narrator.schema import SummaryGeneratorPayloadSchema


assistance_routes = APIRouter(prefix="/assistance")


@assistance_routes.post("/transaction-entry", status_code=status.HTTP_201_CREATED)
async def run_transaction_assistance(
    payload: UserMessageSchema,
    session: AsyncSession = Depends(get_db),
    user: UsersModel = Depends(allow_all)
):
    config = {"configurable": {
              "thread_id": str(user.id),
              "session": session,
              "user": user
              }
              }

    result = await assistance_graph.ainvoke(
        {"user_input": payload.message}, config=config)

    return {"response": result["final_response"]}


# @assistance_routes.post("/generate-summary", status_code=status.HTTP_201_CREATED)
# async def generate_monthly_summary(payload: SummaryGeneratorPayloadSchema):
#     month = payload.date.month
#     year = payload.date.year
#     date = payload.date.date()
#     print(month, year, date)

#     return None


# -- Total Income
# select sum(amount) as total_income from transactions where type = 'income';

# -- Total Expense
# select sum(amount) as total_expense from transactions where type = 'expense';


# -- Top 5 Largest Transactions
# select category_id, type, amount as top_five_transactions
# from transactions group by category_id order by
# top_five_transactions DESC Limit 5;


# -- Net Balance Change For each date
# WITH signed_transactions AS (
#     SELECT
#         date,
#         CASE
#             WHEN type = 'income' THEN amount
#             WHEN type = 'expense' THEN -amount
#             ELSE 0
#         END AS net_amount
#     FROM
#         transactions
# )
# SELECT
#     date,
#     net_amount,
#     SUM(net_amount) OVER (ORDER BY date) AS running_net_balance
# FROM
#     signed_transactions;
