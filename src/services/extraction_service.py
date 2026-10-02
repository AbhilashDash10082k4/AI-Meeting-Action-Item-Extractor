"""
src/services/extraction_service.py

Purpose:
    Core business logic service orchestrating the full meeting extraction pipeline.

Working & Flow:
    - Executed by Controller layer (`ExtractionController`).
    - Step 1: `IngestionParser` extracts raw text from document file.
    - Step 2: `TranscriptCleaner` normalizes raw text string.
    - Step 3: `TranscriptChunker` converts text into indexed `TranscriptSegment` list.
    - Step 4: `LLMExtractor` generates candidate `ActionItem` list.
    - Step 5: `GuardrailValidator` performs 6 deterministic checks & deduplication.
    - Step 6: `ActionItemRepository` persists records to PostgreSQL.

Links to:
    - src/ingestion/parser.py
    - src/preprocessing/cleaner.py
    - src/preprocessing/chunker.py
    - src/extraction/extractor.py
    - src/validation/validator.py
    - src/database/repository.py
    - apps/api/controllers/extraction_controller.py
"""

from typing import BinaryIO
from sqlalchemy.orm import Session
from src.ingestion.parser import IngestionParser
from src.preprocessing.cleaner import TranscriptCleaner
from src.preprocessing.chunker import TranscriptChunker
from src.extraction.extractor import LLMExtractor
from src.validation.validator import GuardrailValidator
from src.database.repository import ActionItemRepository
from src.extraction.schemas import ActionItem, TranscriptSegment, ExtractionResult


class ExtractionService:
    """Service layer executing business logic for processing transcripts and extracting action items."""

    def __init__(self, db_session: Session | None = None):
        self.db_session = db_session
        self.extractor = LLMExtractor()

    def process_transcript_file(
        self,
        filename: str,
        content_bytes: bytes
    ) -> tuple[str, list[TranscriptSegment], list[ActionItem]]:
        # 1. Ingestion
        raw_text = IngestionParser.parse_file(filename, content_bytes)

        # 2. Preprocessing
        cleaned_text = TranscriptCleaner.clean_text(raw_text)
        segments = TranscriptChunker.chunk_transcript(cleaned_text)

        # 3. LLM Extraction
        raw_result: ExtractionResult = self.extractor.extract_action_items(segments)

        # 4. Guardrail Validation & Deduplication
        validated_items = GuardrailValidator.validate_and_deduplicate(
            result=raw_result,
            segments=segments,
            full_transcript=cleaned_text
        )

        # 5. DB Persistence (if DB session attached)
        transcript_id = "temp-transcript-id"
        if self.db_session:
            repo = ActionItemRepository(self.db_session)
            transcript_record = repo.save_transcript(filename=filename, raw_text=cleaned_text)
            transcript_id = transcript_record.id
            repo.save_action_items(transcript_id=transcript_id, action_items=validated_items)

        return transcript_id, segments, validated_items
