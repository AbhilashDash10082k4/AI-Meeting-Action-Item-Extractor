"""
src/database/connection.py

Purpose:
    SQLAlchemy database engine and session management for PostgreSQL (or SQLite fallback for tests).

Working & Flow:
    - Creates SQLAlchemy engine using settings.database_url.
    - Exposes `get_db()` session generator dependency.
    - Exposes `init_db()` table creation helper.

Links to:
    - src/core/config.py
    - src/database/models.py
    - src/database/repository.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.core.config import settings


class Base(DeclarativeBase):
    pass


# Use sqlite in-memory fallback if postgres URL is unavailable during local testing
db_url = settings.database_url
if "postgresql" in db_url and "localhost" in db_url and settings.app_env == "test":
    db_url = "sqlite:///:memory:"

connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
