"""Download button helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st

from frontend.api_client import LegalEaseAPIError, LegalEaseClient
from frontend.components.header import render_section_title


def render_download_options(
    client: LegalEaseClient,
    title: str,
    content: str,
    parties: list,
    effective_date: Optional[str],
    document_type: Optional[str],
    include_logo: bool = True,
    include_signature: bool = True,
) -> None:
    st.markdown('<div class="legalease-card">', unsafe_allow_html=True)
    render_section_title("Download Options")
    st.caption("Exports use your latest edited content.")

    col1, col2, col3 = st.columns(3)
    formats = [
        (col1, "docx", "Download DOCX", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        (col2, "pdf", "Download PDF", "application/pdf"),
        (col3, "txt", "Download TXT", "text/plain"),
    ]

    for col, fmt, label, mime in formats:
        with col:
            if st.button(label, use_container_width=True, key=f"btn_{fmt}"):
                try:
                    with st.spinner(f"Preparing {fmt.upper()}..."):
                        data = client.export(
                            fmt=fmt,
                            title=title,
                            content=content,
                            parties=parties,
                            effective_date=effective_date,
                            document_type=document_type,
                            include_logo=include_logo,
                            include_signature=include_signature,
                        )
                    st.session_state[f"export_{fmt}"] = data
                    st.success(f"{fmt.upper()} ready below.")
                except LegalEaseAPIError as exc:
                    st.error(str(exc))
                except Exception:  # noqa: BLE001
                    st.error(f"Could not export {fmt.upper()}. Please try again.")

            payload = st.session_state.get(f"export_{fmt}")
            if payload:
                safe_name = "".join(ch if ch.isalnum() or ch in "-_ " else "_" for ch in title)[:60] or "document"
                st.download_button(
                    label=f"Save {fmt.upper()}",
                    data=payload,
                    file_name=f"{safe_name.strip().replace(' ', '_')}.{fmt}",
                    mime=mime,
                    use_container_width=True,
                    key=f"dl_{fmt}",
                )

    st.markdown("</div>", unsafe_allow_html=True)
