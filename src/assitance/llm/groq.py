from langchain_groq import ChatGroq
from typing import Optional
from src.utils.settings import settings

DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_TEMPERATURE = 0.5


def create_groq_llm_instance(model: Optional[str] = DEFAULT_MODEL, temperature: Optional[float] = DEFAULT_TEMPERATURE):
    groq_llm = ChatGroq(model=model, temperature=temperature,
                        api_key=settings.GROQ_API_KEY)
    return groq_llm
