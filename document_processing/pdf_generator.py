"""PDF export using FPDF2."""

from __future__ import annotations

import logging
import re
from io import BytesIO
from typing import List, Optional

from fpdf import FPDF

from backend.config import get_settings
from backend.utils.sanitizers import sanitize_text
from document_processing.formatter import DISCLAIMER, build_footer_text

logger = logging.getLogger(__name__)


def _pdf_safe(text: str) -> str:
    """Convert text to characters safe for Helvetica core fonts."""
    if not text:
        return ""
    replacements = {
        "\u2014": "-",  # em dash
        "\u2013": "-",  # en dash
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    # Drop remaining non-latin1 characters rather than crashing export
    return text.encode("latin-1", errors="replace").decode("latin-1")


class LegalEasePDF(FPDF):
    """Custom PDF with header/footer and page numbers."""

    def __init__(self, include_logo: bool = True):
        super().__init__()
        self.include_logo = include_logo
        self.settings = get_settings()

    def header(self) -> None:
        if self.include_logo:
            logo = self.settings.logo_path
            if logo.exists():
                try:
                    self.image(str(logo), x=10, y=8, w=18)
                except Exception:  # noqa: BLE001
                    logger.warning("Could not embed logo into PDF")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(90, 90, 90)
        self.cell(
            0,
            8,
            _pdf_safe("LegalEase - AI-Powered Legal Document Generator"),
            align="R",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(4)
        self.set_draw_color(40, 60, 90)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-18)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, _pdf_safe(build_footer_text()), align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R")


def generate_pdf(
    title: str,
    content: str,
    parties: Optional[List[str]] = None,
    effective_date: Optional[str] = None,
    document_type: Optional[str] = None,
    include_logo: bool = True,
    include_signature: bool = True,
) -> bytes:
    """Generate a PDF document and return raw bytes."""
    parties = [_pdf_safe(p) for p in (parties or [])]
    title = _pdf_safe(sanitize_text(title, max_length=300))
    content = _pdf_safe(sanitize_text(content))
    document_type = _pdf_safe(document_type or "")
    effective_date = _pdf_safe(effective_date or "")

    pdf = LegalEasePDF(include_logo=include_logo)
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.add_page()

    def writeln(text: str, height: float = 6, align: str = "L") -> None:
        """Write a wrapping line and always return to the left margin."""
        pdf.multi_cell(
            0,
            height,
            text,
            align=align,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 35, 60)
    writeln(title.upper(), height=9, align="C")
    pdf.ln(2)

    if document_type:
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(70, 70, 70)
        writeln(document_type, align="C")
        pdf.ln(2)

    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 11)

    if parties:
        writeln(f"Parties: {', '.join(parties)}")

    if effective_date:
        writeln(f"Effective Date: {effective_date}")

    pdf.ln(4)

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            pdf.ln(3)
            continue

        # Headings
        if (
            (stripped.isupper() and len(stripped) < 90)
            or stripped.startswith("#")
            or (stripped.endswith(":") and len(stripped) < 90)
        ):
            heading = stripped.lstrip("#").strip().rstrip(":")
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(20, 35, 60)
            writeln(heading, height=7)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)
            continue

        # Bullets
        bullet_match = re.match(r"^[-*•]\s+(.*)$", stripped)
        number_match = re.match(r"^(\d+[\.\)])\s+(.*)$", stripped)
        if bullet_match:
            writeln(f"    - {bullet_match.group(1)}")
        elif number_match:
            writeln(f"    {number_match.group(1)} {number_match.group(2)}")
        else:
            writeln(stripped)

    if include_signature and "signature" not in content.lower():
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 12)
        writeln("SIGNATURES", height=7)
        pdf.set_font("Helvetica", "", 11)
        for party in parties or ["Party A", "Party B"]:
            pdf.ln(3)
            writeln(f"For {party}:")
            writeln("Signature: _______________________________")
            writeln("Name: ____________________________________")
            writeln("Date: ____________________________________")

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(90, 90, 90)
    writeln(_pdf_safe(DISCLAIMER), height=5)

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
