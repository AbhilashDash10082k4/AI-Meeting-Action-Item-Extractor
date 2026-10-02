# Feature Specification: AI Meeting Action-Item Extraction

## Current State
- Supports transcript file parsing (`.txt`, `.md`, `.docx`, `.pdf`).
- Segment-based preprocessing & line indexing.
- LLM-based structured action item extraction (`task`, `owner`, `deadline`, `status`, `confidence`, `evidence`, `source_segment_ids`).
- Deterministic guardrail validation & deduplication.
- Architecture: Streamlit UI -> FastAPI Route -> Controller -> Service -> Repository -> PostgreSQL.

## Data Flow
1. User uploads transcript via Streamlit UI.
2. UI POSTs file to API route `/api/v1/extract`.
3. Route delegates request to Controller (`ExtractionController`).
4. Controller invokes `ExtractionService`.
5. `ExtractionService` executes pipeline:
   - `IngestionParser`: Extracts raw text from file.
   - `TranscriptPreprocessor`: Converts raw text into indexed `TranscriptSegment` objects.
   - `LLMExtractor`: Invokes OpenAI structured output JSON mode with strict prompts.
   - `GuardrailValidator`: Deterministically verifies task presence, deadline validity, exact quote evidence match against segments, confidence limits `[0.0, 1.0]`, and deduplicates tasks.
   - `ActionItemRepository`: Persists raw transcript and validated action items into PostgreSQL via SQLAlchemy ORM.
6. Controller formats JSON response and sends back to Streamlit UI for interactive display.

## Future Improvements
- Multi-language transcript support and dynamic translation.
- Automated calendar invitation generation for extracted deadlines.
- Real-time streaming audio transcript processing.
