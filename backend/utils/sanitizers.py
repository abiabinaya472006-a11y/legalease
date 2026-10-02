"""Input sanitization helpers."""

from __future__ import annotations

import html
import re
from typing import Optional


CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
EXCESS_NEWLINES = re.compile(r"\n{4,}")


def sanitize_text(value: Optional[str], *, max_length: int = 200000) -> str:
    """Remove control characters and normalize whitespace for safe processing."""
    if value is None:
        return ""
    text = str(value)
    text = CONTROL_CHARS.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = EXCESS_NEWLINES.sub("\n\n\n", text)
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    return text


def escape_html(value: str) -> str:
    """HTML-escape user content for safe rendering."""
    return html.escape(sanitize_text(value), quote=True)


def sanitize_filename(name: str, default: str = "document") -> str:
    """Create a filesystem-safe filename stem."""
    cleaned = sanitize_text(name, max_length=100)
    cleaned = re.sub(r"[^\w\s\-]+", "", cleaned, flags=re.UNICODE)
    cleaned = re.sub(r"[\s_]+", "_", cleaned).strip("._")
    return cleaned or default
