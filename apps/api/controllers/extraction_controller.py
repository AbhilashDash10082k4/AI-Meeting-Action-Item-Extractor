"""
apps/api/controllers/extraction_controller.py

Purpose:
    Controller class processing HTTP input parameters and formatting endpoint JSON responses.

Working & Flow:
    - Called by FastAPI Routes (`apps/api/routes/extraction_route.py`).
    - Validates file payload input.
    - Delegates core pipeline execution to `ExtractionService`.
    - Returns structured HTTP response payloads.

Links to:
    - src/services/extraction_service.py
    - apps/api/routes/extraction_route.py
"""

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from src.services.extraction_service import ExtractionService


class ExtractionController:
    """Controller handling HTTP request validation and response formatting."""

    def __init__(self, db_session: Session | None = None):
        self.service = ExtractionService(db_session=db_session)

    async def handle_file_upload(self, file: UploadFile) -> dict:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename missing")

        filename = file.filename
        content_bytes = await file.read()

        if not content_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        try:
            transcript_id, segments, action_items = self.service.process_transcript_file(
                filename=filename,
                content_bytes=content_bytes
            )
        except ValueError as err:
            raise HTTPException(status_code=422, detail=str(err))
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"Extraction failed: {str(err)}")

        return {
            "status": "success",
            "transcript_id": transcript_id,
            "filename": filename,
            "segments_count": len(segments),
            "action_items_count": len(action_items),
            "action_items": [item.model_dump(mode="json") for item in action_items],
            "segments": [seg.model_dump(mode="json") for seg in segments]
        }
