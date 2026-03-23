"""
graph/graph_builder.py — Build NetworkX DiGraph from triplets and compute analytics.
"""
import networkx as nx


def build_graph(triplets: list[dict]) -> nx.DiGraph:
    """Construct a directed graph from a list of {head, relation, tail} dicts."""
    G = nx.DiGraph()
    for t in triplets:
        G.add_edge(t["head"], t["tail"],
                   relation=t.get("relation", ""),
                   domain=t.get("domain", "General"))
    return G


def get_analytics(G: nx.DiGraph) -> dict:
    """Return key graph statistics."""
    if G.number_of_nodes() == 0:
        return {"nodes": 0, "edges": 0, "density": 0.0, "top_nodes": []}
    degree_dict = dict(G.degree())
    top_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": round(nx.density(G), 4),
        "top_nodes": top_nodes,
        "degree_dict": degree_dict,
    }


def get_subgraph_for_node(G: nx.DiGraph, node: str, depth: int = 1) -> nx.DiGraph:
    """Return a subgraph of all neighbours within `depth` hops of `node`."""
    nodes = {node}
    frontier = {node}
    for _ in range(depth):
        next_frontier = set()
        for n in frontier:
            next_frontier.update(G.successors(n))
            next_frontier.update(G.predecessors(n))
        nodes.update(next_frontier)
        frontier = next_frontier
    return G.subgraph(nodes).copy()
