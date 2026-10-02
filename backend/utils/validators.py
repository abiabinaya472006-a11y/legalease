"""Validation helpers beyond Pydantic models."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Set

from backend.config import get_settings
from backend.models.schemas import DocumentType


ALLOWED_TEXT_EXTENSIONS: Set[str] = {".txt", ".md", ".text"}
ALLOWED_UPLOAD_MIME_PREFIXES = ("text/",)


def is_supported_document_type(value: str) -> bool:
    try:
        DocumentType(value)
        return True
    except ValueError:
        return False


def validate_upload_filename(filename: str) -> str:
    """Validate uploaded filename extension."""
    if not filename:
        raise ValueError("Uploaded file must have a name.")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_TEXT_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Allowed: {', '.join(sorted(ALLOWED_TEXT_EXTENSIONS))}."
        )
    return filename


def validate_upload_size(num_bytes: int) -> None:
    settings = get_settings()
    if num_bytes <= 0:
        raise ValueError("Uploaded file is empty.")
    if num_bytes > settings.max_upload_bytes:
        raise ValueError(
            f"File exceeds the maximum size of {settings.max_upload_size_mb} MB."
        )


def ensure_non_empty_lines(values: Iterable[str], field_name: str = "items") -> None:
    items = [v.strip() for v in values if v and str(v).strip()]
    if not items:
        raise ValueError(f"{field_name} cannot be empty.")
