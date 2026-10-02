"""Reusable Google Gemini service for LegalEase."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from backend.config import get_settings
from backend.models.schemas import (
    AnalyzeResponse,
    DocumentRequest,
    DocumentResponse,
    DocumentSection,
    Language,
    SummarizeResponse,
    TranslateResponse,
)
from ai_core.prompts import (
    build_analysis_prompt,
    build_generation_prompt,
    build_summary_prompt,
    build_translate_prompt,
)
from ai_core.templates import get_template

logger = logging.getLogger(__name__)


class GeminiConfigurationError(Exception):
    """Raised when Gemini API key is missing or invalid."""


class GeminiGenerationError(Exception):
    """Raised when Gemini API call fails or returns empty content."""


class GeminiService:
    """Thin wrapper around the Google Generative AI SDK."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model
        self._model = None

    def _ensure_client(self) -> None:
        if not self.api_key or self.api_key == "your_api_key_here":
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is not configured. Copy .env.example to .env "
                "and set a valid Google Gemini API key."
            )
        if self._model is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to initialize Gemini client")
                raise GeminiConfigurationError(
                    "Unable to initialize Gemini client. Check the API key and package installation."
                ) from exc

    def generate_text(self, prompt: str, *, temperature: float = 0.3) -> str:
        """Send a prompt to Gemini and return cleaned text."""
        self._ensure_client()
        try:
            response = self._model.generate_content(  # type: ignore[union-attr]
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 8192,
                },
            )
        except GeminiConfigurationError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("Gemini API call failed")
            raise GeminiGenerationError(
                "The AI service failed to generate a response. Please try again shortly."
            ) from exc

        text = self._extract_text(response)
        if not text:
            raise GeminiGenerationError(
                "The AI service returned an empty response. Please refine your inputs and try again."
            )
        return text.strip()

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Safely extract text from a Gemini response object."""
        try:
            if hasattr(response, "text") and response.text:
                return str(response.text)
        except Exception:  # noqa: BLE001
            pass

        parts: List[str] = []
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                part_text = getattr(part, "text", None)
                if part_text:
                    parts.append(str(part_text))
        return "\n".join(parts).strip()

    def generate_document(self, request: DocumentRequest) -> DocumentResponse:
        """Generate a structured legal-document draft."""
        template = get_template(request.document_type)
        prompt = build_generation_prompt(request)
        content = self.generate_text(prompt, temperature=0.25)
        sections = parse_sections(content)
        assumptions = extract_assumptions(content)
        title = extract_title(content) or str(template["title"])

        return DocumentResponse(
            success=True,
            document_type=request.document_type.value,
            title=title,
            parties=request.parties,
            effective_date=request.effective_date,
            jurisdiction=request.jurisdiction,
            language=request.language.value,
            content=content,
            sections=sections,
            assumptions=assumptions,
        )

    def analyze_document(self, text: str, language: Language) -> AnalyzeResponse:
        """Analyze pasted/uploaded legal document text."""
        prompt = build_analysis_prompt(text, language)
        raw = self.generate_text(prompt, temperature=0.2)
        parsed = parse_analysis(raw)
        return AnalyzeResponse(
            success=True,
            document_type=parsed.get("document_type"),
            parties=parsed.get("parties", []),
            important_dates=parsed.get("important_dates", []),
            key_clauses=parsed.get("key_clauses", []),
            obligations=parsed.get("obligations", []),
            payment_terms=parsed.get("payment_terms", []),
            termination_clauses=parsed.get("termination_clauses", []),
            confidentiality_clauses=parsed.get("confidentiality_clauses", []),
            important_conditions=parsed.get("important_conditions", []),
            missing_information=parsed.get("missing_information", []),
            raw_analysis=raw,
        )

    def summarize_document(self, text: str, language: Language) -> SummarizeResponse:
        """Produce a plain-language summary."""
        prompt = build_summary_prompt(text, language)
        summary = self.generate_text(prompt, temperature=0.2)
        return SummarizeResponse(
            success=True,
            summary=summary,
            language=language.value,
        )

    def translate_document(
        self,
        text: str,
        target_language: Language,
        preserve_structure: bool = True,
    ) -> TranslateResponse:
        """Translate document content while preserving structure."""
        prompt = build_translate_prompt(text, target_language, preserve_structure)
        translated = self.generate_text(prompt, temperature=0.2)
        return TranslateResponse(
            success=True,
            target_language=target_language.value,
            translated_text=translated,
        )


def extract_title(content: str) -> Optional[str]:
    """Extract the first meaningful non-empty line as a title."""
    for line in content.splitlines():
        cleaned = line.strip().strip("#").strip()
        if cleaned and len(cleaned) < 200:
            lower = cleaned.lower()
            if lower.startswith("disclaimer"):
                continue
            return cleaned
    return None


def parse_sections(content: str) -> List[DocumentSection]:
    """Parse heading/content pairs from generated text."""
    sections: List[DocumentSection] = []
    # Match markdown headings or ALL-CAPS / numbered headings
    pattern = re.compile(
        r"^(?:#{1,3}\s+|\d+[\.\)]\s+)?([A-Z][A-Za-z0-9 &\-/()]{2,80})\s*$",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(content))
    if not matches:
        if content.strip():
            sections.append(DocumentSection(heading="Document Body", content=content.strip()))
        return sections

    for idx, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        body = content[start:end].strip()
        if heading.lower().startswith("disclaimer"):
            continue
        sections.append(DocumentSection(heading=heading, content=body))
    return sections


def extract_assumptions(content: str) -> List[str]:
    """Pull assumption/placeholder bullets from generated content."""
    assumptions: List[str] = []
    lower = content.lower()
    markers = ["assumptions / placeholders", "assumptions", "placeholders"]
    start_idx = -1
    for marker in markers:
        pos = lower.find(marker)
        if pos != -1:
            start_idx = pos
            break
    if start_idx == -1:
        return assumptions

    chunk = content[start_idx:]
    for line in chunk.splitlines()[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith("disclaimer"):
            break
        if re.match(r"^(#{1,3}|\d+[\.\)])\s+[A-Z]", stripped):
            # Next major heading
            if "assumption" not in stripped.lower() and "placeholder" not in stripped.lower():
                break
        bullet = re.sub(r"^[-*•\d\.\)\s]+", "", stripped).strip()
        if bullet:
            assumptions.append(bullet)
    return assumptions[:30]


def parse_analysis(raw: str) -> Dict[str, Any]:
    """Parse analysis headings into structured fields."""
    mapping = {
        "document type": "document_type",
        "parties": "parties",
        "important dates": "important_dates",
        "key clauses": "key_clauses",
        "obligations": "obligations",
        "payment terms": "payment_terms",
        "termination clauses": "termination_clauses",
        "confidentiality clauses": "confidentiality_clauses",
        "potentially important conditions": "important_conditions",
        "important conditions": "important_conditions",
        "missing information": "missing_information",
    }

    result: Dict[str, Any] = {v: [] for v in mapping.values() if v != "document_type"}
    result["document_type"] = None

    current_key: Optional[str] = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        heading_match = re.match(r"^(?:\d+[\.\)]\s*)?([A-Za-z ]+?)\s*:?\s*$", stripped)
        normalized = None
        if heading_match:
            candidate = heading_match.group(1).strip().lower()
            if candidate in mapping:
                normalized = mapping[candidate]
                current_key = normalized
                continue

        # Inline "Heading: value"
        inline = re.match(r"^(?:\d+[\.\)]\s*)?([A-Za-z ]+?)\s*:\s*(.+)$", stripped)
        if inline:
            candidate = inline.group(1).strip().lower()
            if candidate in mapping:
                key = mapping[candidate]
                value = inline.group(2).strip()
                if key == "document_type":
                    result["document_type"] = value
                else:
                    result[key].append(value)
                current_key = key
                continue

        if current_key:
            bullet = re.sub(r"^[-*•\d\.\)\s]+", "", stripped).strip()
            if not bullet:
                continue
            if current_key == "document_type":
                result["document_type"] = bullet
            else:
                result[current_key].append(bullet)

    return result


def get_gemini_service() -> GeminiService:
    """Factory for dependency injection."""
    return GeminiService()
