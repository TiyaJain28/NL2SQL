import re
import pandas as pd

from app.agent.state import AgentState
from app.agent.prompts import INTENT_PROMPT, SQL_GENERATION_PROMPT, SQL_REPAIR_PROMPT
from app.agent.llm_client import get_llm
from app.services.schema_service import get_schema_text
from app.services.sql_validator import validate_and_sanitize, SQLValidationError
from app.services.query_executor import execute_sql, QueryExecutionError
from app.services.viz_service import choose_chart
from app.services.insight_service import generate_insight


def _clean_sql(raw: str) -> str:
    """Strips markdown fences if the LLM adds them despite instructions."""
    raw = raw.strip()
    raw = re.sub(r"^```sql\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"```$", "", raw)
    return raw.strip()


def understand_intent_node(state: AgentState) -> AgentState:
    llm = get_llm()
    prompt = INTENT_PROMPT.format(question=state["question"])
    response = llm.invoke(prompt)
    intent = (response.content if hasattr(response, "content") else str(response)).strip()
    state["intent"] = intent
    return state


def retrieve_schema_node(state: AgentState) -> AgentState:
    state["schema_text"] = get_schema_text()
    return state


def _format_history(history: list[dict]) -> str:
    if not history:
        return "(none — this is the first question)"
    lines = []
    for turn in history[-5:]:
        lines.append(f"Q: {turn['question']}\nSQL: {turn['sql']}")
    return "\n\n".join(lines)


def generate_sql_node(state: AgentState) -> AgentState:
    llm = get_llm()
    prompt = SQL_GENERATION_PROMPT.format(
        schema_text=state["schema_text"],
        conversation_history=_format_history(state.get("conversation_history", [])),
        question=state["question"],
    )
    response = llm.invoke(prompt)
    raw_sql = response.content if hasattr(response, "content") else str(response)
    state["sql"] = _clean_sql(raw_sql)
    return state


def validate_sql_node(state: AgentState) -> AgentState:
    try:
        state["validated_sql"] = validate_and_sanitize(state["sql"])
        state["validation_error"] = None
    except SQLValidationError as e:
        state["validation_error"] = str(e)
    return state


def execute_sql_node(state: AgentState) -> AgentState:
    try:
        columns, rows = execute_sql(state["validated_sql"])
        state["columns"] = columns
        state["rows"] = rows
        state["execution_error"] = None
    except QueryExecutionError as e:
        state["execution_error"] = str(e)
    return state


def repair_sql_node(state: AgentState) -> AgentState:
    """Feeds the failed SQL + error back to the LLM and regenerates."""
    error_message = state.get("execution_error") or state.get("validation_error") or "Unknown error"
    llm = get_llm()
    prompt = SQL_REPAIR_PROMPT.format(
        schema_text=state["schema_text"],
        question=state["question"],
        failed_sql=state.get("sql", ""),
        error_message=error_message,
    )
    response = llm.invoke(prompt)
    raw_sql = response.content if hasattr(response, "content") else str(response)
    state["sql"] = _clean_sql(raw_sql)
    state["repair_attempts"] = state.get("repair_attempts", 0) + 1
    # clear previous errors before re-validating
    state["validation_error"] = None
    state["execution_error"] = None
    return state


def load_dataframe_node(state: AgentState) -> AgentState:
    df = pd.DataFrame(state.get("rows", []), columns=state.get("columns", []))
    state["_df"] = df  # transient, not part of typed schema but fine at runtime
    return state


def visualize_node(state: AgentState) -> AgentState:
    df = state.get("_df")
    if df is None:
        df = pd.DataFrame(state.get("rows", []), columns=state.get("columns", []))
    chart_type, chart_json = choose_chart(df)
    state["chart_type"] = chart_type
    state["chart_json"] = chart_json
    return state


def insight_node(state: AgentState) -> AgentState:
    df = state.get("_df")
    if df is None:
        df = pd.DataFrame(state.get("rows", []), columns=state.get("columns", []))
    state["insight"] = generate_insight(state["question"], df)
    return state


def failure_node(state: AgentState) -> AgentState:
    state["final_error"] = (
        state.get("execution_error")
        or state.get("validation_error")
        or "The agent could not produce a valid query for this question."
    )
    state["columns"] = state.get("columns", [])
    state["rows"] = state.get("rows", [])
    state["insight"] = f"Sorry, I couldn't answer that: {state['final_error']}"
    state["chart_type"] = "table"
    state["chart_json"] = None
    return state
