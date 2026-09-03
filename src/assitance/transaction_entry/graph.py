from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional
import operator

from src.assitance.llm.groq import create_groq_llm_instance
from src.assitance.transaction_entry.schema import ExtractedTransactionSchema
from src.transaction import controller
from src.transaction.schema import TransactionCreateSchema
from src.utils.db_helper import get_or_create
from src.categories.models import CategoriesModel
from src.categories.controller import get_deterministic_color
from src.payment_options.models import PaymentOptionsModel


llm = create_groq_llm_instance(temperature=0.2)
structured_llm = llm.with_structured_output(
    ExtractedTransactionSchema)


class GraphState(BaseModel):
    user_input: str = Field(description="The user input to the graph.")
    conversation_history: Annotated[List[str], operator.add] = []
    extracted: Optional[ExtractedTransactionSchema] = None
    final_response: Optional[str] = None


EXTRACTION_PROMPT = PromptTemplate(
    template="""
        You are a financial assistant extracting transaction details.

        Below is the conversation so far (it may span multiple messages, where later
        messages answer questions raised by earlier ones). Treat it as one combined input.

        Required fields: title, transaction_type (income/expense), amount, category, payment_option.

        If title is missing, add one based on the context of the message.
        If anything required is missing, except title, set is_complete to False and write a short, polite
        clarifying question in missing_info_message asking only for what's missing.

        If everything is present, set is_complete to True, leave missing_info_message null,
        and fill in all fields. Always copy the user's original message into `note`.
            
        Conversation so far:
        {user_input}
        """,
    input_variables=["user_input"]
)


def extractor(state: GraphState):
    full_conversation = "\n".join(
        state.conversation_history + [state.user_input])

    prompt = EXTRACTION_PROMPT.format(user_input=full_conversation)
    result: ExtractedTransactionSchema = structured_llm.invoke(prompt)

    print("RESULT :: SCHEMA :: ", result)

    return {"extracted": result, "conversation_history": [state.user_input]}


def route_after_extraction(state: GraphState):
    return "create_transaction" if state.extracted.is_complete else "ask_again"


async def create_transaction_node(state: GraphState, config: RunnableConfig):
    session: AsyncSession = config["configurable"]["session"]
    user = config["configurable"]["user"]
    data = state.extracted

    print("extracted :: ", data)

    try:
        category_id = await get_or_create(
            session, CategoriesModel, user.id, data.category,
            extra_defaults={"color": get_deterministic_color(data.category)}
        )
        payment_option_id = await get_or_create(
            session, PaymentOptionsModel, user.id, data.payment_option,
            extra_defaults={"payment_type": data.payment_type}
        )

        payload = TransactionCreateSchema(
            amount=data.amount,
            category_id=category_id,
            payment_option_id=payment_option_id,
            note=data.note,
            title=data.title,
            type=data.transaction_type,
        )

        await controller.create_transaction(payload, session, user)
        await session.commit()

    except SQLAlchemyError as err:
        await session.rollback()
        print(
            f"Error while creating transaction through AI assistance :: {err}")
        return {
            "final_response": "Something went wrong while saving your transaction. Please try again."
        }

    message = f"Added {data.transaction_type} of {data.amount} under '{data.category}' ({data.payment_option})"
    return {"final_response": message}


def ask_again_node(state: GraphState):
    return {"final_response": state.extracted.missing_info_message}


graph_builder = StateGraph(GraphState)
graph_builder.add_node("extractor", extractor)
graph_builder.add_node("create_transaction", create_transaction_node)
graph_builder.add_node("ask_again", ask_again_node)

graph_builder.add_edge(START, "extractor")
graph_builder.add_conditional_edges(
    "extractor",
    route_after_extraction,
    {
        "create_transaction": "create_transaction",
        "ask_again": "ask_again",
    },
)
graph_builder.add_edge("create_transaction", END)
graph_builder.add_edge("ask_again", END)

memory = MemorySaver()
assistance_graph = graph_builder.compile(checkpointer=memory)
