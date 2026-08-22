"""Settings — runtime configuration and secret management."""

from __future__ import annotations

import os

import streamlit as st

from app.ui.layout import page_header
from config.settings import get_settings


def render_settings() -> None:
    page_header("Settings", "Runtime configuration loaded from environment variables.")
    settings = get_settings()
    api_tab, runtime_tab = st.tabs(["API & model", "Runtime"])
    with api_tab:
        configured = bool(settings.gemini_api_key.get_secret_value())
        st.subheader("Gemini API")
        st.caption("Enter a key for this running session. Keys are never displayed or written to the page.")
        st.write(f"Current status: {'Configured (********)' if configured else 'Not configured'}")
        with st.form("gemini_api_key_form"):
            api_key = st.text_input("Gemini API key", type="password", placeholder="Paste a new key to add or replace the current key").strip()
            if st.form_submit_button("Save API key"):
                if not api_key:
                    st.warning("Enter an API key before saving.")
                else:
                    st.session_state["gemini_api_key"] = api_key
                    os.environ["GEMINI_API_KEY"] = api_key
                    get_settings.cache_clear()
                    st.success("Gemini API key updated for this session.")
                    st.rerun()
        if configured and st.button("Clear Gemini API key"):
            st.session_state["gemini_api_key"] = ""
            os.environ["GEMINI_API_KEY"] = ""
            get_settings.cache_clear()
            st.rerun()
        st.slider("Model temperature", 0.0, 1.0, 0.2, 0.05, help="Reserved for the next generation configuration update.")
        st.write({"llm_model": settings.llm_model, "embedding_model": settings.embedding_model})
    with runtime_tab:
        st.metric("API key status", "Connected" if configured else "Action required")
        st.write({"app_name": settings.app_name, "app_env": settings.app_env, "log_level": settings.log_level, "max_upload_mb": settings.max_upload_mb, "data_dir": str(settings.data_dir)})
