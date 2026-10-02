"""Translation route."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiGenerationError,
    GeminiService,
    get_gemini_service,
)
from backend.models.schemas import ErrorResponse, TranslateRequest, TranslateResponse
from backend.utils.sanitizers import sanitize_text

logger = logging.getLogger(__name__)
router = APIRouter(tags=["translate"])


@router.post(
    "/translate",
    response_model=TranslateResponse,
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def translate_document(
    request: TranslateRequest,
    gemini: GeminiService = Depends(get_gemini_service),
) -> TranslateResponse:
    """Translate generated content into the selected language."""
    text = sanitize_text(request.text, max_length=100000)
    try:
        return gemini.translate_document(
            text,
            request.target_language,
            preserve_structure=request.preserve_structure,
        )
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during translation")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while translating the document.",
        ) from exc
