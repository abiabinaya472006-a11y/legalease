"""Document generation route."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiGenerationError,
    GeminiService,
    get_gemini_service,
)
from backend.models.schemas import DocumentRequest, DocumentResponse, ErrorResponse
from backend.utils.sanitizers import sanitize_text

logger = logging.getLogger(__name__)
router = APIRouter(tags=["generate"])


@router.post(
    "/generate",
    response_model=DocumentResponse,
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def generate_document(
    request: DocumentRequest,
    gemini: GeminiService = Depends(get_gemini_service),
) -> DocumentResponse:
    """Generate a legal-document draft using Google Gemini."""
    # Sanitize free-text fields before prompting
    request.terms = sanitize_text(request.terms, max_length=20000)
    if request.additional_instructions:
        request.additional_instructions = sanitize_text(
            request.additional_instructions, max_length=5000
        )
    request.jurisdiction = sanitize_text(request.jurisdiction, max_length=200)

    try:
        return gemini.generate_document(request)
    except GeminiConfigurationError as exc:
        logger.error("Gemini configuration error during generate")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiGenerationError as exc:
        logger.error("Gemini generation error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during document generation")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating the document.",
        ) from exc
