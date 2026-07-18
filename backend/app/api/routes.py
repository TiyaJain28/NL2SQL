import json
from fastapi import APIRouter, HTTPException

from app.models import QueryRequest, QueryResponse
from app.agent.graph import agent_app
from app.agent.memory import new_conversation_id, get_history, append_turn
from app.config import settings

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest):
    conversation_id = request.conversation_id or new_conversation_id()
    history = get_history(conversation_id)

    initial_state = {
        "question": request.question,
        "conversation_history": history,
        "repair_attempts": 0,
        "max_repair_attempts": settings.MAX_SQL_REPAIR_ATTEMPTS,
    }

    try:
        final_state = agent_app.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {e}")

    if not final_state.get("final_error"):
        append_turn(conversation_id, request.question, final_state.get("validated_sql", final_state.get("sql", "")))

    chart_json = final_state.get("chart_json")
    chart = json.loads(chart_json) if chart_json else None

    return QueryResponse(
        conversation_id=conversation_id,
        question=request.question,
        sql=final_state.get("validated_sql", final_state.get("sql", "")),
        columns=final_state.get("columns", []),
        rows=final_state.get("rows", []),
        chart=chart,
        chart_type=final_state.get("chart_type"),
        insight=final_state.get("insight", ""),
        repair_attempts=final_state.get("repair_attempts", 0),
        error=final_state.get("final_error"),
    )


@router.get("/health")
def health():
    return {"status": "ok"}
