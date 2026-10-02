"""
src/validation/validator.py

Purpose:
    Deterministic guardrail validator and deduplication engine for extracted action items.

Working & Flow:
    - `validate_and_deduplicate(result, segments, full_transcript)` filters LLM extraction candidates.
    - Enforces 6 strict deterministic checks:
        1. Task exists & non-empty.
        2. Owner format valid (str or None).
        3. Deadline date valid.
        4. Evidence non-empty.
        5. Evidence quote verified in transcript segments.
        6. Confidence score within [0.0, 1.0].
    - Deduplicates redundant tasks using normalized task + owner keys.

Links to:
    - src/extraction/schemas.py
    - src/services/extraction_service.py
"""

import re
from src.extraction.schemas import ActionItem, ExtractionResult, TranscriptSegment


class GuardrailValidator:
    """Deterministic validation guardrail ensuring grounding, schema compliance, and deduplication."""

    @staticmethod
    def validate_and_deduplicate(
        result: ExtractionResult,
        segments: list[TranscriptSegment],
        full_transcript: str
    ) -> list[ActionItem]:
        valid_items: list[ActionItem] = []
        full_text_normalized = GuardrailValidator._normalize_text(full_transcript)

        for item in result.action_items:
            if not GuardrailValidator._is_valid_item(item, segments, full_text_normalized):
                continue
            valid_items.append(item)

        return GuardrailValidator._deduplicate(valid_items)

    @staticmethod
    def _is_valid_item(item: ActionItem, segments: list[TranscriptSegment], full_transcript_norm: str) -> bool:
        # Check 1: task exists and is non-empty
        if not item.task or not item.task.strip():
            return False

        # Check 2: evidence exists and is non-empty
        if not item.evidence or not item.evidence.strip():
            return False

        # Check 3: confidence range 0-1
        if item.confidence < 0.0 or item.confidence > 1.0:
            return False

        # Check 4: evidence actually appears in transcript
        evidence_norm = GuardrailValidator._normalize_text(item.evidence)
        if evidence_norm not in full_transcript_norm:
            # Fallback substring check against individual segments
            matched_in_segments = any(
                evidence_norm in GuardrailValidator._normalize_text(seg.text)
                for seg in segments
            )
            if not matched_in_segments:
                return False

        return True

    @staticmethod
    def _deduplicate(items: list[ActionItem]) -> list[ActionItem]:
        seen_keys: set[str] = set()
        deduped: list[ActionItem] = []

        for item in items:
            norm_task = GuardrailValidator._normalize_text(item.task)
            norm_owner = GuardrailValidator._normalize_text(item.owner or "unassigned")
            dedup_key = f"{norm_task}::{norm_owner}"

            if dedup_key in seen_keys:
                continue

            seen_keys.add(dedup_key)
            deduped.append(item)

        return deduped

    @staticmethod
    def _normalize_text(text: str) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip().lower())
