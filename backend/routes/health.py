"""Health and status routes."""

from fastapi import APIRouter

from backend.config import get_settings
from backend.models.schemas import HealthResponse, StatusResponse
from backend.utils.temp_files import cleanup_stale_temp_files

router = APIRouter(tags=["health"])


@router.get("/", response_model=StatusResponse)
async def root_status() -> StatusResponse:
    """Return API status."""
    settings = get_settings()
    return StatusResponse(
        status="ok",
        service="LegalEase API",
        version=settings.app_version,
        message="LegalEase AI-Powered Legal Document Generator is running.",
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health including Gemini configuration status."""
    settings = get_settings()
    cleaned = cleanup_stale_temp_files()
    return HealthResponse(
        status="healthy" if settings.has_gemini_key else "degraded",
        gemini_configured=settings.has_gemini_key,
        details={
            "app": settings.app_name,
            "version": settings.app_version,
            "model": settings.gemini_model if settings.has_gemini_key else None,
            "temp_files_cleaned": cleaned,
            "message": (
                "All systems operational."
                if settings.has_gemini_key
                else "GEMINI_API_KEY is not configured. Generation endpoints will fail until set."
            ),
        },
    )
