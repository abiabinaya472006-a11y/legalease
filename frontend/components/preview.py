"""Preview and edit panel components."""

from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st

from frontend.components.header import render_section_title


def render_preview_and_editor(document: Dict[str, Any]) -> str:
    """Show structured preview + editable content. Returns current edited text."""
    st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
    render_section_title("Generated Document Preview")

    title = document.get("title") or document.get("document_type") or "Document"
    parties = document.get("parties") or []
    effective_date = document.get("effective_date") or "—"
    jurisdiction = document.get("jurisdiction") or "—"
    language = document.get("language") or "English"

    meta_cols = st.columns(4)
    meta_cols[0].markdown(f"**Title**\n\n{title}")
    meta_cols[1].markdown(f"**Parties**\n\n{', '.join(parties) if parties else '—'}")
    meta_cols[2].markdown(f"**Effective Date**\n\n{effective_date}")
    meta_cols[3].markdown(f"**Language**\n\n{language}")
    st.caption(f"Jurisdiction: {jurisdiction}")

    sections = document.get("sections") or []
    if sections:
        with st.expander("Structured sections", expanded=False):
            for section in sections:
                st.markdown(f"**{section.get('heading', 'Section')}**")
                st.write(section.get("content") or "")
                st.divider()

    assumptions = document.get("assumptions") or []
    if assumptions:
        with st.expander("Assumptions / placeholders", expanded=False):
            for item in assumptions:
                st.markdown(f"- {item}")

    if document.get("disclaimer"):
        st.info(document["disclaimer"])

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
    render_section_title("Edit Mode")
    st.caption("Modify the draft before exporting. Your edits are used for downloads and translation.")
    edited = st.text_area(
        "Editable document content",
        value=st.session_state.get("edited_content") or document.get("content", ""),
        height=420,
        key="document_editor",
        label_visibility="collapsed",
    )
    st.session_state["edited_content"] = edited
    st.markdown("</div>", unsafe_allow_html=True)
    return edited


def render_analysis_panel(analysis: Optional[Dict[str, Any]]) -> None:
    if not analysis:
        return
    st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
    render_section_title("AI Analysis")
    st.caption(analysis.get("disclaimer", ""))
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**Document type:** {analysis.get('document_type') or 'Not specified'}")
        st.markdown("**Parties**")
        for p in analysis.get("parties") or ["Not specified"]:
            st.write(f"- {p}")
        st.markdown("**Important dates**")
        for d in analysis.get("important_dates") or ["Not specified"]:
            st.write(f"- {d}")
        st.markdown("**Key clauses**")
        for c in analysis.get("key_clauses") or ["Not specified"]:
            st.write(f"- {c}")
        st.markdown("**Obligations**")
        for o in analysis.get("obligations") or ["Not specified"]:
            st.write(f"- {o}")
    with cols[1]:
        st.markdown("**Payment terms**")
        for p in analysis.get("payment_terms") or ["Not specified"]:
            st.write(f"- {p}")
        st.markdown("**Termination clauses**")
        for t in analysis.get("termination_clauses") or ["Not specified"]:
            st.write(f"- {t}")
        st.markdown("**Confidentiality clauses**")
        for c in analysis.get("confidentiality_clauses") or ["Not specified"]:
            st.write(f"- {c}")
        st.markdown("**Important conditions**")
        for c in analysis.get("important_conditions") or ["Not specified"]:
            st.write(f"- {c}")
        st.markdown("**Missing information**")
        for m in analysis.get("missing_information") or ["Not specified"]:
            st.write(f"- {m}")
    with st.expander("Full analysis text"):
        st.text(analysis.get("raw_analysis") or "")
    st.markdown("</div>", unsafe_allow_html=True)
