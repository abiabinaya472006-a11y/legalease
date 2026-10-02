"""LegalEase FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.models.schemas import ErrorResponse
from backend.routes import analyze, export, generate, health, summarize, translate
from backend.utils.temp_files import cleanup_stale_temp_files, ensure_temp_dir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("legalease")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    ensure_temp_dir()
    cleanup_stale_temp_files()
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    if not settings.has_gemini_key:
        logger.warning("GEMINI_API_KEY is not configured — AI endpoints will return 503.")
    yield
    cleanup_stale_temp_files()
    logger.info("LegalEase API shutdown complete.")


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="LegalEase API",
        description=(
            "AI-Powered Legal Document Generator. "
            "Generates AI-assisted drafts for informational and drafting purposes. "
            "Review documents with a qualified legal professional where appropriate."
        ),
        version=settings.app_version,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router)
    application.include_router(generate.router)
    application.include_router(analyze.router)
    application.include_router(summarize.router)
    application.include_router(translate.router)
    application.include_router(export.router)

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        # Never expose secrets or stack traces to clients
        payload = ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred. Please try again later.",
            code="internal_error",
        )
        return JSONResponse(status_code=500, content=payload.model_dump())

    return application


app = create_app()
