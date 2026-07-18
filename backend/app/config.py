from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://analytics_readonly:readonly_pw@localhost:5432/analytics"
    ADMIN_DATABASE_URL: str = "postgresql+psycopg2://app_admin:app_admin_pw@localhost:5432/analytics"

    # LLM
    LLM_PROVIDER: str = "openai"          # "openai" or "gemini"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

    # Agent behavior
    MAX_SQL_REPAIR_ATTEMPTS: int = 3
    MAX_ROW_LIMIT: int = 500

    class Config:
        env_file = ".env"


settings = Settings()
