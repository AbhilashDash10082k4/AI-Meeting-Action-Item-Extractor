"""
src/extraction/extractor.py

Purpose:
    LLM structured output caller invoking OpenAI API (or mock fallback) for action item extraction.

Working & Flow:
    - `extract_action_items(segments)` formats transcript segments into prompt payload.
    - Invokes OpenAI structured completion using `ExtractionResult` Pydantic model.
    - Returns `ExtractionResult` object containing candidate action items.

Links to:
    - src/extraction/schemas.py
    - src/extraction/prompts.py
    - src/core/config.py
    - src/validation/validator.py
"""

import json
from openai import OpenAI
from src.core.config import settings
from src.extraction.schemas import TranscriptSegment, ExtractionResult, ActionItem
from src.extraction.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class LLMExtractor:
    """Executes structured LLM calls to extract candidate action items from transcript segments."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.llm_model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def extract_action_items(self, segments: list[TranscriptSegment]) -> ExtractionResult:
        if not segments:
            return ExtractionResult(action_items=[])

        if not self.client:
            # Fallback mock engine if no API key is provided for test environment
            return self._mock_extraction(segments)

        segments_payload = [
            {
                "id": seg.id,
                "speaker": seg.speaker,
                "text": seg.text,
                "sequence": seg.sequence
            }
            for seg in segments
        ]

        user_prompt = USER_PROMPT_TEMPLATE.format(
            segments_json=json.dumps(segments_payload, indent=2)
        )

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=ExtractionResult,
                temperature=0.0
            )
            return response.choices[0].message.parsed or ExtractionResult(action_items=[])
        except Exception:
            # Fallback to json mode if beta parsing endpoint fails
            return self._extract_json_mode(user_prompt)

    def _extract_json_mode(self, user_prompt: str) -> ExtractionResult:
        if not self.client:
            return ExtractionResult(action_items=[])
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\nRespond strictly in valid JSON matching key 'action_items'."},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return ExtractionResult.model_validate(data)

    def _mock_extraction(self, segments: list[TranscriptSegment]) -> ExtractionResult:
        """Deterministic mock rule for local execution when no OpenAI API key is set."""
        action_items: list[ActionItem] = []
        keywords = ["will", "must", "action item", "assigned to", "by next", "deadline"]

        for seg in segments:
            text_lower = seg.text.lower()
            if any(kw in text_lower for kw in keywords):
                action_items.append(
                    ActionItem(
                        task=seg.text,
                        owner=seg.speaker or "Unassigned",
                        deadline=None,
                        status="pending",
                        confidence=0.85,
                        evidence=seg.text,
                        source_segment_ids=[seg.id]
                    )
                )
        return ExtractionResult(action_items=action_items)
