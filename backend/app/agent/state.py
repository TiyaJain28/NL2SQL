from typing import TypedDict, Optional, Any


class AgentState(TypedDict, total=False):
    # Input
    question: str
    conversation_history: list[dict]  # [{"question": ..., "sql": ...}, ...]

    # Working state
    intent: str
    schema_text: str
    sql: str
    validated_sql: str
    validation_error: Optional[str]

    execution_error: Optional[str]
    repair_attempts: int
    max_repair_attempts: int

    columns: list[str]
    rows: list[dict[str, Any]]

    chart_type: Optional[str]
    chart_json: Optional[str]

    insight: str
    final_error: Optional[str]
