"""Document export routes (DOCX, PDF, TXT)."""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.models.schemas import ErrorResponse, ExportRequest
from backend.utils.sanitizers import sanitize_filename, sanitize_text
from document_processing.docx_generator import generate_docx
from document_processing.pdf_generator import generate_pdf
from document_processing.txt_generator import generate_txt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["export"])


def _prepare(request: ExportRequest) -> ExportRequest:
    request.title = sanitize_text(request.title, max_length=300)
    request.content = sanitize_text(request.content, max_length=200000)
    request.parties = [sanitize_text(p, max_length=200) for p in request.parties if p]
    if request.effective_date:
        request.effective_date = sanitize_text(request.effective_date, max_length=100)
    return request


@router.post(
    "/docx",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def export_docx(request: ExportRequest) -> Response:
    """Generate and download a DOCX file."""
    try:
        req = _prepare(request)
        data = generate_docx(
            title=req.title,
            content=req.content,
            parties=req.parties,
            effective_date=req.effective_date,
            document_type=req.document_type,
            include_logo=req.include_logo,
            include_signature=req.include_signature,
        )
        filename = f"{sanitize_filename(req.title)}.docx"
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("DOCX export failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate DOCX. Please try again.",
        ) from exc


@router.post(
    "/pdf",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def export_pdf(request: ExportRequest) -> Response:
    """Generate and download a PDF file."""
    try:
        req = _prepare(request)
        data = generate_pdf(
            title=req.title,
            content=req.content,
            parties=req.parties,
            effective_date=req.effective_date,
            document_type=req.document_type,
            include_logo=req.include_logo,
            include_signature=req.include_signature,
        )
        filename = f"{sanitize_filename(req.title)}.pdf"
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("PDF export failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF. Please try again.",
        ) from exc


@router.post(
    "/txt",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def export_txt(request: ExportRequest) -> Response:
    """Generate and download a TXT file."""
    try:
        req = _prepare(request)
        data = generate_txt(
            title=req.title,
            content=req.content,
            parties=req.parties,
            effective_date=req.effective_date,
            document_type=req.document_type,
            include_logo=req.include_logo,
            include_signature=req.include_signature,
        )
        filename = f"{sanitize_filename(req.title)}.txt"
        return Response(
            content=data,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("TXT export failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate TXT. Please try again.",
        ) from exc
