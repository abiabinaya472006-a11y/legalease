"""
LegalEase — AI-Powered Legal Document Generator
===============================================

Generate, preview, edit, analyze, translate, and export legal-document drafts
with Google Gemini.

## 1. Project overview

LegalEase is a modular full-stack application:

- **Streamlit** frontend for an approachable drafting workspace
- **FastAPI** REST API for validation, AI calls, and exports
- **Google Gemini** for generation, analysis, summarization, and translation
- **python-docx / FPDF / plain text** for professional downloads

AI output is for **informational and drafting purposes only**. Always review
generated documents with a qualified legal professional where appropriate.

## 2. Features

- Select from 8 legal document types (easy to extend)
- Enter parties, terms, effective dates, jurisdiction, and language
- Generate structured drafts with Gemini
- Preview + edit before export
- Analyze and summarize existing legal text
- Translate while preserving legal structure
- Download **TXT**, **DOCX**, and **PDF**
- Optional logo branding on exports
- Multilingual output: English, Tamil, Hindi, Telugu, Malayalam, Kannada
- Clear legal disclaimers throughout the UI and exports

## 3. Architecture

```
Streamlit Frontend
        ↓
FastAPI REST API
        ↓
Validation Layer (Pydantic)
        ↓
AI Service (ai_core/gemini_generator.py)
        ↓
Gemini API
        ↓
Document Processing
        ↓
DOCX / PDF / TXT Export
```

## 4. Folder structure

```
legalease/
├── ai_core/                  # Gemini prompts, templates, generator
├── assets/                   # logo.png and static branding
├── backend/                  # FastAPI app, models, routes, utils
├── deployment/               # Docker / Procfile
├── document_processing/      # DOCX, PDF, TXT generators
├── frontend/                 # Streamlit UI + API client
├── scripts/                  # Helper scripts (logo creator)
├── tests/                    # Pytest suite
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## 5. Installation

```bash
cd legalease
python -m venv .venv
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/create_logo.py
```

### macOS / Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
python scripts/create_logo.py
```

## 6. Virtual environment setup

Always activate the virtual environment before running backend, frontend, or tests.
This keeps dependencies isolated from your system Python.

## 7. Environment-variable setup

```bash
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
```

Edit `.env` and set:

```
GEMINI_API_KEY=your_real_key_here
BACKEND_API_URL=http://localhost:8000
```

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

**Never commit `.env` or real API keys.**

## 8. Backend startup

From the project root (with venv active):

```bash
uvicorn backend.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 9. Frontend startup

In a **second** terminal (venv active):

```bash
streamlit run frontend/app.py
```

Open the URL Streamlit prints (usually http://localhost:8501).

The backend API URL is configurable in the Streamlit sidebar (`BACKEND_API_URL`).

## 10. API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API status |
| GET | `/health` | Health + Gemini configuration flag |
| POST | `/generate` | Generate a legal-document draft |
| POST | `/analyze` | Analyze pasted legal text |
| POST | `/analyze/upload` | Analyze uploaded `.txt` / `.md` |
| POST | `/summarize` | Plain-language summary |
| POST | `/translate` | Translate content |
| POST | `/export/docx` | Download DOCX |
| POST | `/export/pdf` | Download PDF |
| POST | `/export/txt` | Download TXT |

### Example `POST /generate` body

```json
{
  "document_type": "NDA",
  "parties": ["Alice Corp", "Bob Smith"],
  "terms": "Protect confidential product roadmap for 24 months.",
  "effective_date": "2026-04-01",
  "jurisdiction": "India",
  "language": "English",
  "additional_instructions": "Keep clauses concise."
}
```

## 11. Testing

```bash
pytest
```

Coverage includes:

- API health
- `DocumentRequest` validation
- Generation endpoint (mocked Gemini)
- Empty input rejection
- AI failure / missing API key handling
- DOCX / PDF / TXT generation
- Text sanitization

## 12. Deployment

### Docker Compose

```bash
cd deployment
docker compose up --build
```

- API on port **8000**
- Streamlit on port **8501**

### Single API container

```bash
docker build -f deployment/Dockerfile -t legalease-api .
docker run -p 8000:8000 --env-file .env legalease-api
```

### Platform notes

- Set `GEMINI_API_KEY` as a secret/env var in your host (Render, Railway, Fly.io, etc.)
- Point Streamlit `BACKEND_API_URL` at the public API URL
- Use HTTPS in production and restrict CORS if exposing the API publicly

## 13. Security notes

- Secrets come only from environment variables
- Inputs are validated with Pydantic and sanitized before AI/export use
- Uploads limited by type (`.txt`, `.md`) and size (`MAX_UPLOAD_SIZE_MB`)
- Temporary files are created under `tmp/` and cleaned by TTL
- Generated legal content is not persisted by default
- API keys are never returned in responses or logs intentionally

## 14. Legal disclaimer

LegalEase generates **AI-assisted legal-document drafts** for informational and
drafting purposes. The application:

- does **not** provide legal advice
- does **not** guarantee legal validity, enforceability, or compliance
- does **not** fabricate laws, citations, or authorities by design (and prompts forbid this)
- requires users to verify jurisdiction-specific requirements with qualified professionals

> LegalEase generates AI-assisted legal-document drafts for informational and drafting purposes. Review the document with a qualified legal professional where appropriate.

## Local run commands (quick reference)

```bash
# Terminal 1 — backend
uvicorn backend.main:app --reload

# Terminal 2 — frontend
streamlit run frontend/app.py

# Tests
pytest
```

## Adding a new document type

1. Add a value to `DocumentType` in `backend/models/schemas.py`
2. Add a blueprint entry in `ai_core/templates.py`
3. The UI list in `frontend/components/form.py` should include the new label

## Feature checklist

- [x] Document type selection
- [x] Parties / terms / dates / jurisdiction / language inputs
- [x] Gemini generation
- [x] Preview + edit mode
- [x] Analyze + summarize
- [x] Translate (6 languages)
- [x] TXT / DOCX / PDF export with logo + signatures
- [x] Legal disclaimers
- [x] Modular backend / AI / document processing
- [x] Tests, README, Docker deployment config
"""
