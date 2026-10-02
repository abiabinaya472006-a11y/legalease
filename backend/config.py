"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
TEMP_DIR = PROJECT_ROOT / "tmp"


class Settings(BaseSettings):
    """Central settings for LegalEase."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    backend_api_url: str = "http://localhost:8000"

    max_upload_size_mb: int = 5
    temp_file_ttl_seconds: int = 300

    app_name: str = "LegalEase"
    app_version: str = "1.0.0"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key != "your_api_key_here")

    @property
    def logo_path(self) -> Path:
        return ASSETS_DIR / "logo.png"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    return Settings()
