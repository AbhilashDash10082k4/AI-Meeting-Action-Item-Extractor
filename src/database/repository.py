"""
src/database/repository.py

Purpose:
    Repository pattern abstraction for executing database CRUD operations via SQLAlchemy.

Working & Flow:
    - Called exclusively by Service layer (`ExtractionService`).
    - `save_transcript_and_action_items()` persists raw transcripts & validated ActionItem schemas.
    - `get_transcript_action_items()` queries stored items for a transcript ID.

Links to:
    - src/database/models.py
    - src/extraction/schemas.py
    - src/services/extraction_service.py
"""

from sqlalchemy.orm import Session
from src.database.models import TranscriptRecord, ActionItemRecord
from src.extraction.schemas import ActionItem


class ActionItemRepository:
    """Repository handling direct SQL operations for transcripts and action items."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def save_transcript(self, filename: str, raw_text: str) -> TranscriptRecord:
        record = TranscriptRecord(filename=filename, raw_text=raw_text)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def save_action_items(self, transcript_id: str, action_items: list[ActionItem]) -> list[ActionItemRecord]:
        records: list[ActionItemRecord] = []
        for item in action_items:
            rec = ActionItemRecord(
                transcript_id=transcript_id,
                task=item.task,
                owner=item.owner,
                deadline=item.deadline,
                status=item.status,
                confidence=item.confidence,
                evidence=item.evidence,
                source_segment_ids=item.source_segment_ids
            )
            self.db.add(rec)
            records.append(rec)
        self.db.commit()
        for rec in records:
            self.db.refresh(rec)
        return records

    def get_action_items_by_transcript(self, transcript_id: str) -> list[ActionItemRecord]:
        return (
            self.db.query(ActionItemRecord)
            .filter(ActionItemRecord.transcript_id == transcript_id)
            .all()
        )
