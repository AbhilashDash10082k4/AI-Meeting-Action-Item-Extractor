"""
src/extraction/extractor.py

Purpose:
    Executes configurable LLM extraction and a deterministic mock fallback.

Working & Flow:
    - extract_action_items builds the transcript prompt and selects the configured provider.
    - _extract_openai uses the OpenAI SDK for OpenAI-compatible structured JSON.
    - _extract_groq uses the Groq SDK with Groq Structured Outputs.
    - _extract_gemini uses the Google GenAI SDK with a Pydantic JSON schema.
    - _mock_extraction provides deterministic local/test behavior without credentials.
    - All provider results are validated through ExtractionResult before returning.

Links to:
    - src/core/config.py
    - src/extraction/schemas.py
    - src/extraction/prompts.py
    - src/services/extraction_service.py
"""

import json

from openai import OpenAI

from src.core.config import settings
from src.extraction.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.extraction.schemas import ActionItem, ExtractionResult, TranscriptSegment


class LLMExtractor:
    """Executes structured action-item extraction using the configured LLM provider."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.provider = settings.llm_provider
        self.model = model or settings.llm_model
        self.api_key = api_key
        self.client = None

        if self.provider == "openai":
            self.api_key = api_key or settings.openai_api_key
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "groq":
            self.api_key = api_key or settings.groq_api_key
        elif self.provider == "gemini":
            self.api_key = api_key or settings.gemini_api_key

    def extract_action_items(
        self,
        segments: list[TranscriptSegment]
    ) -> ExtractionResult:
        """Extracts action items from transcript segments using the configured provider."""
        if not segments:
            return ExtractionResult(action_items=[])

        if self.provider == "openai" and self.api_key:
            return self._extract_openai(segments)

        if self.provider == "groq" and self.api_key:
            return self._extract_groq(segments)

        if self.provider == "gemini" and self.api_key:
            return self._extract_gemini(segments)

        return self._mock_extraction(segments)

    def _build_prompt(self, segments: list[TranscriptSegment]) -> str:
        """Builds the user prompt payload shared by all LLM providers."""
        segments_payload = [
            {
                "id": seg.id,
                "speaker": seg.speaker,
                "text": seg.text,
                "sequence": seg.sequence
            }
            for seg in segments
        ]
        return USER_PROMPT_TEMPLATE.format(
            segments_json=json.dumps(segments_payload, indent=2)
        )

    def _extract_openai(self, segments: list[TranscriptSegment]) -> ExtractionResult:
        """Calls OpenAI structured output and validates the parsed response."""
        client = self.client or OpenAI(api_key=self.api_key)
        prompt = self._build_prompt(segments)

        response = client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format=ExtractionResult,
            temperature=0.0
        )
        return response.choices[0].message.parsed or ExtractionResult(
            action_items=[]
        )

    def _extract_groq(self, segments: list[TranscriptSegment]) -> ExtractionResult:
        """Calls Groq Structured Outputs using its OpenAI-compatible API."""
        from groq import Groq

        client = Groq(api_key=self.api_key)
        prompt = self._build_prompt(segments)
        schema = ExtractionResult.model_json_schema()

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "meeting_action_items",
                    "strict": False,
                    "schema": schema
                }
            },
            temperature=0.0
        )
        content = response.choices[0].message.content or "{}"
        return ExtractionResult.model_validate_json(content)

    def _extract_gemini(self, segments: list[TranscriptSegment]) -> ExtractionResult:
        """Calls Gemini structured output using the Pydantic extraction schema."""
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        prompt = f"{SYSTEM_PROMPT}\n\n{self._build_prompt(segments)}"
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResult
            )
        )
        return ExtractionResult.model_validate_json(response.text)

    def _mock_extraction(
        self,
        segments: list[TranscriptSegment]
    ) -> ExtractionResult:
        """Creates deterministic candidates for tests and credential-free local execution."""
        action_items: list[ActionItem] = []
        keywords = ["will", "must", "action item", "assigned to", "by next", "deadline"]

        for seg in segments:
            text_lower = seg.text.lower()
            if any(keyword in text_lower for keyword in keywords):
                action_items.append(
                    ActionItem(
                        task=seg.text,
                        owner=None,
                        deadline=None,
                        status="pending",
                        confidence=0.85,
                        evidence=seg.text,
                        source_segment_ids=[seg.id]
                    )
                )

        return ExtractionResult(action_items=action_items)
