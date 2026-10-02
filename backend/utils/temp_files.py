"""Safe temporary-file helpers with automatic cleanup."""

from __future__ import annotations

import logging
import tempfile
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator, Optional

from backend.config import TEMP_DIR, get_settings

logger = logging.getLogger(__name__)


def ensure_temp_dir() -> Path:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_DIR


def create_temp_path(suffix: str = ".tmp", prefix: str = "legalease_") -> Path:
    """Create a unique temporary file path under the project tmp directory."""
    ensure_temp_dir()
    name = f"{prefix}{uuid.uuid4().hex}{suffix}"
    return TEMP_DIR / name


@contextmanager
def temporary_file(
    suffix: str = ".tmp",
    prefix: str = "legalease_",
    content: Optional[bytes] = None,
) -> Generator[Path, None, None]:
    """Yield a temp file path and delete it afterward."""
    path = create_temp_path(suffix=suffix, prefix=prefix)
    try:
        if content is not None:
            path.write_bytes(content)
        yield path
    finally:
        cleanup_path(path)


def cleanup_path(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        logger.warning("Failed to delete temporary file: %s", path)


def cleanup_stale_temp_files(max_age_seconds: Optional[int] = None) -> int:
    """Remove temp files older than TTL. Returns count deleted."""
    settings = get_settings()
    ttl = max_age_seconds if max_age_seconds is not None else settings.temp_file_ttl_seconds
    ensure_temp_dir()
    now = time.time()
    deleted = 0
    for path in TEMP_DIR.glob("legalease_*"):
        try:
            age = now - path.stat().st_mtime
            if age > ttl:
                path.unlink()
                deleted += 1
        except OSError:
            logger.warning("Could not clean temp file: %s", path)
    return deleted


@contextmanager
def named_temp_bytes(suffix: str) -> Iterator[tempfile.NamedTemporaryFile]:
    """Context manager around a NamedTemporaryFile deleted on close."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=str(ensure_temp_dir()))
    try:
        yield tmp
    finally:
        try:
            tmp.close()
        except Exception:  # noqa: BLE001
            pass
        cleanup_path(Path(tmp.name))
