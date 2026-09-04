from langchain_core.prompts import PromptTemplate

TRANSACTION_EXTRACTION_PROMPT = PromptTemplate(
    template="""
        You are a financial assistant extracting transaction details.

        Below is the conversation so far (it may span multiple messages, where later
        messages answer questions raised by earlier ones). Treat it as one combined input.

        Required fields: title, transaction_type (income/expense), amount, category, payment_option.

        If title is missing, add one based on the context of the message.
        If anything required is missing, except title, 
        set is_complete to False and write a short, polite
        clarifying question in missing_info_message asking only for what's missing.

        If everything is present, set is_complete to True, leave missing_info_message null,
        and fill in all fields. Always copy the user's original message into `note`.
            
        Conversation so far:
        {user_input}
        """,
    input_variables=["user_input"]
)


# SUMMARY_NARRATOR_PROMPT = PromptTemplate(
#     template="""
#       You are a monthly summary narrator for a finance management app.


#     """,
#     input_variables=["date"]
# )
