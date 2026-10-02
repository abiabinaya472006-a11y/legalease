"""Document input form components."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Tuple

import streamlit as st

from frontend.components.header import render_section_title

DOCUMENT_TYPES = [
    "Employment Contract",
    "NDA",
    "Lease Agreement",
    "Freelance Agreement",
    "Service Agreement",
    "Offer Letter",
    "Partnership Agreement",
    "General Agreement",
]

LANGUAGES = ["English", "Tamil", "Hindi", "Telugu", "Malayalam", "Kannada"]


def render_document_form() -> Tuple[Dict[str, Any], bool]:
    """Render the main generation form. Returns (payload, submitted)."""
    with st.container():
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("1. Document Type")
        document_type = st.selectbox(
            "Select a legal document type",
            DOCUMENT_TYPES,
            help="Choose the template that best matches your drafting needs.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("2. Parties")
        parties_raw = st.text_area(
            "Parties involved (one name per line)",
            placeholder="Acme Pvt Ltd\nJordan Lee",
            height=100,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("3. Terms & Conditions")
        terms = st.text_area(
            "Enter key terms, obligations, payment details, duration, etc.",
            placeholder=(
                "Example: 12-month engagement, monthly fee of INR 50,000, "
                "30-day termination notice, confidentiality for 2 years..."
            ),
            height=160,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("4. Effective Date")
        effective_date = st.date_input("Effective date", value=date.today())
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("5. Jurisdiction")
        jurisdiction = st.text_input(
            "Governing jurisdiction",
            value="India",
            placeholder="e.g., State of California / India / England & Wales",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("6. Language")
        language = st.selectbox("Output language", LANGUAGES, index=0)
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("7. Branding")
        include_logo = st.checkbox("Include logo on exports", value=True)
        include_signature = st.checkbox("Include signature block on exports", value=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("8. Additional Instructions")
        additional = st.text_area(
            "Optional drafting instructions",
            placeholder="e.g., Keep clauses concise; emphasize remote-work policy.",
            height=90,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    submitted = st.button("Generate Document", type="primary", use_container_width=True)

    parties: List[str] = [p.strip() for p in parties_raw.splitlines() if p.strip()]
    payload = {
        "document_type": document_type,
        "parties": parties,
        "terms": terms.strip(),
        "effective_date": effective_date.isoformat(),
        "jurisdiction": jurisdiction.strip() or "Not specified",
        "language": language,
        "additional_instructions": additional.strip() or None,
        "include_logo": include_logo,
        "include_signature": include_signature,
    }
    return payload, submitted


def validate_form(payload: Dict[str, Any]) -> List[str]:
    """Client-side validation messages before calling the API."""
    errors: List[str] = []
    if not payload.get("parties"):
        errors.append("Add at least one party (one name per line).")
    if not payload.get("terms") or len(payload["terms"]) < 10:
        errors.append("Terms & conditions must be at least 10 characters.")
    if not payload.get("effective_date"):
        errors.append("Effective date is required.")
    return errors
