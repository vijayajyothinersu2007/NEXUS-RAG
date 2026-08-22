"""Shared Streamlit layout and navigation."""

from __future__ import annotations

import streamlit as st

from app.ui.theme import ENTERPRISE_CSS
from config.settings import get_settings

PAGES = [
    ("evaluation", "Evaluation"),
    ("dashboard", "Dashboard"),
    ("documents", "Documents"),
    ("chat", "Chat & Citation"),
    ("graph", "Knowledge Graph"),
    ("compare", "Compare Documents"),
    ("versions", "Version History"),
    ("settings", "Settings"),
]


def bootstrap_page() -> None:
    settings = get_settings()
    st.set_page_config(
        page_title=f"{settings.app_name} — Evidence-First Knowledge Intelligence",
        page_icon="◆",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="nx-brand">
                <svg class="nx-brand-logo" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="NexusRAG logo">
                    <path d="M18 2.5 30.99 10v15L18 32.5 5.01 25V10L18 2.5Z" stroke="#818CF8" stroke-width="1.5"/>
                    <path d="m11 13 7 4 7-4M18 17v8" stroke="#C4B5FD" stroke-width="1.5" stroke-linecap="round"/>
                    <circle cx="18" cy="17" r="2.3" fill="#6366F1" stroke="#E0E7FF" stroke-width="1"/>
                </svg>
                <div class="nx-brand-mark">NEXUS RAG</div>
                <div class="nx-brand-sub">Evidence-first enterprise knowledge intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="nx-nav-group">RAG Evaluations</div>', unsafe_allow_html=True)
        for index, (key, label) in enumerate(PAGES):
            if index == 1:
                st.markdown('<div class="nx-nav-group nx-nav-group-secondary">Workspace</div>', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}", width="stretch", type="primary" if st.session_state.current_page == key else "secondary"):
                st.session_state.current_page = key
        st.markdown("---")
        st.markdown(
            '<div class="nx-status"><span class="nx-status-dot"></span>System operational</div>',
            unsafe_allow_html=True,
        )
        st.caption("Evidence-first answers")
    return st.session_state.current_page


def page_header(title: str, subtitle: str) -> None:
    evaluation = st.session_state.get("latest_evaluation", {})
    faithfulness = evaluation.get("faithfulness", 0.0)
    relevancy = evaluation.get("answer_relevance", 0.0)
    st.markdown(
        '<div class="nx-topbar"><span style="color:#64748B;font-size:0.78rem;">NEXUS RAG / WORKSPACE</span>'
        '<span class="nx-status"><span class="nx-status-dot"></span>Live workspace</span>'
        f'<div class="nx-model-metrics"><span>MODEL METRICS</span><strong>Faithfulness {faithfulness:.0%}</strong><strong>Relevancy {relevancy:.0%}</strong></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="nx-page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nx-page-sub">{subtitle}</div>', unsafe_allow_html=True)


def coming_soon(phase: str, capability: str) -> None:
    st.markdown(
        f"""
        <div class="nx-placeholder">
            <strong>{capability} is not implemented yet.</strong>
            <p>This screen is reserved for {phase}. NexusRAG will not display placeholder
            answers, fake citations, or simulated graph data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
