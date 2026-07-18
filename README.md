# Agentic AI Analytics Assistant (NL-to-SQL)

An enterprise-style AI analytics assistant that lets users ask business
questions in plain English and get back validated SQL, results, a chart,
and a natural-language insight — powered by a **LangGraph agentic workflow**
rather than a single prompt-response call.

## Architecture

```
React (Vite + Tailwind + Plotly)
        │  POST /api/query
        ▼
FastAPI backend
        ▼
LangGraph Agent
  1. understand_intent   – classify the question
  2. retrieve_schema     – introspect live Postgres schema
  3. generate_sql        – LLM writes SQL grounded in schema + history
  4. validate_sql        – SELECT-only, single statement, LIMIT cap
  5. execute_sql         – run against a read-only Postgres role
  6. repair_sql (loop)   – on validation/execution failure, re-prompt LLM
                            with the error, up to MAX_SQL_REPAIR_ATTEMPTS
  7. load_dataframe       – results → Pandas
  8. visualize            – heuristic chooses bar/line/grouped-bar/table
  9. insight              – LLM writes a short business summary
        ▼
JSON response → rendered in React (table + Plotly chart + insight + SQL)
```

## Project layout

```
nl-to-sql-agent/
├── docker-compose.yml
├── backend/
│   └── app/
│       ├── main.py, config.py, database.py, models.py
│       ├── agent/        # LangGraph state, prompts, nodes, graph, memory
│       ├── services/     # schema, validator, executor, viz, insight
│       ├── api/routes.py
│       └── db/seed.sql   # sample e-commerce schema + seed data
└── frontend/
    └── src/
        ├── App.jsx, components/, api/client.js
```

## Running locally with Docker

```bash
cp .env.example .env      # add your OPENAI_API_KEY
docker compose up --build
```

- Backend: http://localhost:8000/docs (FastAPI Swagger UI)
- Frontend: http://localhost:3000
- Postgres: localhost:5432 (db `analytics`, seeded with a sample
  products/orders/customers/regions schema)

## Running without Docker

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# start a local Postgres and run backend/app/db/seed.sql against it,
# then set DATABASE_URL / ADMIN_DATABASE_URL in a .env file
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Security notes

- SQL execution uses a dedicated `analytics_readonly` Postgres role — even if
  the LLM or validator were somehow bypassed, the DB connection itself cannot
  write.
- `sql_validator.py` blocks DDL/DML keywords, multi-statement queries, and
  enforces a maximum row `LIMIT`.
- Conversation memory is in-process for simplicity (`agent/memory.py`) —
  swap for Redis or a database table for a multi-instance production
  deployment.

## Example

**Q:** "Show the top 5 products by revenue this quarter."
**Agent:** generates a `JOIN`-based aggregation query, validates it, executes
it, renders a bar chart, and returns something like: *"Aurora Wireless
Headphones led this quarter with $4,230 in revenue, followed by Pulse
Smartwatch at $3,890…"*

## Extending

- Add more chart heuristics or let the LLM choose chart type explicitly.
- Add a `HumanApprovalNode` before execution for high-risk queries.
- Persist conversation memory + query logs to Postgres for audit trails.
- Add role-based schema filtering so different users only see permitted tables.
