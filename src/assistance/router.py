from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.auth.models import UsersModel
from src.utils.db import get_db
from src.utils.auth.authentication import allow_all
from src.assistance.transaction_entry.schema import UserMessageSchema
from src.assistance.transaction_entry.graph import assistance_graph
from src.assistance.summary_narrator.schema import (
    AggregatedDataSchema,
    SummaryGeneratorPayloadSchema,
    SummaryNarrationSchema,
    SummaryResponseSchema
)
from src.assistance.summary_narrator.chain import data_aggregation, data_formatter, summary_chain


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


@assistance_routes.post(
    "/generate-summary",
    response_model=SummaryResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def generate_monthly_summary(
    payload: SummaryGeneratorPayloadSchema,
    session: AsyncSession = Depends(get_db),
    user: UsersModel = Depends(allow_all)
):

    current_date = payload.date or datetime.now(timezone.utc())
    current_month = current_date.strftime("%B")
    current_year = str(current_date.year)

    aggregated_data: AggregatedDataSchema = await data_aggregation(
        session=session,
        user=user,
        target_date=current_date
    )
    formatted_data = data_formatter(
        aggregated_data=aggregated_data,
        month=current_month, year=current_year
    )

    narration: SummaryNarrationSchema = await summary_chain.ainvoke(formatted_data)

    return {
        "aggregated_data": aggregated_data,
        "narration": narration
    }

    # return await generate_summary(session=session, user=user, date=payload.date)
