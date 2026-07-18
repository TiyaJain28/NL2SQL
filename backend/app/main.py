from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.seed_service import run_seed        
from app.api.routes import router

app = FastAPI(
    title="Agentic AI Analytics Assistant",
    description="NL-to-SQL agent: understands questions, generates & validates SQL, "
                 "self-repairs on error, visualizes results, and explains insights.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Agentic AI Analytics Assistant is running. See /docs for API."}
