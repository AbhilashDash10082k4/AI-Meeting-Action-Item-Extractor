"""
src/database/models.py

Purpose:
    SQLAlchemy ORM definitions for transcripts and extracted action items.

Working & Flow:
    - `TranscriptRecord`: Stores filename, raw text, and upload timestamp.
    - `ActionItemRecord`: Stores extracted task fields linked via foreign key to TranscriptRecord.

Links to:
    - src/database/connection.py
    - src/database/repository.py
"""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.connection import Base


class TranscriptRecord(Base):
    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    action_items: Mapped[list["ActionItemRecord"]] = relationship(
        "ActionItemRecord", back_populates="transcript", cascade="all, delete-orphan"
    )


class ActionItemRecord(Base):
    __tablename__ = "action_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transcript_id: Mapped[str] = mapped_column(String(36), ForeignKey("transcripts.id"), nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    source_segment_ids: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transcript: Mapped["TranscriptRecord"] = relationship("TranscriptRecord", back_populates="action_items")
