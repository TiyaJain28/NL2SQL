INTENT_PROMPT = """Classify the analytical intent of this business question into
exactly one label: AGGREGATION, TREND, COMPARISON, RANKING, LOOKUP, FOLLOW_UP.

Question: {question}

Respond with only the label."""


SQL_GENERATION_PROMPT = """You are an expert PostgreSQL analyst. Generate a single
read-only SQL SELECT query that answers the user's question, using ONLY the
tables/columns given in the schema below. Never invent columns or tables.

Rules:
- Output ONLY the SQL query, no explanation, no markdown fences.
- Use explicit JOINs with proper foreign key relationships from the schema.
- Always alias aggregate columns with meaningful names (e.g. total_revenue).
- Add ORDER BY / LIMIT when the question implies "top N" or ranking.
- If the question references dates like "this month" or "this quarter", use
  CURRENT_DATE and date_trunc() appropriately.
- If this is a follow-up question, take the prior conversation into account.

Schema:
{schema_text}

Conversation so far:
{conversation_history}

Question: {question}

SQL:"""


SQL_REPAIR_PROMPT = """The following PostgreSQL query failed when executed.
Fix it. Output ONLY the corrected SQL query, no explanation, no markdown fences.

Schema:
{schema_text}

Original question: {question}

Failed SQL:
{failed_sql}

Database error:
{error_message}

Corrected SQL:"""
