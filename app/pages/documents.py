"""Documents — upload, inspect, re-parse, delete."""

from __future__ import annotations

from datetime import datetime
from math import ceil

import streamlit as st

from app.ui.layout import page_header
from backend.ingestion.models import IndexingStatus
from backend.ingestion.pipeline import IngestionPipeline


def render_documents() -> None:
    page_header(
        "Document management",
        "Upload enterprise files, extract text and structure, and inspect metadata. Chunking and embeddings start in Phase 2.",
    )
    pipeline = IngestionPipeline()
    registry = pipeline.registry

    with st.container():
        st.subheader("Upload")
        with st.form("upload_form", clear_on_submit=True):
            uploaded = st.file_uploader(
                "PDF, DOCX, TXT, CSV, or XLSX",
                type=["pdf", "docx", "txt", "csv", "xlsx"],
            )
            c1, c2, c3 = st.columns(3)
            document_name = c1.text_input("Document name (optional)")
            version = c2.text_input("Version", value="1.0")
            year = c3.number_input("Year", min_value=1990, max_value=2100, value=datetime.now().year)
            c4, c5 = st.columns(2)
            department = c4.text_input("Department / owner")
            category = c5.text_input("Category", placeholder="Policy, Regulation, Manual…")
            submitted = st.form_submit_button("Upload and parse", type="primary")

        if submitted:
            if uploaded is None:
                st.error("Choose a file before uploading.")
            else:
                with st.spinner("Validating and parsing document…"):
                    progress = st.progress(0, text="Storing uploaded file")
                    file_bytes = uploaded.getvalue()
                    progress.progress(35, text="Parsing document")
                    result = pipeline.ingest_bytes(
                        uploaded.name,
                        file_bytes,
                        version=version,
                        year=int(year),
                        department=department,
                        category=category,
                        document_name=document_name,
                    )
                    progress.progress(85, text="Chunking and indexing")
                    progress.progress(100, text="Ingestion complete")
                if result.success:
                    st.success(result.message)
                elif result.duplicate:
                    st.warning(result.message)
                else:
                    st.error(result.message)

    st.divider()
    docs = registry.list_documents()
    st.subheader(f"Library ({len(docs)})")
    if not docs:
        st.info("The library is empty. Sample files are in `data/samples` if you want to try the parsers.")
        return

    query = st.text_input("Filter by name, department, or type")
    filtered = docs
    if query.strip():
        needle = query.lower()
        filtered = [
            d
            for d in docs
            if needle in d.document_name.lower()
            or needle in d.department.lower()
            or needle in d.document_type.value
            or needle in d.category.lower()
        ]

    for doc in sorted(filtered, key=lambda item: item.upload_date, reverse=True):
        with st.expander(
            f"{doc.document_name}  ·  {doc.document_type.value.upper()}  ·  v{doc.version}  ·  {doc.display_status()}"
        ):
            status_class = {
                IndexingStatus.PARSED: "nx-badge-parsed",
                IndexingStatus.PARSE_FAILED: "nx-badge-failed",
                IndexingStatus.UPLOADED: "nx-badge-uploaded",
                IndexingStatus.INDEXED: "nx-badge-parsed",
            }[doc.indexing_status]
            st.markdown(
                f'<span class="nx-badge {status_class}">{doc.display_status()}</span>',
                unsafe_allow_html=True,
            )
            m1, m2, m3, m4 = st.columns(4)
            m1.write(f"**Year:** {doc.year or '—'}")
            m2.write(f"**Department:** {doc.department or '—'}")
            m3.write(f"**Category:** {doc.category or '—'}")
            m4.write(f"**Uploaded:** {doc.upload_date.strftime('%Y-%m-%d %H:%M UTC')}")
            n1, n2, n3, n4 = st.columns(4)
            n1.write(f"**Pages:** {doc.page_count if doc.page_count is not None else '—'}")
            n2.write(f"**Sections:** {doc.section_count}")
            n3.write(f"**Tables:** {doc.table_count}")
            n4.write(f"**Chunks:** {doc.chunk_count} (Phase 2)")
            st.caption(f"File: {doc.original_filename}  ·  {doc.file_size_bytes:,} bytes")
            st.caption(f"SHA-256: `{doc.file_hash}`")
            if doc.error_message:
                st.error(doc.error_message)
            for warning in doc.warnings:
                st.warning(warning)

            parsed = pipeline.load_extracted(doc.document_id)
            if parsed and parsed.full_text:
                token_count = ceil(len(parsed.full_text) / 4)
                st.caption(f"Estimated tokens: {token_count:,} · {len(parsed.full_text):,} characters")
                st.markdown("**Extracted preview**")
                preview = parsed.full_text[:2500]
                st.markdown(f'<div class="nx-excerpt">{_escape(preview)}</div>', unsafe_allow_html=True)
                if len(parsed.full_text) > 2500:
                    st.caption(f"Showing first 2,500 of {len(parsed.full_text):,} characters.")
                if parsed.sections:
                    st.markdown("**Detected sections**")
                    for section in parsed.sections[:12]:
                        page = f" (page {section.page_number})" if section.page_number else ""
                        st.write(f"- {section.title}{page}")

            b1, b2, _ = st.columns([1, 1, 2])
            if b1.button("Re-parse", key=f"reparse_{doc.document_id}"):
                with st.spinner("Re-parsing original file…"):
                    result = pipeline.reparse(doc.document_id)
                if result.success:
                    st.success(result.message)
                    st.rerun()
                else:
                    st.error(result.message)
            if b2.button("Delete", key=f"delete_{doc.document_id}"):
                pipeline.delete(doc.document_id)
                st.success("Document deleted.")
                st.rerun()


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )
