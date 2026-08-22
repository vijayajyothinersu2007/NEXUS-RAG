"""Chat and citation workspace with a source-context viewer."""

from __future__ import annotations

from html import escape
from time import perf_counter

import streamlit as st

from app.ui.layout import page_header
from backend.rag.generator import RAGGenerationError, RAGGenerator


SAMPLE_QUERY = "What is the standard procedure for Project Ingestion?"
SAMPLE_EVIDENCE = {
    "text": "Project Ingestion begins by validating the source file, extracting its content, registering the document, and then chunking and indexing it for retrieval.",
    "metadata": {"filename": "operations_manual.docx", "page_num": 4, "chunk_id": "sample-context-01"},
}


def render_chat() -> None:
    page_header("Chat & Citation", "Ask grounded questions and inspect the exact evidence behind every answer.")
    chat_column, evidence_column = st.columns([1.15, 0.85], gap="large")
    with chat_column:
        _render_chat_panel()
    with evidence_column:
        _render_evidence_viewer()


def _render_chat_panel() -> None:
    st.subheader("Chat")
    messages = st.session_state.get("chat_messages", [])
    if not messages:
        st.markdown(f"**Sample query**  \n{SAMPLE_QUERY}")
        st.markdown("The standard procedure is to validate the source, extract its content, register the document, then chunk and index it for retrieval. [1]")
        if st.button("[1]  View source", key="sample_citation"):
            st.session_state["active_citation"] = SAMPLE_EVIDENCE
        st.divider()
    for message_index, message in enumerate(messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("evidence"):
                _render_citation_buttons(message["evidence"], f"message_{message_index}")
    query = st.chat_input("Ask about the document library")
    if not query:
        return
    st.session_state.setdefault("chat_messages", []).append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    try:
        started = perf_counter()
        generator = RAGGenerator()
        evidence = generator.retrieve(query)
        with st.chat_message("assistant"):
            response = st.write_stream(generator.stream(query, evidence))
            _render_citation_buttons(evidence, "latest")
            feedback = st.radio("Was this response useful?", ["Helpful", "Not helpful"], horizontal=True, key=f"feedback_{len(messages)}")
        st.session_state["chat_messages"].append({"role": "assistant", "content": response, "evidence": evidence})
        st.session_state.setdefault("response_feedback", []).append({"feedback": feedback, "query": query})
        st.session_state.setdefault("query_log", []).append({"query": query, "latency_ms": round((perf_counter() - started) * 1000), "evidence": len(evidence)})
    except (RAGGenerationError, RuntimeError, ImportError, OSError) as exc:
        print("Gemini API Error:", exc)
        st.error(f"Error details: {exc}")


def _render_citation_buttons(evidence: list[dict[str, object]], key_suffix: str) -> None:
    st.caption("Citations")
    columns = st.columns(min(len(evidence), 4))
    for index, item in enumerate(evidence):
        metadata = item.get("metadata", {})
        if columns[index % len(columns)].button(f"[{index + 1}]", key=f"citation_{key_suffix}_{index}", help=f"Open {metadata.get('filename', 'source')} page {metadata.get('page_num', '?')}"):
            st.session_state["active_citation"] = item


def _render_evidence_viewer() -> None:
    st.subheader("Evidence Viewer")
    evidence = st.session_state.get("active_citation", SAMPLE_EVIDENCE)
    metadata = evidence.get("metadata", {})
    st.markdown(f"**{metadata.get('filename', 'operations_manual.docx')}** · page {metadata.get('page_num', '?')}")
    st.markdown(f'<div class="nx-citation-card"><strong>Highlighted context [1]</strong><br><br>{escape(str(evidence.get("text", "")))}</div>', unsafe_allow_html=True)
    st.caption(f"Chunk: {metadata.get('chunk_id', 'Retrieved passage')}")


def _render_api_error(message: str) -> None:
    st.markdown(f'<div class="nx-alert"><div class="nx-alert-title">Gemini response unavailable</div><div class="nx-alert-detail">{escape(message)} Open Settings to verify the API key, billing status, and quota.</div></div>', unsafe_allow_html=True)
