"""HTTP client for communicating with the LegalEase FastAPI backend."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests


DEFAULT_BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")


class LegalEaseAPIError(Exception):
    """Raised when the backend returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class LegalEaseClient:
    """Thin REST client used by the Streamlit UI."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 120):
        self.base_url = (base_url or DEFAULT_BACKEND_URL).rstrip("/")
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _handle(self, response: requests.Response) -> Any:
        if response.status_code >= 400:
            detail = None
            try:
                payload = response.json()
                detail = payload.get("detail") or payload.get("error") or payload
            except Exception:  # noqa: BLE001
                detail = response.text
            if isinstance(detail, list):
                # FastAPI validation errors
                messages = []
                for item in detail:
                    loc = ".".join(str(x) for x in item.get("loc", []) if x != "body")
                    msg = item.get("msg", "Invalid input")
                    messages.append(f"{loc}: {msg}" if loc else msg)
                detail = "; ".join(messages)
            raise LegalEaseAPIError(str(detail), status_code=response.status_code)
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.content

    def health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(self._url("/health"), timeout=10)
            return self._handle(resp)
        except requests.ConnectionError as exc:
            raise LegalEaseAPIError(
                "Cannot connect to the backend. Start it with: "
                "uvicorn backend.main:app --reload"
            ) from exc
        except requests.Timeout as exc:
            raise LegalEaseAPIError("Backend health check timed out.") from exc

    def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = requests.post(self._url("/generate"), json=payload, timeout=self.timeout)
            return self._handle(resp)
        except requests.ConnectionError as exc:
            raise LegalEaseAPIError(
                "Cannot reach the LegalEase API. Ensure the backend is running."
            ) from exc
        except requests.Timeout as exc:
            raise LegalEaseAPIError("Document generation timed out. Please try again.") from exc

    def analyze(self, text: str, language: str = "English") -> Dict[str, Any]:
        resp = requests.post(
            self._url("/analyze"),
            json={"text": text, "language": language},
            timeout=self.timeout,
        )
        return self._handle(resp)

    def summarize(self, text: str, language: str = "English") -> Dict[str, Any]:
        resp = requests.post(
            self._url("/summarize"),
            json={"text": text, "language": language},
            timeout=self.timeout,
        )
        return self._handle(resp)

    def translate(
        self,
        text: str,
        target_language: str,
        preserve_structure: bool = True,
    ) -> Dict[str, Any]:
        resp = requests.post(
            self._url("/translate"),
            json={
                "text": text,
                "target_language": target_language,
                "preserve_structure": preserve_structure,
            },
            timeout=self.timeout,
        )
        return self._handle(resp)

    def export(
        self,
        fmt: str,
        title: str,
        content: str,
        parties: Optional[List[str]] = None,
        effective_date: Optional[str] = None,
        document_type: Optional[str] = None,
        include_logo: bool = True,
        include_signature: bool = True,
    ) -> bytes:
        if fmt not in {"docx", "pdf", "txt"}:
            raise LegalEaseAPIError(f"Unsupported export format: {fmt}")
        payload = {
            "title": title,
            "content": content,
            "parties": parties or [],
            "effective_date": effective_date,
            "document_type": document_type,
            "include_logo": include_logo,
            "include_signature": include_signature,
        }
        resp = requests.post(
            self._url(f"/export/{fmt}"),
            json=payload,
            timeout=self.timeout,
        )
        data = self._handle(resp)
        if isinstance(data, bytes):
            return data
        raise LegalEaseAPIError("Export endpoint did not return file bytes.")
