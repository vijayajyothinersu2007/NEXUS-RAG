"""Version history and comparison launcher."""

import streamlit as st

from app.ui.layout import page_header
from backend.ingestion.registry import DocumentRegistry


def render_versions() -> None:
    page_header("Version history", "Uploaded versions and their indexing state.")
    documents = sorted(DocumentRegistry().list_documents(), key=lambda doc: doc.upload_date, reverse=True)
    if not documents:
        st.info("No document versions have been uploaded.")
        return
    summary, timeline = st.tabs(["Summary", "Timeline"])
    with summary:
        c1, c2, c3 = st.columns(3)
        c1.metric("Tracked files", len({doc.document_name for doc in documents}))
        c2.metric("Uploaded versions", len(documents))
        c3.metric("Latest upload", documents[0].upload_date.strftime("%d %b %Y"))
    with timeline:
        for document in documents:
            with st.expander(f"{document.document_name} · v{document.version} · {document.upload_date:%Y-%m-%d}"):
                st.write(f"Filename: {document.original_filename}")
                st.write(f"Status: {document.display_status()} | Pages: {document.page_count or 0} | Chunks: {document.chunk_count}")
                if document.warnings:
                    for warning in document.warnings:
                        st.warning(warning)
    st.caption("Use Compare documents to inspect rule-level changes between versions.")
