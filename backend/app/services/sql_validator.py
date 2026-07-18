"""
Enforces that agent-generated SQL is safe to run:
- SELECT-only (no DDL/DML)
- exactly one statement
- forbidden keywords blocked even inside CTEs/subqueries
- automatically injects a LIMIT cap if the query doesn't have one
"""

import re
import sqlparse
from app.config import settings

FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "GRANT", "REVOKE", "CREATE", "REPLACE", "MERGE", "CALL",
    "EXECUTE", "COPY", "VACUUM", "ATTACH", "DETACH",
}


class SQLValidationError(Exception):
    pass


def validate_and_sanitize(sql: str) -> str:
    sql = sql.strip().rstrip(";")

    if not sql:
        raise SQLValidationError("Empty SQL generated.")

    statements = sqlparse.parse(sql)
    if len(statements) != 1:
        raise SQLValidationError("Only a single SQL statement is allowed.")

    stmt = statements[0]
    stmt_type = stmt.get_type()
    if stmt_type not in ("SELECT", "UNKNOWN"):
        raise SQLValidationError(f"Only SELECT statements are allowed (got {stmt_type}).")

    # Guard against SELECT ... INTO (writes a new table)
    if re.search(r"\bSELECT\b.*\bINTO\b", sql, re.IGNORECASE):
        raise SQLValidationError("SELECT INTO is not permitted.")

    upper_sql = sql.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            raise SQLValidationError(f"Forbidden keyword detected: {keyword}")

    if not re.match(r"^\s*(SELECT|WITH)\b", sql, re.IGNORECASE):
        raise SQLValidationError("Query must start with SELECT or WITH.")

    # Enforce a row limit cap to protect the DB from runaway result sets
    if not re.search(r"\bLIMIT\s+\d+\b", upper_sql):
        sql = f"{sql}\nLIMIT {settings.MAX_ROW_LIMIT}"
    else:
        # Clamp existing LIMIT to the max allowed
        def _clamp(match):
            n = min(int(match.group(1)), settings.MAX_ROW_LIMIT)
            return f"LIMIT {n}"
        sql = re.sub(r"LIMIT\s+(\d+)", _clamp, sql, flags=re.IGNORECASE)

    return sql
