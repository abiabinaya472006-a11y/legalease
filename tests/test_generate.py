"""Generation endpoint tests with mocked Gemini service."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiGenerationError,
    get_gemini_service,
)
from backend.main import app
from backend.models.schemas import DocumentResponse, DocumentSection

client = TestClient(app)


VALID_PAYLOAD = {
    "document_type": "NDA",
    "parties": ["Alice Corp", "Bob Smith"],
    "terms": "Protect confidential product roadmap shared during evaluation for 24 months.",
    "effective_date": "2026-04-01",
    "jurisdiction": "India",
    "language": "English",
    "additional_instructions": "Keep clauses concise.",
}


def _mock_response() -> DocumentResponse:
    return DocumentResponse(
        document_type="NDA",
        title="Non-Disclosure Agreement (NDA)",
        parties=["Alice Corp", "Bob Smith"],
        effective_date="2026-04-01",
        jurisdiction="India",
        language="English",
        content=(
            "Non-Disclosure Agreement (NDA)\n\n"
            "PARTIES\nAlice Corp and Bob Smith\n\n"
            "1. Confidential Information\nRoadmap details are confidential.\n\n"
            "ASSUMPTIONS / PLACEHOLDERS\n- Addresses not provided\n\n"
            "DISCLAIMER: LegalEase generates AI-assisted legal-document drafts "
            "for informational and drafting purposes. Review the document with "
            "a qualified legal professional where appropriate."
        ),
        sections=[
            DocumentSection(heading="PARTIES", content="Alice Corp and Bob Smith"),
            DocumentSection(
                heading="Confidential Information",
                content="Roadmap details are confidential.",
            ),
        ],
        assumptions=["Addresses not provided"],
    )


@pytest.fixture
def override_gemini_success():
    mock = MagicMock()
    mock.generate_document.return_value = _mock_response()
    app.dependency_overrides[get_gemini_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_gemini_service, None)


@pytest.fixture
def override_gemini_config_error():
    mock = MagicMock()
    mock.generate_document.side_effect = GeminiConfigurationError("GEMINI_API_KEY is not configured.")
    app.dependency_overrides[get_gemini_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_gemini_service, None)


@pytest.fixture
def override_gemini_failure():
    mock = MagicMock()
    mock.generate_document.side_effect = GeminiGenerationError("empty response")
    app.dependency_overrides[get_gemini_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_gemini_service, None)


def test_generate_success(override_gemini_success):
    response = client.post("/generate", json=VALID_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["document_type"] == "NDA"
    assert "Alice Corp" in data["parties"]
    assert data["content"]
    assert "disclaimer" in data


def test_generate_empty_input():
    response = client.post(
        "/generate",
        json={
            "document_type": "NDA",
            "parties": [],
            "terms": "",
            "effective_date": "",
        },
    )
    assert response.status_code == 422


def test_generate_ai_failure(override_gemini_failure):
    response = client.post("/generate", json=VALID_PAYLOAD)
    assert response.status_code == 502
    assert "detail" in response.json()


def test_generate_missing_api_key(override_gemini_config_error):
    response = client.post("/generate", json=VALID_PAYLOAD)
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]


def test_unsupported_document_type():
    payload = dict(VALID_PAYLOAD)
    payload["document_type"] = "Will and Testament"
    response = client.post("/generate", json=payload)
    assert response.status_code == 422
