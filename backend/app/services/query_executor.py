from sqlalchemy.exc import SQLAlchemyError
from app.database import run_readonly_query


class QueryExecutionError(Exception):
    pass


def execute_sql(sql: str):
    """Runs SQL against the read-only DB role. Raises QueryExecutionError
    with the underlying Postgres message on failure, so it can be fed
    back into the agent's repair loop."""
    try:
        columns, rows = run_readonly_query(sql)
        return columns, rows
    except SQLAlchemyError as e:
        raise QueryExecutionError(str(e.__cause__ or e)) from e
