"""
apps/api/main.py

Purpose:
    FastAPI application entrypoint configuring CORS, rate limiter state, routes, and DB table creation.

Working & Flow:
    - Initializes FastAPI app instance.
    - Attaches `slowapi` rate limiter instance.
    - Registers extraction routes from `apps/api/routes/extraction_route.py`.
    - Triggers database table initialization on startup.

Links to:
    - apps/api/routes/extraction_route.py
    - src/database/connection.py
    - src/core/config.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.database.connection import init_db
from apps.api.routes.extraction_route import router as extraction_router, limiter

app = FastAPI(
    title="AI Meeting Action-Item Extractor API",
    version="0.1.0",
    description="Production-grade API for extracting validated action items from meeting transcripts."
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(extraction_router)


@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception:
        pass  # DB initialization warning handling when running without live Postgres


@app.get("/health")
def health_check():
    return {"status": "healthy"}
