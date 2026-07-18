from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Read-only engine — used to actually execute agent-generated SQL.
readonly_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Admin engine — used only for schema introspection (information_schema is
# readable by the readonly role too, but kept separate for clarity/extension).
admin_engine = create_engine(settings.ADMIN_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=readonly_engine)


def run_readonly_query(sql: str, params: dict | None = None):
    """Execute a validated, read-only SQL statement and return rows + columns."""
    with readonly_engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return columns, rows
