"""Knowledge graph extraction and visualization page."""

from __future__ import annotations

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from app.ui.layout import page_header
from backend.graph.graph_builder import GraphBuilder
from config.settings import get_settings


NODE_COLORS = {
    "Document": "#6366F1", "Policy": "#FB7185", "Department": "#2DD4BF",
    "Role": "#86EFAC", "Requirement": "#FACC15", "Rule": "#FB923C",
    "Control": "#C084FC", "Procedure": "#60A5FA", "Concept": "#10B981",
    "Entity": "#38BDF8", "Organization": "#38BDF8", "Chunk Vector": "#818CF8",
}


def render_knowledge_graph() -> None:
    page_header("Knowledge graph", "Extract and explore entities and relationships grounded in processed documents.")
    settings = get_settings()
    builder = GraphBuilder(settings.processed_dir / "knowledge_graph.json")
    controls = st.columns([1, 1, 3])
    if controls[0].button("Build Graph", type="primary", help="Extract entity relationships from processed documents"):
        with st.spinner("Extracting entity relationships..."):
            graph = builder.build_from_processed(settings.processed_dir)
        st.success(f"Graph saved with {graph.number_of_nodes()} entities and {graph.number_of_edges()} relationships.")
    else:
        try:
            graph = builder.load()
        except (OSError, ValueError, TypeError):
            graph = nx.Graph()
    if controls[1].button("Reset Selection"):
        st.session_state["graph_kind_filter"] = "All entity types"
        st.session_state["graph_node_filter"] = "All nodes"
        st.rerun()
    if graph.number_of_nodes() == 0:
        graph = _fallback_graph()
        st.info("Showing an interactive sample network. Build Graph to replace it with extracted entities.")
    kinds = sorted({attributes.get("kind", "Entity") for _, attributes in graph.nodes(data=True)})
    selected_kind = controls[2].selectbox(
        "Filter entity type",
        ["All entity types", *kinds],
        key="graph_kind_filter",
    )
    node_options = ["All nodes", *[str(node) for node in graph.nodes]]
    selected_node = controls[2].selectbox("Select a Node by ID", node_options, key="graph_node_filter")
    st.caption(f"{graph.number_of_nodes()} nodes · {graph.number_of_edges()} relationships")
    graph_column, details_column = st.columns([2.4, 1])
    with graph_column:
        st.plotly_chart(
            _network_figure(graph, selected_kind, selected_node),
            width="stretch",
            config={"displayModeBar": False, "scrollZoom": True},
        )
    with details_column:
        _render_node_details(graph, selected_node)


def _fallback_graph() -> nx.Graph:
    graph = nx.Graph()
    node_types = [
        ("Document", "Employee Policy"),
        ("Document", "Operations Manual"),
        ("Document", "Security Regulation"),
        ("Concept", "Attendance"),
        ("Concept", "Compliance"),
        ("Concept", "Access Control"),
        ("Entity", "NexusCorp"),
        ("Entity", "Employee"),
        ("Entity", "Manager"),
        ("Organization", "HR"),
        ("Organization", "Security"),
        ("Organization", "Operations"),
        ("Chunk Vector", "Policy chunk 01"),
        ("Chunk Vector", "Policy chunk 02"),
        ("Chunk Vector", "Policy chunk 03"),
    ]
    for index, (kind, label) in enumerate(node_types):
        graph.add_node(f"sample-{index}", kind=kind, label=label)
    edges = [(index, (index + 1) % 15) for index in range(15)]
    edges.extend([(0, 4), (1, 5), (2, 6), (3, 7), (8, 12), (9, 13)])
    graph.add_edges_from((f"sample-{left}", f"sample-{right}", {"relation": "RELATED_TO"}) for left, right in edges)
    return graph


def _network_figure(graph: nx.Graph, selected_kind: str, selected_node: str) -> go.Figure:
    positions = nx.spring_layout(graph, seed=42, k=1.5)
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for left, right in graph.edges:
        edge_x.extend([positions[left][0], positions[right][0], None])
        edge_y.extend([positions[left][1], positions[right][1], None])

    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line={"color": "#475569", "width": 1.2},
        hoverinfo="skip",
        name="Relationships",
    ))
    grouped: dict[str, list[tuple[str, dict]]] = {}
    for node, attributes in graph.nodes(data=True):
        grouped.setdefault(attributes.get("kind", "Entity"), []).append((str(node), attributes))
    for kind, nodes in grouped.items():
        node_x = [positions[node][0] for node, _ in nodes]
        node_y = [positions[node][1] for node, _ in nodes]
        labels = [attributes.get("label", node) for node, attributes in nodes]
        highlighted = [
            selected_node != "All nodes" and node == selected_node
            or selected_node == "All nodes" and selected_kind != "All entity types" and kind == selected_kind
            for node, _ in nodes
        ]
        colors = ["#FACC15" if is_highlighted else NODE_COLORS.get(kind, "#94A3B8") for is_highlighted in highlighted]
        opacity = [1.0 if is_highlighted or selected_kind == "All entity types" and selected_node == "All nodes" else 0.22 for is_highlighted in highlighted]
        figure.add_trace(go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            textfont={"color": "#FFFFFF", "size": 11},
            marker={"size": 18, "color": colors, "opacity": opacity, "line": {"color": "#FFFFFF", "width": 1}},
            customdata=[[node, kind, attributes.get("filename", "") or "No source metadata"] for node, attributes in nodes],
            hovertemplate="<b>%{text}</b><br>ID: %{customdata[0]}<br>Type: %{customdata[1]}<br>Source: %{customdata[2]}<extra></extra>",
            name=kind,
        ))
    figure.update_layout(
        height=560,
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin={"l": 0, "r": 0, "t": 10, "b": 10},
        showlegend=True,
        legend={"font": {"color": "#E2E8F0"}, "orientation": "h", "y": 1.02, "x": 0},
        hoverlabel={"bgcolor": "#1E293B", "bordercolor": "#818CF8", "font": {"color": "#FFFFFF"}},
        xaxis={"showline": False, "zeroline": False, "showgrid": False, "showticklabels": False, "visible": False},
        yaxis={"showline": False, "zeroline": False, "showgrid": False, "showticklabels": False, "visible": False},
    )
    return figure


def _render_node_details(graph: nx.Graph, selected_node: str) -> None:
    st.subheader("Node details")
    if selected_node == "All nodes":
        st.caption("Select a node ID to inspect its metadata and relationships.")
        return
    if selected_node not in graph:
        st.warning("That node is no longer available in the current graph.")
        return
    attributes = graph.nodes[selected_node]
    st.markdown(f"**{attributes.get('label', selected_node)}**")
    st.caption(f"ID: {selected_node}")
    st.write({
        "type": attributes.get("kind", "Entity"),
        "source": attributes.get("filename", "No source metadata"),
        "page": attributes.get("page_num", "Not specified"),
    })
    neighbors = list(graph.neighbors(selected_node))
    st.markdown(f"**Connected relationships ({len(neighbors)})**")
    for neighbor in neighbors:
        edge = graph.get_edge_data(selected_node, neighbor) or {}
        st.write(f"{edge.get('relation', 'RELATED_TO')} -> {graph.nodes[neighbor].get('label', neighbor)}")
