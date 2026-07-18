import uuid

# Simple in-process conversation store: { conversation_id: [ {question, sql}, ... ] }
# Swap this for Redis / a database table for multi-instance deployments.
_conversations: dict[str, list[dict]] = {}


def new_conversation_id() -> str:
    return str(uuid.uuid4())


def get_history(conversation_id: str) -> list[dict]:
    return _conversations.get(conversation_id, [])


def append_turn(conversation_id: str, question: str, sql: str) -> None:
    _conversations.setdefault(conversation_id, []).append({"question": question, "sql": sql})
