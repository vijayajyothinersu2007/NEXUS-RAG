"""Cross-document comparison."""

from pathlib import Path

import streamlit as st

from app.ui.layout import page_header
from backend.comparison.diff_engine import DiffEngine
from backend.ingestion.registry import DocumentRegistry
from config.settings import get_settings


def render_compare() -> None:
    page_header("Compare documents", "Review additions, removals, modifications, and policy conflicts from extracted evidence.")
    documents = [doc for doc in DocumentRegistry().list_documents() if doc.extracted_path and Path(doc.extracted_path).exists()]
    if len(documents) < 2:
        st.info("Upload and parse at least two documents to compare them.")
        return
    labels = [f"{doc.document_name} · v{doc.version}" for doc in documents]
    left, right = st.columns(2)
    before_index = left.selectbox("Earlier document", range(len(documents)), format_func=lambda index: labels[index])
    after_index = right.selectbox("Later document", range(len(documents)), index=min(1, len(documents) - 1), format_func=lambda index: labels[index])
    if before_index == after_index:
        st.warning("Choose two different documents.")
        return
    result = DiffEngine().compare_files(documents[before_index].extracted_path, documents[after_index].extracted_path)
    summary = result["summary"]
    cols = st.columns(4)
    for column, kind in zip(cols, ("added", "removed", "modified", "conflict")):
        column.metric(kind.title(), summary[kind])
    for change in result["changes"]:
        title = f"{change['change_type'].title()}: {change['key']}"
        with st.expander(title):
            if change["before"]:
                st.markdown(f"**Before (page {change['page_before'] or '?'})**")
                st.code(change["before"], language="text")
            if change["after"]:
                st.markdown(f"**After (page {change['page_after'] or '?'})**")
                st.code(change["after"], language="text")
