"""Dashboard — real ingestion metrics only."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.ui.layout import page_header
from backend.ingestion.registry import DocumentRegistry
from config.settings import get_settings


def render_dashboard() -> None:
    page_header(
        "Knowledge workspace",
        "A live view of your evidence library and ingestion health.",
    )
    registry = DocumentRegistry()
    stats = registry.stats()
    docs = registry.list_documents()

    c1, c2, c3, c4 = st.columns(4)
    _metric(c1, "Total documents", stats["total_documents"], "Library size")
    _metric(c2, "Parsed documents", stats["parsed_documents"], "Ready for retrieval")
    _metric(c3, "Parse failures", stats["failed_documents"], "Needs attention")
    _metric(c4, "Document versions", stats["document_versions"], "Tracked revisions")

    c5, c6, c7, c8 = st.columns(4)
    _metric(c5, "Total pages", stats["total_pages"], "Across all sources")
    _metric(c6, "Extracted characters", f'{stats["total_characters"]:,}', "Text captured")
    _metric(c7, "Indexed documents", stats["indexed_documents"], hint="Phase 2")
    _metric(c8, "Total chunks", stats["total_chunks"], hint="Phase 2")

    st.divider()
    chart_left, chart_right = st.columns(2)
    _render_entity_chart(chart_left)
    _render_relationship_chart(chart_right, docs)
    _render_query_telemetry()

    left, right = st.columns((1.2, 1))
    with left:
        st.subheader("Document inventory")
        if not docs:
            st.info("No documents uploaded yet. Open Documents to add PDF, DOCX, TXT, CSV, or XLSX files.")
        else:
            frame = pd.DataFrame(
                [
                    {
                        "Name": d.document_name,
                        "Type": d.document_type.value.upper(),
                        "Version": d.version,
                        "Year": d.year or "",
                        "Department": d.department or "—",
                        "Status": d.display_status(),
                        "Pages": d.page_count or 0,
                        "Chunks": d.chunk_count,
                    }
                    for d in sorted(docs, key=lambda item: item.upload_date, reverse=True)
                ]
            )
            st.dataframe(frame, width="stretch", hide_index=True)
    with right:
        st.subheader("By file type")
        by_type = stats["by_type"]
        if by_type:
            chart = px.bar(x=list(by_type.keys()), y=list(by_type.values()), labels={"x": "File type", "y": "Documents"})
            _dark_chart(chart)
            st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
        else:
            st.caption("Upload documents to see type distribution.")


def _metric(container, label: str, value, hint: str | None = None) -> None:
    with container:
        st.markdown(
            f"""
            <div class="nx-card">
                <div class="nx-metric-label">{label}</div>
                <div class="nx-metric-value">{value}</div>
                <div style="color:#7F8C8D;font-size:0.75rem;">{hint or "&nbsp;"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_entity_chart(container) -> None:
    with container:
        st.subheader("Knowledge graph entities")
        graph = _load_graph()
        counts = graph.get("entity_counts", {})
        if not counts:
            st.caption("Build the knowledge graph to populate entity analytics.")
            return
        chart = go.Figure(go.Pie(labels=list(counts), values=list(counts.values()), hole=0.62, marker={"colors": ["#818CF8", "#2DD4BF", "#FACC15", "#FB7185"]}))
        _dark_chart(chart)
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})


def _render_relationship_chart(container, documents) -> None:
    with container:
        st.subheader("Relationships by file")
        graph = _load_graph()
        density = graph.get("relationship_density", {})
        if not density:
            density = {doc.original_filename: doc.chunk_count for doc in documents if doc.chunk_count}
        if not density:
            st.caption("Relationship density will appear after graph extraction.")
            return
        chart = px.bar(x=list(density), y=list(density.values()), labels={"x": "Source file", "y": "Relationships"})
        _dark_chart(chart)
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})


def _render_query_telemetry() -> None:
    st.subheader("Query activity")
    queries = st.session_state.get("query_log", [])
    if not queries:
        st.caption("Submit a chat query to begin tracking volume and response latency.")
        return
    frame = pd.DataFrame(queries)
    average = frame["latency_ms"].mean()
    metric, _ = st.columns([1, 3])
    metric.metric("Average latency", f"{average:.0f} ms")
    chart = px.area(frame, y="latency_ms", labels={"index": "Query", "latency_ms": "Latency (ms)"})
    _dark_chart(chart)
    st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})


def _load_graph() -> dict:
    path = get_settings().processed_dir / "knowledge_graph.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    nodes = raw.get("nodes", [])
    edges = raw.get("links", raw.get("edges", []))
    entity_counts: dict[str, int] = {}
    for node in nodes:
        kind = node.get("kind", node.get("type", "Entity"))
        entity_counts[kind] = entity_counts.get(kind, 0) + 1
    density: dict[str, int] = {}
    for edge in edges:
        filename = edge.get("filename", "Unknown source")
        density[filename] = density.get(filename, 0) + 1
    return {"entity_counts": entity_counts, "relationship_density": density}


def _dark_chart(chart) -> None:
    chart.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin={"t": 12, "r": 8, "b": 40, "l": 40}, font={"color": "#CBD5E1"})
