"""Header and disclaimer components."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

DISCLAIMER = (
    "LegalEase generates AI-assisted legal-document drafts for informational "
    "and drafting purposes. Review the document with a qualified legal "
    "professional where appropriate."
)

STYLES_PATH = Path(__file__).resolve().parent.parent / "styles.css"


def inject_styles() -> None:
    if STYLES_PATH.exists():
        st.markdown(f"<style>{STYLES_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header() -> None:
    inject_styles()
    st.markdown(
        """
        <div class="legalease-hero">
          <h1>LegalEase</h1>
          <p>AI-Powered Legal Document Generator — draft, preview, edit, analyze, and export professional legal-document outlines in minutes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="legalease-disclaimer">{DISCLAIMER}</div>', unsafe_allow_html=True)


def render_section_title(title: str) -> None:
    st.markdown(f'<div class="legalease-section-title">{title}</div>', unsafe_allow_html=True)
