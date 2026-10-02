"""DocumentRequest validation tests."""

import pytest
from pydantic import ValidationError

from backend.models.schemas import DocumentRequest, DocumentType, Language


def test_valid_document_request():
    req = DocumentRequest(
        document_type=DocumentType.NDA,
        parties=["Alice", "Bob"],
        terms="Confidential information must not be disclosed for two years.",
        effective_date="2026-01-15",
        jurisdiction="India",
        language=Language.ENGLISH,
    )
    assert req.document_type == DocumentType.NDA
    assert len(req.parties) == 2


def test_empty_parties_rejected():
    with pytest.raises(ValidationError) as exc:
        DocumentRequest(
            document_type=DocumentType.NDA,
            parties=["  ", ""],
            terms="Confidential information must not be disclosed for two years.",
            effective_date="2026-01-15",
        )
    assert "party" in str(exc.value).lower()


def test_short_terms_rejected():
    with pytest.raises(ValidationError):
        DocumentRequest(
            document_type=DocumentType.SERVICE_AGREEMENT,
            parties=["Acme"],
            terms="Too short",
            effective_date="2026-01-15",
        )


def test_missing_effective_date_rejected():
    with pytest.raises(ValidationError):
        DocumentRequest(
            document_type=DocumentType.OFFER_LETTER,
            parties=["Acme", "Jordan"],
            terms="Role: Engineer. Salary: 100000. Start date next month.",
            effective_date="   ",
        )


def test_party_name_too_long_rejected():
    with pytest.raises(ValidationError):
        DocumentRequest(
            document_type=DocumentType.GENERAL_AGREEMENT,
            parties=["A" * 201],
            terms="General collaboration terms spanning several sentences here.",
            effective_date="15 January 2026",
        )


def test_whitespace_parties_trimmed():
    req = DocumentRequest(
        document_type=DocumentType.FREELANCE_AGREEMENT,
        parties=["  Alice  ", "Bob"],
        terms="Deliver website redesign within 30 days for fixed fee.",
        effective_date="2026-03-01",
    )
    assert req.parties[0] == "Alice"
