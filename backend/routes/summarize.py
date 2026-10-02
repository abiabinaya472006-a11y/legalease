"""Summarization route."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiGenerationError,
    GeminiService,
    get_gemini_service,
)
from backend.models.schemas import ErrorResponse, SummarizeRequest, SummarizeResponse
from backend.utils.sanitizers import sanitize_text

logger = logging.getLogger(__name__)
router = APIRouter(tags=["summarize"])


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def summarize_document(
    request: SummarizeRequest,
    gemini: GeminiService = Depends(get_gemini_service),
) -> SummarizeResponse:
    """Generate a plain-language summary of legal text."""
    text = sanitize_text(request.text, max_length=100000)
    try:
        return gemini.summarize_document(text, request.language)
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during summarization")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while summarizing the document.",
        ) from exc
