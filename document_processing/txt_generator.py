"""Plain-text export without HTML formatting."""

from __future__ import annotations

from typing import List, Optional

from backend.utils.sanitizers import sanitize_text
from document_processing.formatter import DISCLAIMER, build_footer_text


def generate_txt(
    title: str,
    content: str,
    parties: Optional[List[str]] = None,
    effective_date: Optional[str] = None,
    document_type: Optional[str] = None,
    include_logo: bool = True,  # kept for API symmetry; ignored for TXT
    include_signature: bool = True,
) -> bytes:
    """Generate a clean UTF-8 plain-text document."""
    parties = parties or []
    title = sanitize_text(title, max_length=300)
    content = sanitize_text(content)

    lines: List[str] = []
    lines.append(title.upper())
    lines.append("=" * len(title))
    lines.append("")

    if document_type:
        lines.append(f"Document Type: {document_type}")
    if parties:
        lines.append(f"Parties: {', '.join(parties)}")
    if effective_date:
        lines.append(f"Effective Date: {effective_date}")
    if document_type or parties or effective_date:
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    lines.append(content.rstrip())
    lines.append("")

    if include_signature and "signature" not in content.lower():
        lines.append("")
        lines.append("SIGNATURES")
        lines.append("-" * 11)
        for party in parties or ["Party A", "Party B"]:
            lines.append("")
            lines.append(f"For {party}:")
            lines.append("Signature: _______________________________")
            lines.append("Name: ____________________________________")
            lines.append("Date: ____________________________________")

    lines.append("")
    lines.append("-" * 60)
    lines.append(DISCLAIMER)
    lines.append(build_footer_text())
    lines.append("")

    text = "\n".join(lines)
    return text.encode("utf-8")
