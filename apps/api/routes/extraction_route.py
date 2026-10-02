"""
apps/api/routes/extraction_route.py

Purpose:
    FastAPI router endpoints for meeting transcript extraction with rate-limiting support.

Working & Flow:
    - Route definition: POST /api/v1/extract.
    - Applies `slowapi` rate limiting decorator.
    - Delegates request lifecycle control directly to `ExtractionController`.

Links to:
    - apps/api/controllers/extraction_controller.py
    - apps/api/main.py
"""

from fastapi import APIRouter, Depends, UploadFile, File, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.database.connection import get_db
from apps.api.controllers.extraction_controller import ExtractionController

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/v1", tags=["Extraction"])


@router.post("/extract")
@limiter.limit("30/minute")
async def extract_action_items(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload transcript file (.txt, .md, .docx, .pdf) and extract validated action items.
    """
    controller = ExtractionController(db_session=db)
    return await controller.handle_file_upload(file)
