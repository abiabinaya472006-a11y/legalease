"""Pydantic request/response schemas for LegalEase API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class DocumentType(str, Enum):
    """Supported legal document types. Extend this enum to add templates."""

    EMPLOYMENT_CONTRACT = "Employment Contract"
    NDA = "NDA"
    LEASE_AGREEMENT = "Lease Agreement"
    FREELANCE_AGREEMENT = "Freelance Agreement"
    SERVICE_AGREEMENT = "Service Agreement"
    OFFER_LETTER = "Offer Letter"
    PARTNERSHIP_AGREEMENT = "Partnership Agreement"
    GENERAL_AGREEMENT = "General Agreement"


class Language(str, Enum):
    """Supported output languages."""

    ENGLISH = "English"
    TAMIL = "Tamil"
    HINDI = "Hindi"
    TELUGU = "Telugu"
    MALAYALAM = "Malayalam"
    KANNADA = "Kannada"


class DocumentRequest(BaseModel):
    """Request body for generating a legal-document draft."""

    document_type: DocumentType = Field(
        ...,
        description="Type of legal document to generate",
    )
    parties: List[str] = Field(
        ...,
        min_length=1,
        description="Names of parties involved (at least one required)",
        examples=[["Alice Corp", "Bob Smith"]],
    )
    terms: str = Field(
        ...,
        min_length=10,
        description="Terms and conditions for the document",
    )
    effective_date: str = Field(
        ...,
        min_length=4,
        description="Effective date of the agreement (YYYY-MM-DD preferred)",
    )
    jurisdiction: str = Field(
        default="Not specified",
        description="Governing jurisdiction / location",
    )
    language: Language = Field(
        default=Language.ENGLISH,
        description="Output language for the generated document",
    )
    additional_instructions: Optional[str] = Field(
        default=None,
        description="Optional extra drafting instructions",
    )

    @field_validator("parties")
    @classmethod
    def validate_parties(cls, value: List[str]) -> List[str]:
        cleaned = [p.strip() for p in value if p and p.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty party name is required.")
        if len(cleaned) > 20:
            raise ValueError("A maximum of 20 parties is allowed.")
        for party in cleaned:
            if len(party) > 200:
                raise ValueError("Each party name must be 200 characters or fewer.")
        return cleaned

    @field_validator("terms")
    @classmethod
    def validate_terms(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("Terms must be at least 10 characters long.")
        if len(cleaned) > 20000:
            raise ValueError("Terms must be 20,000 characters or fewer.")
        return cleaned

    @field_validator("effective_date")
    @classmethod
    def validate_effective_date(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Effective date is required.")
        # Accept ISO dates or free-form readable dates; validate ISO when possible.
        try:
            date.fromisoformat(cleaned)
        except ValueError:
            if len(cleaned) < 4:
                raise ValueError(
                    "Provide a valid effective date (YYYY-MM-DD or a readable date)."
                )
        return cleaned

    @field_validator("jurisdiction")
    @classmethod
    def validate_jurisdiction(cls, value: str) -> str:
        cleaned = (value or "Not specified").strip()
        if len(cleaned) > 200:
            raise ValueError("Jurisdiction must be 200 characters or fewer.")
        return cleaned or "Not specified"

    @field_validator("additional_instructions")
    @classmethod
    def validate_instructions(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if len(cleaned) > 5000:
            raise ValueError("Additional instructions must be 5,000 characters or fewer.")
        return cleaned


class DocumentSection(BaseModel):
    """A single section within a generated document."""

    heading: str
    content: str


class DocumentResponse(BaseModel):
    """Response containing a generated legal-document draft."""

    success: bool = True
    document_type: str
    title: str
    parties: List[str]
    effective_date: str
    jurisdiction: str
    language: str
    content: str
    sections: List[DocumentSection] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "LegalEase generates AI-assisted legal-document drafts for informational "
        "and drafting purposes. Review the document with a qualified legal "
        "professional where appropriate."
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyzeRequest(BaseModel):
    """Request body for analyzing legal-document text."""

    text: str = Field(..., min_length=20, description="Legal document text to analyze")
    language: Language = Field(default=Language.ENGLISH)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 20:
            raise ValueError("Document text must be at least 20 characters.")
        if len(cleaned) > 100000:
            raise ValueError("Document text must be 100,000 characters or fewer.")
        return cleaned


class AnalyzeResponse(BaseModel):
    """Structured analysis of a legal document."""

    success: bool = True
    document_type: Optional[str] = None
    parties: List[str] = Field(default_factory=list)
    important_dates: List[str] = Field(default_factory=list)
    key_clauses: List[str] = Field(default_factory=list)
    obligations: List[str] = Field(default_factory=list)
    payment_terms: List[str] = Field(default_factory=list)
    termination_clauses: List[str] = Field(default_factory=list)
    confidentiality_clauses: List[str] = Field(default_factory=list)
    important_conditions: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    raw_analysis: str = ""
    disclaimer: str = (
        "This analysis is AI-assisted and informational only. It does not "
        "determine legal validity, enforceability, or compliance."
    )


class SummarizeRequest(BaseModel):
    """Request body for plain-language summarization."""

    text: str = Field(..., min_length=20)
    language: Language = Field(default=Language.ENGLISH)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 20:
            raise ValueError("Text must be at least 20 characters.")
        if len(cleaned) > 100000:
            raise ValueError("Text must be 100,000 characters or fewer.")
        return cleaned


class SummarizeResponse(BaseModel):
    """Plain-language summary response."""

    success: bool = True
    summary: str
    language: str
    disclaimer: str = (
        "This summary is AI-assisted and for informational purposes only. "
        "It is not legal advice."
    )


class TranslateRequest(BaseModel):
    """Request body for translating document content."""

    text: str = Field(..., min_length=1)
    target_language: Language
    preserve_structure: bool = True

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Text to translate cannot be empty.")
        if len(cleaned) > 100000:
            raise ValueError("Text must be 100,000 characters or fewer.")
        return cleaned


class TranslateResponse(BaseModel):
    """Translated document content."""

    success: bool = True
    original_language_hint: Optional[str] = None
    target_language: str
    translated_text: str
    disclaimer: str = (
        "Translations are AI-assisted. Have translated legal content reviewed "
        "by a qualified professional familiar with the target language and jurisdiction."
    )


class ExportRequest(BaseModel):
    """Request body for exporting a document."""

    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    parties: List[str] = Field(default_factory=list)
    effective_date: Optional[str] = None
    document_type: Optional[str] = None
    include_logo: bool = True
    include_signature: bool = True

    @field_validator("title", "content")
    @classmethod
    def strip_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty.")
        return cleaned

    @model_validator(mode="after")
    def validate_content_length(self) -> "ExportRequest":
        if len(self.content) > 200000:
            raise ValueError("Content is too large to export.")
        return self


class StatusResponse(BaseModel):
    """API root status payload."""

    status: str = "ok"
    service: str = "LegalEase API"
    version: str = "1.0.0"
    message: str = "LegalEase AI-Powered Legal Document Generator is running."


class HealthResponse(BaseModel):
    """Health check payload."""

    status: str
    gemini_configured: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error payload."""

    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
