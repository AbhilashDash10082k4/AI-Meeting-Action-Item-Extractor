"""
tests/test_pipeline.py

Purpose:
    Unit tests for parsing, preprocessing, deterministic validation, and extraction.

Working & Flow:
    - Tests transcript cleaning/chunking.
    - Tests evidence grounding and deduplication.
    - Tests the credential-free mock extraction path and missing-owner behavior.

Links to:
    - src/ingestion/parser.py
    - src/preprocessing/cleaner.py
    - src/preprocessing/chunker.py
    - src/validation/validator.py
    - src/services/extraction_service.py
    - src/extraction/extractor.py
"""

from src.ingestion.parser import IngestionParser
from src.preprocessing.cleaner import TranscriptCleaner
from src.preprocessing.chunker import TranscriptChunker
from src.extraction.schemas import ActionItem, ExtractionResult, TranscriptSegment
from src.validation.validator import GuardrailValidator
from src.services.extraction_service import ExtractionService


def test_cleaner_and_chunker():
    """Verifies that transcript text is cleaned and split into speaker segments."""
    raw = "[Alice]: Hello team\n\n[Bob]: I will take task A."
    cleaned = TranscriptCleaner.clean_text(raw)
    segments = TranscriptChunker.chunk_transcript(cleaned)

    assert len(segments) == 2
    assert segments[0].speaker == "Alice"
    assert segments[0].text == "Hello team"
    assert segments[1].speaker == "Bob"
    assert segments[1].text == "I will take task A."


def test_validator_exact_evidence_grounding():
    """Rejects action items whose evidence quote is absent from the transcript."""
    segments = [
        TranscriptSegment(
            id="seg-1",
            speaker="Bob",
            text="I will write the test cases.",
            sequence=1
        )
    ]
    full_text = "[Bob]: I will write the test cases."

    valid_item = ActionItem(
        task="Write test cases",
        owner="Bob",
        deadline=None,
        status="pending",
        confidence=0.9,
        evidence="I will write the test cases.",
        source_segment_ids=["seg-1"]
    )

    hallucinated_item = ActionItem(
        task="Refactor backend API",
        owner="Bob",
        deadline=None,
        status="pending",
        confidence=0.9,
        evidence="I will completely rewrite the backend system next month.",
        source_segment_ids=["seg-1"]
    )

    res = ExtractionResult(action_items=[valid_item, hallucinated_item])
    validated = GuardrailValidator.validate_and_deduplicate(res, segments, full_text)

    assert len(validated) == 1
    assert validated[0].task == "Write test cases"


def test_validator_deduplication():
    """Keeps only one copy of duplicate task-owner pairs."""
    segments = [
        TranscriptSegment(
            id="seg-1",
            speaker="Alice",
            text="Task 1",
            sequence=1
        )
    ]
    full_text = "Task 1"

    item1 = ActionItem(
        task="Task 1",
        owner="Alice",
        deadline=None,
        status="pending",
        confidence=0.8,
        evidence="Task 1",
        source_segment_ids=["seg-1"]
    )
    item2 = ActionItem(
        task="Task 1",
        owner="Alice",
        deadline=None,
        status="pending",
        confidence=0.9,
        evidence="Task 1",
        source_segment_ids=["seg-1"]
    )

    res = ExtractionResult(action_items=[item1, item2])
    validated = GuardrailValidator.validate_and_deduplicate(res, segments, full_text)

    assert len(validated) == 1


def test_extraction_service_end_to_end():
    """Verifies the complete credential-free extraction service flow."""
    service = ExtractionService()
    content = b"[Alice]: I will complete the deployment by Friday."
    t_id, segments, items = service.process_transcript_file("test.txt", content)

    assert len(segments) == 1
    assert len(items) == 1
    assert items[0].owner is None
    assert "deployment" in items[0].task


def test_extraction_service_does_not_assign_speaker_as_owner():
    """Ensures a speaker is not treated as an owner without explicit assignment."""
    service = ExtractionService()
    content = b"[Alice]: We should consider improving deployment next quarter."
    _, _, items = service.process_transcript_file("test.txt", content)

    assert items == []
