from functools import lru_cache
from app.config import settings


@lru_cache
def get_llm(temperature: float = 0.1):
    """Returns a chat model client. Swap provider via LLM_PROVIDER env var.
    Kept provider-agnostic so OpenAI/Gemini/local models can be swapped
    without touching agent logic."""
    if settings.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
        )
    elif settings.LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")
