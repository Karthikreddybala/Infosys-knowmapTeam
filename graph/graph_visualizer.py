"""
graph/graph_visualizer.py — Interactive knowledge graph rendering with streamlit-agraph.
Reuses the proven highlight + domain-coloring logic from the original codebase.
"""
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

DOMAIN_COLORS = {
    "AI":           "#1E90FF",   # blue
    "Cybersecurity":"#FF6B35",   # orange
    "Climate":      "#3CB371",   # green
    "Business":     "#FFD700",   # gold
    "General":      "#8A8AFF",   # soft violet
    "Cross":        "#B44FFF",   # purple
}
DEFAULT_COLOR = "#8A8AFF"
HIGHLIGHT_NODE  = "#FF4B4B"
HIGHLIGHT_EDGE  = "#FF4B4B"
DIM_COLOR       = "#888888"


def _get_display_triplets(all_triplets: list[dict],
                           highlights: list[dict] | None,
                           limit: int = 200) -> list[dict]:
    """Limit edges to `limit`, always prioritising highlighted ones first."""
    if not highlights:
        return all_triplets[:limit]

    hl_set = set()
    output = []
    for t in highlights:
        if len(output) < limit:
            output.append(t)
            hl_set.add((t["head"], t["relation"], t["tail"]))
    for t in all_triplets:
        if len(output) >= limit:
            break
        if (t["head"], t["relation"], t["tail"]) not in hl_set:
            output.append(t)
    return output


def draw_graph(triplets: list[dict],
               highlight_triplets: list[dict] | None = None,
               key_suffix: str = "") -> None:
    """
    Render an interactive knowledge graph.
    - Nodes are coloured by domain.
    - When highlight_triplets is provided, those nodes/edges are bright red; others are dimmed.
    """
    if not triplets:
        st.info("The knowledge graph is empty. Add some text to build relations.")
        return

    LIMIT = 200
    safe_triplets = _get_display_triplets(triplets, highlight_triplets, LIMIT)

    hl_edges: set = set()
    hl_nodes: set = set()
    if highlight_triplets:
        for t in highlight_triplets:
            hl_edges.add((t["head"], t["relation"], t["tail"]))
            hl_nodes.add(t["head"])
            hl_nodes.add(t["tail"])

    nodes_map: dict = {}
    edges: list = []

    for idx, trip in enumerate(safe_triplets):
        h, r, t = trip["head"], trip["relation"], trip["tail"]
        domain = trip.get("domain", "General")
        is_hl = not highlight_triplets   # if no search active, everything is "highlighted"

        is_hl_edge = is_hl or (h, r, t) in hl_edges
        is_hl_h    = is_hl or h in hl_nodes
        is_hl_t    = is_hl or t in hl_nodes

        base_col = DOMAIN_COLORS.get(domain, DEFAULT_COLOR)

        color_h    = HIGHLIGHT_NODE if (highlight_triplets and is_hl_h)  else base_col
        color_t    = HIGHLIGHT_NODE if (highlight_triplets and is_hl_t)  else base_col
        edge_color = HIGHLIGHT_EDGE if is_hl_edge else DIM_COLOR
        edge_w     = 4 if is_hl_edge else 1
        size_h     = 45 if (highlight_triplets and is_hl_h)  else 28
        size_t     = 45 if (highlight_triplets and is_hl_t)  else 28

        if h not in nodes_map:
            nodes_map[h] = Node(id=h, label=h, size=size_h, shape="box",
                                color={"background": color_h, "border": "white"},
                                font={"color": "white", "size": 14})
        if t not in nodes_map:
            nodes_map[t] = Node(id=t, label=t, size=size_t, shape="box",
                                color={"background": color_t, "border": "white"},
                                font={"color": "white", "size": 14})

        edges.append(Edge(source=h, target=t, label=r,
                          id=f"e_{h}_{t}_{idx}",
                          color=edge_color, width=edge_w))

    # Unique height per tab to avoid Streamlit component ID clash (original trick)
    height_map = {"tab1": 701, "tab2": 702, "tab3": 703, "admin": 704}
    height = height_map.get(key_suffix, 700)

    config = Config(
        width="100%",
        height=height,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F3B0AF",
        collapsible=False,
        edges={"smooth": {"type": "continuous"}},
        interaction={"hover": True, "navigationButtons": True, "zoomView": True},
    )

    if len(triplets) > LIMIT:
        st.caption(
            f"⚠️ Showing {len(safe_triplets)} of {len(triplets)} edges to maintain performance."
        )

    agraph(nodes=list(nodes_map.values()), edges=edges, config=config)
