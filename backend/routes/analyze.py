"""Document analysis route."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiGenerationError,
    GeminiService,
    get_gemini_service,
)
from backend.models.schemas import AnalyzeRequest, AnalyzeResponse, ErrorResponse, Language
from backend.utils.sanitizers import sanitize_text
from backend.utils.validators import validate_upload_filename, validate_upload_size

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analyze"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def analyze_document(
    request: AnalyzeRequest,
    gemini: GeminiService = Depends(get_gemini_service),
) -> AnalyzeResponse:
    """Analyze pasted legal-document text."""
    text = sanitize_text(request.text, max_length=100000)
    try:
        return gemini.analyze_document(text, request.language)
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during analysis")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing the document.",
        ) from exc


@router.post(
    "/analyze/upload",
    response_model=AnalyzeResponse,
    responses={400: {"model": ErrorResponse}},
)
async def analyze_uploaded_document(
    file: UploadFile = File(...),
    language: Language = Language.ENGLISH,
    gemini: GeminiService = Depends(get_gemini_service),
) -> AnalyzeResponse:
    """Analyze an uploaded plain-text legal document."""
    try:
        validate_upload_filename(file.filename or "")
        raw = await file.read()
        validate_upload_size(len(raw))
        text = sanitize_text(raw.decode("utf-8", errors="replace"), max_length=100000)
        if len(text) < 20:
            raise ValueError("Uploaded file does not contain enough text to analyze.")
        return gemini.analyze_document(text, language)
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not decode the uploaded file as UTF-8 text.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("File analysis failed")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the uploaded file.",
        ) from exc
