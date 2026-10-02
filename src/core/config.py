"""
src/core/config.py

Purpose:
    Centralized configuration management loading environment variables.
    Provides database settings, LLM config, and API parameters across the application.

Working & Flow:
    Reads settings using pydantic-settings / os env fallback.
    Exposes singleton `settings` object used by database connection, API routes, and extractor.

Links to:
    - src/database/connection.py
    - src/extraction/extractor.py
    - apps/api/main.py
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "development")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/meeting_db"
    )
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))


settings = Settings()
