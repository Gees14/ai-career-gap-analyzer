import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.core.config import get_settings
from app.schemas import CVParseResult
from app.services.cv_parser import parse_cv_pdf, parse_cv_text
from app.core.logging import get_logger

router = APIRouter(prefix="/cv", tags=["CV"])
logger = get_logger(__name__)

_ALLOWED_TYPES = {"application/pdf", "text/plain"}
_ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload", response_model=CVParseResult)
async def upload_cv(file: UploadFile = File(...)) -> CVParseResult:
    settings = get_settings()

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Upload a PDF or TXT file.",
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max {settings.max_upload_size_mb} MB.",
        )

    logger.info("CV upload: %s (%.1f KB)", file.filename, len(content) / 1024)

    if ext == ".pdf":
        return parse_cv_pdf(content)
    else:
        return parse_cv_text(content.decode("utf-8", errors="replace"))
