"""
src/core/config.py

Purpose:
    Centralized application configuration for database, API, and LLM provider settings.

Working & Flow:
    - Settings reads environment variables used by the API and extraction service.
    - LLM provider/model/key values are consumed by src/extraction/extractor.py.
    - Database and API settings are consumed by their respective application modules.

Links to:
    - src/extraction/extractor.py
    - src/database/connection.py
    - apps/api/main.py
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    """Stores application configuration loaded from environment variables."""

    app_env: str = os.getenv("APP_ENV", "development")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/meeting_db"
    )
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").lower()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))


settings = Settings()
