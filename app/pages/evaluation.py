"""Reference-based RAG evaluation dashboard."""

import streamlit as st
import plotly.graph_objects as go

from app.ui.layout import page_header
from backend.evaluation.evaluator import RAGEvaluator


def render_evaluation() -> None:
    page_header("RAG evaluation", "Compute metrics from an actual answer, retrieved context, and optional reference facts.")
    _render_live_feedback()
    input_tab, results_tab = st.tabs(["Evaluation workspace", "Latest diagnostics"])
    with input_tab:
        _initialize_evaluation_inputs()
        if st.button("Load latest chat response", key="load_latest_evaluation"):
            _initialize_evaluation_inputs(force=True)
            st.rerun()
        question = st.text_input(
            "Question",
            key="evaluation_question",
            disabled=False,
        )
        answer = st.text_area(
            "Generated answer",
            key="evaluation_answer",
            height=160,
            disabled=False,
        )
        contexts = st.text_area(
            "Retrieved contexts",
            key="evaluation_contexts",
            height=180,
            help="Separate retrieved passages with a blank line.",
            disabled=False,
        )
        reference = st.text_area(
            "Reference answer or required facts",
            key="evaluation_reference",
            height=140,
            help="Optional. Separate required facts with a blank line.",
            disabled=False,
        )
        if st.button("Evaluate", type="primary"):
            if not question.strip() or not answer.strip() or not contexts.strip():
                st.error("Question, answer, and at least one context are required.")
                return
            facts = [item.strip() for item in reference.split("\n\n") if item.strip()]
            metrics = RAGEvaluator().evaluate(question, answer, contexts.split("\n\n"), reference_answer=facts[0] if facts else None, required_facts=facts or None)
            st.session_state["latest_evaluation"] = metrics
            st.rerun()
    with results_tab:
        metrics = st.session_state.get("latest_evaluation")
        if not metrics:
            st.info("Run an evaluation to populate the diagnostic view.")
            return
        columns = st.columns(4)
        for column, (name, value) in zip(columns, metrics.items()):
            column.metric(name.replace("_", " ").title(), f"{value:.0%}")
        chart = go.Figure(go.Bar(x=[name.replace("_", " ").title() for name in metrics], y=list(metrics.values()), marker_color="#818CF8"))
        chart.update_layout(template="plotly_dark", yaxis={"range": [0, 1], "tickformat": ".0%"}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})


def _initialize_evaluation_inputs(force: bool = False) -> None:
    """Keep evaluation widgets editable while seeding them from the latest chat turn."""
    latest_question = ""
    latest_answer = ""
    latest_contexts: list[str] = []
    for message in reversed(st.session_state.get("chat_messages", [])):
        if not latest_question and message.get("role") == "user":
            latest_question = str(message.get("content", ""))
        if not latest_answer and message.get("role") == "assistant":
            latest_answer = str(message.get("content", ""))
            latest_contexts = [str(item.get("text", "")) for item in message.get("evidence", [])]
        if latest_question and latest_answer:
            break
    defaults = {
        "evaluation_question": latest_question,
        "evaluation_answer": latest_answer,
        "evaluation_contexts": "\n\n".join(context for context in latest_contexts if context),
        "evaluation_reference": "",
    }
    for key, value in defaults.items():
        if force or key not in st.session_state:
            st.session_state[key] = value


def _render_live_feedback() -> None:
    messages = st.session_state.get("chat_messages", [])
    feedback = st.session_state.get("response_feedback", [])
    answers = [message for message in messages if message.get("role") == "assistant"]
    if not answers:
        return
    st.subheader("Live response quality")
    metrics = []
    evaluator = RAGEvaluator()
    for answer in answers:
        contexts = [item.get("text", "") for item in answer.get("evidence", [])]
        metrics.append(evaluator.evaluate("", answer.get("content", ""), contexts))
    averages = {
        key: sum(item[key] for item in metrics) / len(metrics)
        for key in metrics[0]
    }
    columns = st.columns(4)
    for column, (name, value) in zip(columns, averages.items()):
        column.metric(name.replace("_", " ").title(), f"{value:.0%}")
    positive = sum(item["feedback"] == "Helpful" for item in feedback)
    st.caption(f"{positive} helpful responses · {len(feedback) - positive} responses needing review")
