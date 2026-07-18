from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent import nodes
from app.config import settings


def _route_after_validation(state: AgentState) -> str:
    if state.get("validation_error"):
        if state.get("repair_attempts", 0) < state.get("max_repair_attempts", settings.MAX_SQL_REPAIR_ATTEMPTS):
            return "repair"
        return "fail"
    return "execute"


def _route_after_execution(state: AgentState) -> str:
    if state.get("execution_error"):
        if state.get("repair_attempts", 0) < state.get("max_repair_attempts", settings.MAX_SQL_REPAIR_ATTEMPTS):
            return "repair"
        return "fail"
    return "success"


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("understand_intent", nodes.understand_intent_node)
    graph.add_node("retrieve_schema", nodes.retrieve_schema_node)
    graph.add_node("generate_sql", nodes.generate_sql_node)
    graph.add_node("validate_sql", nodes.validate_sql_node)
    graph.add_node("execute_sql", nodes.execute_sql_node)
    graph.add_node("repair_sql", nodes.repair_sql_node)
    graph.add_node("load_dataframe", nodes.load_dataframe_node)
    graph.add_node("visualize", nodes.visualize_node)
    graph.add_node("generate_insight", nodes.insight_node)
    graph.add_node("fail", nodes.failure_node)

    graph.set_entry_point("understand_intent")

    graph.add_edge("understand_intent", "retrieve_schema")
    graph.add_edge("retrieve_schema", "generate_sql")
    graph.add_edge("generate_sql", "validate_sql")

    graph.add_conditional_edges(
        "validate_sql",
        _route_after_validation,
        {"repair": "repair_sql", "execute": "execute_sql", "fail": "fail"},
    )

    graph.add_conditional_edges(
        "execute_sql",
        _route_after_execution,
        {"repair": "repair_sql", "success": "load_dataframe", "fail": "fail"},
    )

    # Repair loop always re-validates before trying to execute again
    graph.add_edge("repair_sql", "validate_sql")

    graph.add_edge("load_dataframe", "visualize")
    graph.add_edge("visualize", "generate_insight")
    graph.add_edge("generate_insight", END)
    graph.add_edge("fail", END)

    return graph.compile()


# Compiled once at import time and reused across requests
agent_app = build_agent_graph()
