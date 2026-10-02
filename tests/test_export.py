"""Export endpoint and generator tests."""

from fastapi.testclient import TestClient

from backend.main import app
from document_processing.docx_generator import generate_docx
from document_processing.pdf_generator import generate_pdf
from document_processing.txt_generator import generate_txt

client = TestClient(app)

SAMPLE = {
    "title": "Sample NDA",
    "content": (
        "PARTIES\nAlice and Bob\n\n"
        "CONFIDENTIALITY\n- Keep secrets\n- Do not disclose\n\n"
        "TERM\nThis agreement lasts 24 months."
    ),
    "parties": ["Alice", "Bob"],
    "effective_date": "2026-04-01",
    "document_type": "NDA",
    "include_logo": False,
    "include_signature": True,
}


def test_docx_generator_bytes():
    data = generate_docx(**SAMPLE)
    assert isinstance(data, bytes)
    assert len(data) > 1000
    # DOCX files are ZIP packages
    assert data[:2] == b"PK"


def test_pdf_generator_bytes():
    data = generate_pdf(**SAMPLE)
    assert isinstance(data, bytes)
    assert data.startswith(b"%PDF")


def test_txt_generator_bytes():
    data = generate_txt(**SAMPLE)
    text = data.decode("utf-8")
    assert "SAMPLE NDA" in text
    assert "Alice" in text
    assert "LegalEase" in text
    assert "<html>" not in text.lower()


def test_export_docx_endpoint():
    response = client.post("/export/docx", json=SAMPLE)
    assert response.status_code == 200
    assert (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        in response.headers["content-type"]
    )
    assert response.content[:2] == b"PK"


def test_export_pdf_endpoint():
    response = client.post("/export/pdf", json=SAMPLE)
    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
    assert response.content.startswith(b"%PDF")


def test_export_txt_endpoint():
    response = client.post("/export/txt", json=SAMPLE)
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert b"SAMPLE NDA" in response.content


def test_export_empty_content_rejected():
    bad = dict(SAMPLE)
    bad["content"] = "   "
    response = client.post("/export/txt", json=bad)
    assert response.status_code == 422
