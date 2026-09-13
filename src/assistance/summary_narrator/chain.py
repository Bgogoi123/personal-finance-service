from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.assistance.llm.groq import create_groq_llm_instance
from src.categories import CategoriesModel
from src.payment_options import PaymentOptionsModel
from src.transaction import TransactionsModel
from src.auth import UsersModel
from src.assistance.summary_narrator.schema import (
    AggregatedDataSchema, CategoryExpensesSchema, MetricsSchema,
    PaymentModeExpensesSchema, SummaryNarrationSchema, TopLargestTransactionSchema
)
from src.assistance.prompts import SUMMARY_NARRATOR_PROMPT

summary_llm = create_groq_llm_instance(temperature=0.2)
structured_llm = summary_llm.with_structured_output(SummaryNarrationSchema, method="json_mode")


async def data_aggregation(session: AsyncSession, user: UsersModel, target_date: datetime | None):
    # calculate date
    year = target_date.year
    month = target_date.month
    start_of_month = datetime(year, month, 1, 0, 0, 0, tzinfo=target_date.tzinfo)

    if month == 12:
        end_of_month = datetime(year+1, 1, 1, 0, 0, 0, tzinfo=target_date.tzinfo)
    else:
        end_of_month = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=target_date.tzinfo)

    try:

        # TOTAL INCOME
        income_stmt = await session.scalar(
            select(func.sum(TransactionsModel.amount))
            .where(
                TransactionsModel.user_id == user.id,
                TransactionsModel.type == "income",
                TransactionsModel.created_at >= start_of_month,
                TransactionsModel.created_at < end_of_month
            )
        )

        total_income = float(income_stmt) if income_stmt else 0.0

        # TOTAL EXPENSE
        expense_stmt = await session.scalar(
            select(func.sum(TransactionsModel.amount))
            .where(
                TransactionsModel.user_id == user.id,
                TransactionsModel.type == "expense",
                TransactionsModel.created_at >= start_of_month,
                TransactionsModel.created_at < end_of_month
            )
        )

        total_expense = float(expense_stmt) if expense_stmt else 0.0

        # SPEND GROUP BY CATEGORY
        spent_by_category_stmt = (
            select(
                CategoriesModel.name.label("category_name"),
                func.sum(TransactionsModel.amount).label("total_spent"),
                func.count(TransactionsModel.id).label("transaction_count")
            )
            .join(CategoriesModel, TransactionsModel.category_id == CategoriesModel.id)
            .where(
                TransactionsModel.user_id == user.id,
                TransactionsModel.type == "expense",
                TransactionsModel.created_at >= start_of_month,
                TransactionsModel.created_at < end_of_month
            ).group_by(CategoriesModel.name)
        )

        spent_by_category_result = await session.execute(spent_by_category_stmt)
        rows = spent_by_category_result.all()

        category_expenses: list[CategoryExpensesSchema] = [
            {
                "category_name": row.category_name,
                "total_spent": float(row.total_spent),
                "transaction_count": row.transaction_count
            }
            for row in rows
        ]

        #  Top 5 Largest Transactions (both income & expense)
        top_five_transactions_stmt = (
            select(
                CategoriesModel.name.label("category_name"),
                TransactionsModel.note.label("note"),
                TransactionsModel.type.label("transaction_type"),
                TransactionsModel.amount.label("amount"),
                PaymentOptionsModel.name.label("payment_mode"),
                TransactionsModel.created_at.label("date")
            )
            .join(CategoriesModel, TransactionsModel.category_id == CategoriesModel.id)
            .join(
                PaymentOptionsModel,
                TransactionsModel.payment_option_id == PaymentOptionsModel.id
            )
            .where(
                TransactionsModel.user_id == user.id,
                TransactionsModel.created_at >= start_of_month,
                TransactionsModel.created_at < end_of_month
            )
            .group_by(
                CategoriesModel.name,
                TransactionsModel.note,
                TransactionsModel.type,
                TransactionsModel.amount,
                PaymentOptionsModel.name,
                TransactionsModel.created_at
            )
            .order_by(TransactionsModel.amount.desc())
            .limit(5)
        )

        top_five_transactions_result = await session.execute(top_five_transactions_stmt)
        top_five_rows = top_five_transactions_result.all()

        top_transactions: list[TopLargestTransactionSchema] = [
            {
                "category_name": row.category_name,
                "note": row.note,
                "transaction_type": row.transaction_type,
                "amount": float(row.amount),
                "payment_mode": row.payment_mode,
                "date": row.date.isoformat()
            } for row in top_five_rows
        ]

        # Payment Mode Breakdown (Most used Payment Mode for expenses.)
        spent_by_payment_mode_stmt = (
            select(
                CategoriesModel.name.label("category_name"),
                PaymentOptionsModel.name.label("payment_mode"),
                TransactionsModel.amount.label("amount"),
                TransactionsModel.created_at.label("date"),
            )
            .join(CategoriesModel, TransactionsModel.category_id == CategoriesModel.id)
            .join(
                PaymentOptionsModel,
                TransactionsModel.payment_option_id == PaymentOptionsModel.id
            )
            .where(
                TransactionsModel.user_id == user.id,
                TransactionsModel.created_at >= start_of_month,
                TransactionsModel.created_at < end_of_month,
                TransactionsModel.type == "expense"
            )
            .order_by(PaymentOptionsModel.name.asc())
        )

        spent_by_payment_mode_result = await session.execute(spent_by_payment_mode_stmt)
        payment_mode_rows = spent_by_payment_mode_result.all()

        payment_mode_expenses: list[PaymentModeExpensesSchema] = [
            {
                "category_name": row.category_name,
                "payment_mode": row.payment_mode,
                "amount": float(row.amount),
                "date": row.date.isoformat()
            } for row in payment_mode_rows
        ]

        metrics = MetricsSchema(
            total_income=total_income,
            total_expense=total_expense
        )

        payload = AggregatedDataSchema(
            metrics=metrics,
            category_expenses=category_expenses,
            expenses_by_payment_mode=payment_mode_expenses,
            top_largest_transactions=top_transactions
        )

        return payload

    except SQLAlchemyError as err:
        print(f" ERR :: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SWW")


def data_formatter(aggregated_data: AggregatedDataSchema, month: str, year: str):
    total_income = aggregated_data.metrics.total_income
    total_expense = aggregated_data.metrics.total_expense
    net_savings = total_income - total_expense
    savings_rate = (net_savings/total_income * 100) if total_income > 0 else 0.0

    # Categories: Sort categories by spend and Compute percentage of total expense
    categories = sorted(
        aggregated_data.category_expenses,
        key=lambda c: c.total_spent,
        reverse=True
    )

    category_info: list[str] = []

    for category in categories:
        percentage = (
            category.total_spent/total_expense * 100
            if total_expense > 0 else 0
        )

        category_info.append(
            f"- {category.category_name}: ₹{category.total_spent:.2f} "
            f"({percentage:.1f}% of spend, {category.transaction_count} transactions)."
        )

    category_summary = (
        "\n"
        .join(category_info)
        if len(category_info) > 0
        else "No expenses recorded."
    )

    # Transactions: Extract transaction data into free texts.
    top_transactions_info: list[str] = []
    for t in aggregated_data.top_largest_transactions:
        top_transactions_info.append(
            f"- {t.transaction_type.title()} of ₹{t.amount:.2f} in {t.category_name.title()} "
            f"via {t.payment_mode.title()} ({t.note or 'No Note'})"
        )

    top_transactions_summary = (
        "\n".join(top_transactions_info)
        if len(top_transactions_info) > 0
        else "No notable transactions."
    )

    # Expenses by Payment Mode:
    payment_mode_totals: dict[str, float] = {}

    for mode in aggregated_data.expenses_by_payment_mode:
        payment_mode_totals[mode.payment_mode] = (
            payment_mode_totals.get(mode.payment_mode, 0) + mode.amount
        )

    expenses_by_payment_mode_summary = (
        "\n"
        .join(
            f"- {mode}: ₹{amt:.2f}" for mode, amt in sorted(
                payment_mode_totals.items(),
                key=lambda m: m[1],
                reverse=True
            )
        ) if payment_mode_totals else "No Payment Mode Data."
    )

    result = {
        "month_label": month,
        "year": year,
        "total_income": f"{total_income:.2f}",
        "total_expense": f"{total_expense:.2f}",
        "net_savings": f"{net_savings:.2f}",
        "savings_rate": f"{savings_rate:.1f}",
        "category_summary": category_summary,
        "top_transactions_summary": top_transactions_summary,
        "expenses_by_payment_mode_summary": expenses_by_payment_mode_summary
    }

    return result


summary_chain = SUMMARY_NARRATOR_PROMPT | structured_llm

# async def get_net_balance_change():
#     try:
#         net_balance_cte = (
#             select(
#                 TransactionsModel.created_at.label("date"),
#                 TransactionsModel.type.label("transaction_type"),
#                 case(
#                     (TransactionsModel.type == "expense", -TransactionsModel.amount),
#                     (TransactionsModel.type == "income", TransactionsModel.amount),
#                     else_=TransactionsModel.amount
#                 ).label("amount")
#             )
#             .where(
#                 TransactionsModel.user_id == user.id,
#                 TransactionsModel.created_at >= start_of_month,
#                 TransactionsModel.created_at < end_of_month
#             )
#             .cte("net_balance_cte")

#         )

#         stmt = select(
#             net_balance_cte.c.date,
#             net_balance_cte.c.transaction_type,
#             net_balance_cte.c.amount,
#             (
#                 func.sum(net_balance_cte.c.amount)
#                 .over(order_by=net_balance_cte.c.date)
#                 .label("running_net_balance")
#             )
#         )

#         net_balance = await session.execute(stmt)
#         net_balance_result = net_balance.all()

#         net_balance = [
#             {
#                 "date": res.date,
#                 "transaction_type": res.transaction_type,
#                 "amount": float(res.amount),
#                 "running_net_balance": float(res.running_net_balance)
#             } for res in net_balance_result
#         ]

#         print("RUNNIGNG NET BALANCE :::: ", net_balance)
#     except:
#         pass
