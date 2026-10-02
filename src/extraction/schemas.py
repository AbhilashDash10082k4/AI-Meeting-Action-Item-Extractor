"""
src/extraction/schemas.py

Purpose:
    Defines Pydantic models for transcript segments, extracted action items, and extraction result containers.

Working & Flow:
    - TranscriptSegment: Represents indexed transcript chunk with speaker/text metadata.
    - ActionItem: Strictly validated action item payload extracted from LLM.
    - ExtractionResult: Wrapper contract containing extracted action items.

Links to:
    - src/preprocessing/chunker.py
    - src/extraction/extractor.py
    - src/validation/validator.py
    - apps/api/controllers/extraction_controller.py
"""

from datetime import date
from typing import Literal
from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    id: str
    speaker: str | None = None
    text: str
    sequence: int
    start_time: float | None = None
    end_time: float | None = None


class ActionItem(BaseModel):
    task: str = Field(..., description="Action item description")
    owner: str | None = Field(default=None, description="Assigned owner name or null")
    deadline: date | None = Field(default=None, description="ISO date YYYY-MM-DD or null")
    status: Literal[
        "pending",
        "in_progress",
        "completed",
        "cancelled",
        "unknown"
    ] = Field(default="pending", description="Task commitment status")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0 to 1.0")
    evidence: str = Field(..., description="Exact quote from transcript supporting this task")
    source_segment_ids: list[str] = Field(default_factory=list, description="IDs of backing transcript segments")


class ExtractionResult(BaseModel):
    action_items: list[ActionItem] = Field(default_factory=list)
