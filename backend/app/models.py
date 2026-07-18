from typing import Any, Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None


class QueryResponse(BaseModel):
    conversation_id: str
    question: str
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    chart: Optional[dict[str, Any]] = None
    chart_type: Optional[str] = None
    insight: str
    repair_attempts: int
    error: Optional[str] = None
