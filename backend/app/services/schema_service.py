"""
Retrieves live database schema (tables, columns, types, FK relationships)
so the LLM can ground SQL generation in the real structure of the database
instead of guessing column names.
"""

from sqlalchemy import text
from app.database import admin_engine

_SCHEMA_QUERY = """
SELECT
    c.table_name,
    c.column_name,
    c.data_type,
    c.is_nullable
FROM information_schema.columns c
WHERE c.table_schema = 'public'
ORDER BY c.table_name, c.ordinal_position;
"""

_FK_QUERY = """
SELECT
    tc.table_name        AS source_table,
    kcu.column_name       AS source_column,
    ccu.table_name         AS target_table,
    ccu.column_name        AS target_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
    ON tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
"""


def get_schema_text(cache: dict = {}) -> str:
    """Returns a compact, LLM-friendly text description of the schema.
    Cached in-process since schema rarely changes during a session."""
    if "schema_text" in cache:
        return cache["schema_text"]

    with admin_engine.connect() as conn:
        columns = conn.execute(text(_SCHEMA_QUERY)).fetchall()
        fks = conn.execute(text(_FK_QUERY)).fetchall()

    tables: dict[str, list[str]] = {}
    for table_name, column_name, data_type, is_nullable in columns:
        tables.setdefault(table_name, []).append(f"{column_name} ({data_type})")

    lines = []
    for table, cols in tables.items():
        lines.append(f"TABLE {table}: " + ", ".join(cols))

    if fks:
        lines.append("\nFOREIGN KEYS:")
        for src_t, src_c, tgt_t, tgt_c in fks:
            lines.append(f"  {src_t}.{src_c} -> {tgt_t}.{tgt_c}")

    schema_text = "\n".join(lines)
    cache["schema_text"] = schema_text
    return schema_text
