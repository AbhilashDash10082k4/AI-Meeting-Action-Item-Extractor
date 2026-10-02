"""
src/preprocessing/chunker.py

Purpose:
    Segments cleaned transcript text into structured TranscriptSegment objects with sequence IDs.

Working & Flow:
    - Parses lines for optional speaker patterns (e.g., "John: ...", "[Alice] ...").
    - Constructs `TranscriptSegment` Pydantic models for extraction tracing.

Links to:
    - src/extraction/schemas.py
    - src/services/extraction_service.py
"""

import re
import uuid
from src.extraction.schemas import TranscriptSegment


class TranscriptChunker:
    """Chunks transcript text into indexed segments with speaker detection."""

    SPEAKER_PATTERN = re.compile(r"^(?:\[(?P<speaker1>[^\]]+)\]|(?P<speaker2>[A-Z][a-zA-B0-9\s]{1,20}):)\s*(?P<text>.+)$")

    @staticmethod
    def chunk_transcript(text: str) -> list[TranscriptSegment]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        segments: list[TranscriptSegment] = []

        for idx, line in enumerate(lines):
            match = TranscriptChunker.SPEAKER_PATTERN.match(line)
            if match:
                speaker = match.group("speaker1") or match.group("speaker2")
                segment_text = match.group("text")
            else:
                speaker = None
                segment_text = line

            seg_id = f"seg-{idx + 1}-{uuid.uuid4().hex[:6]}"
            segment = TranscriptSegment(
                id=seg_id,
                speaker=speaker,
                text=segment_text,
                sequence=idx + 1,
                start_time=None,
                end_time=None
            )
            segments.append(segment)

        return segments
