"""
LegalEase — Streamlit Frontend

Run from project root:
    streamlit run frontend/app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

# Ensure project root is on sys.path when launched via Streamlit
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.api_client import LegalEaseAPIError, LegalEaseClient
from frontend.components.downloads import render_download_options
from frontend.components.form import LANGUAGES, render_document_form, validate_form
from frontend.components.header import DISCLAIMER, render_header, render_section_title
from frontend.components.preview import render_analysis_panel, render_preview_and_editor

st.set_page_config(
    page_title="LegalEase — AI Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_client() -> LegalEaseClient:
    backend_url = st.session_state.get("backend_url") or os.getenv(
        "BACKEND_API_URL", "http://localhost:8000"
    )
    return LegalEaseClient(base_url=backend_url)


def init_state() -> None:
    defaults = {
        "document": None,
        "edited_content": "",
        "analysis": None,
        "summary": None,
        "translated": None,
        "backend_url": os.getenv("BACKEND_API_URL", "http://localhost:8000"),
        "include_logo": True,
        "include_signature": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar(client: LegalEaseClient) -> None:
    with st.sidebar:
        st.markdown("### LegalEase Settings")
        st.session_state["backend_url"] = st.text_input(
            "Backend API URL",
            value=st.session_state["backend_url"],
            help="Configurable FastAPI base URL",
        )
        if st.button("Check API health", use_container_width=True):
            try:
                health = LegalEaseClient(st.session_state["backend_url"]).health()
                status = health.get("status", "unknown")
                gemini_ok = health.get("gemini_configured", False)
                if status == "healthy":
                    st.success(f"API healthy · Gemini configured: {gemini_ok}")
                else:
                    st.warning(
                        f"API reachable but degraded. Gemini configured: {gemini_ok}. "
                        f"{health.get('details', {}).get('message', '')}"
                    )
            except LegalEaseAPIError as exc:
                st.error(str(exc))

        st.divider()
        st.markdown("### Legal notice")
        st.caption(DISCLAIMER)
        st.divider()
        st.markdown("### Tips")
        st.caption(
            "1. Start the backend first (`uvicorn backend.main:app --reload`).\n"
            "2. Set `GEMINI_API_KEY` in `.env`.\n"
            "3. Place a logo at `assets/logo.png` for branded exports.\n"
            "4. Edit drafts before downloading."
        )


def main() -> None:
    init_state()
    render_header()
    client = get_client()
    render_sidebar(client)

    tab_generate, tab_analyze = st.tabs(["Draft Generator", "Analyze / Summarize"])

    with tab_generate:
        payload, submitted = render_document_form()
        st.session_state["include_logo"] = payload.get("include_logo", True)
        st.session_state["include_signature"] = payload.get("include_signature", True)

        if submitted:
            errors = validate_form(payload)
            if errors:
                for err in errors:
                    st.error(err)
            else:
                api_payload = {
                    k: v
                    for k, v in payload.items()
                    if k not in {"include_logo", "include_signature"}
                }
                try:
                    with st.spinner("Generating your legal-document draft with Gemini..."):
                        result = client.generate(api_payload)
                    st.session_state["document"] = result
                    st.session_state["edited_content"] = result.get("content", "")
                    st.session_state["analysis"] = None
                    st.session_state["summary"] = None
                    st.session_state["translated"] = None
                    for fmt in ("docx", "pdf", "txt"):
                        st.session_state.pop(f"export_{fmt}", None)
                    st.success("Document draft generated. Review and edit below.")
                except LegalEaseAPIError as exc:
                    st.error(str(exc))
                except Exception:  # noqa: BLE001
                    st.error("Unexpected error while generating the document.")

        document = st.session_state.get("document")
        if document:
            edited = render_preview_and_editor(document)

            # Analysis / summary / translation of generated content
            st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
            render_section_title("AI Tools for This Draft")
            tool_cols = st.columns(3)
            with tool_cols[0]:
                if st.button("Analyze draft", use_container_width=True):
                    try:
                        with st.spinner("Analyzing..."):
                            st.session_state["analysis"] = client.analyze(
                                edited, document.get("language", "English")
                            )
                        st.success("Analysis complete.")
                    except LegalEaseAPIError as exc:
                        st.error(str(exc))
            with tool_cols[1]:
                if st.button("Summarize draft", use_container_width=True):
                    try:
                        with st.spinner("Summarizing..."):
                            st.session_state["summary"] = client.summarize(
                                edited, document.get("language", "English")
                            )
                        st.success("Summary ready.")
                    except LegalEaseAPIError as exc:
                        st.error(str(exc))
            with tool_cols[2]:
                target_lang = st.selectbox(
                    "Translate to",
                    LANGUAGES,
                    index=LANGUAGES.index(document.get("language", "English"))
                    if document.get("language") in LANGUAGES
                    else 0,
                    key="translate_target",
                )
                if st.button("Translate draft", use_container_width=True):
                    try:
                        with st.spinner(f"Translating to {target_lang}..."):
                            result = client.translate(edited, target_lang)
                        st.session_state["translated"] = result
                        st.session_state["edited_content"] = result.get("translated_text", edited)
                        st.success(f"Translated to {target_lang}. Editor updated.")
                        st.rerun()
                    except LegalEaseAPIError as exc:
                        st.error(str(exc))
            st.markdown("</div>", unsafe_allow_html=True)

            render_analysis_panel(st.session_state.get("analysis"))

            summary = st.session_state.get("summary")
            if summary:
                st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
                render_section_title("Summary")
                st.caption(summary.get("disclaimer", ""))
                st.write(summary.get("summary", ""))
                st.markdown("</div>", unsafe_allow_html=True)

            render_download_options(
                client=client,
                title=document.get("title") or document.get("document_type") or "LegalEase Document",
                content=st.session_state.get("edited_content") or edited,
                parties=document.get("parties") or [],
                effective_date=document.get("effective_date"),
                document_type=document.get("document_type"),
                include_logo=st.session_state.get("include_logo", True),
                include_signature=st.session_state.get("include_signature", True),
            )

    with tab_analyze:
        st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
        render_section_title("Analyze an Existing Document")
        st.caption(
            "Paste text or upload a .txt/.md file. Analysis is informational only "
            "and does not determine legal validity."
        )
        analysis_language = st.selectbox("Analysis language", LANGUAGES, key="analysis_lang")
        uploaded = st.file_uploader("Upload text file (optional)", type=["txt", "md", "text"])
        pasted = st.text_area(
            "Or paste legal-document text",
            height=260,
            placeholder="Paste contract or agreement text here...",
        )
        source_text = pasted.strip()
        if uploaded is not None:
            try:
                source_text = uploaded.read().decode("utf-8", errors="replace").strip()
            except Exception:  # noqa: BLE001
                st.error("Could not read the uploaded file as text.")

        a_col, s_col = st.columns(2)
        with a_col:
            if st.button("Run analysis", use_container_width=True, key="run_analysis"):
                if len(source_text) < 20:
                    st.error("Provide at least 20 characters of document text.")
                else:
                    try:
                        with st.spinner("Analyzing document..."):
                            st.session_state["standalone_analysis"] = client.analyze(
                                source_text, analysis_language
                            )
                    except LegalEaseAPIError as exc:
                        st.error(str(exc))
        with s_col:
            if st.button("Run summary", use_container_width=True, key="run_summary"):
                if len(source_text) < 20:
                    st.error("Provide at least 20 characters of document text.")
                else:
                    try:
                        with st.spinner("Summarizing document..."):
                            st.session_state["standalone_summary"] = client.summarize(
                                source_text, analysis_language
                            )
                    except LegalEaseAPIError as exc:
                        st.error(str(exc))
        st.markdown("</div>", unsafe_allow_html=True)

        render_analysis_panel(st.session_state.get("standalone_analysis"))
        standalone_summary = st.session_state.get("standalone_summary")
        if standalone_summary:
            st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
            render_section_title("Plain-Language Summary")
            st.caption(standalone_summary.get("disclaimer", ""))
            st.write(standalone_summary.get("summary", ""))
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
