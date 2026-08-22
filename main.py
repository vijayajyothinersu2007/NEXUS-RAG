"""NexusRAG Streamlit entry point."""

from __future__ import annotations



import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.pages.chat import render_chat
from app.pages.compare import render_compare
from app.pages.dashboard import render_dashboard
from app.pages.documents import render_documents
from app.pages.evaluation import render_evaluation
from app.pages.knowledge_graph import render_knowledge_graph
from app.pages.settings import render_settings
from app.pages.versions import render_versions
from app.ui.layout import bootstrap_page, render_sidebar
from config.settings import get_settings

PAGE_RENDERERS = {
    "dashboard": render_dashboard,
    "documents": render_documents,
    "chat": render_chat,
    "graph": render_knowledge_graph,
    "compare": render_compare,
    "versions": render_versions,
    "evaluation": render_evaluation,
    "settings": render_settings,
}


def main() -> None:
    get_settings()
    bootstrap_page()
    page = render_sidebar()
    PAGE_RENDERERS[page]()


if __name__ == "__main__":
    main()
