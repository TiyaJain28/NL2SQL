import pandas as pd
from app.agent.llm_client import get_llm


INSIGHT_PROMPT = """You are a business analyst. Given the user's question and the
resulting data (as a small preview table), write a concise (2-4 sentence)
natural-language business insight. Mention concrete numbers from the data.
Do not restate the SQL. Do not mention tables or columns names verbatim.

Question: {question}

Data preview (CSV, up to 15 rows):
{preview}

Insight:"""


def generate_insight(question: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "The query returned no results for this question. Try broadening the filters or date range."

    preview = df.head(15).to_csv(index=False)
    llm = get_llm()
    prompt = INSIGHT_PROMPT.format(question=question, preview=preview)
    response = llm.invoke(prompt)
    return response.content.strip() if hasattr(response, "content") else str(response).strip()
