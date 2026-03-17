import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

def get_display_triplets(all_triplets, highlights=None, limit=200):
    """Safely limits the number of rendered edges while prioritizing search highlights."""
    if not highlights:
        return all_triplets[:limit]
        
    output = []
    hl_set = set()
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

def draw_graph(triplets_to_draw, highlight_triplets=None, key_suffix=""):
    """Renders the interactive knowledge graph topology with optional highlights."""
    nodes = []
    edges = []
    added_nodes = set()
    
    # Restrict to safe rendering limits
    display_limit = 200
    safe_triplets = get_display_triplets(triplets_to_draw, highlight_triplets, display_limit)
    
    hl_edges = set()
    hl_nodes = set()
    
    if highlight_triplets:
        for t in highlight_triplets:
            hl_edges.add((t["head"], t["relation"], t["tail"]))
            hl_nodes.add(t["head"])
            hl_nodes.add(t["tail"])
            
    for idx, trip in enumerate(safe_triplets):
        h = trip["head"]
        t = trip["tail"]
        r = trip["relation"]
        
        is_hl_edge = True if not highlight_triplets else (h, r, t) in hl_edges
        is_hl_h = True if not highlight_triplets else h in hl_nodes
        is_hl_t = True if not highlight_triplets else t in hl_nodes
        
        # Style logic: Dim background nodes if there is a search active
        color_h = "#FF4B4B" if is_hl_h else "#1E90FF"
        color_t = "#0068C9" if is_hl_t else "#1E90FF"
        edge_color = "#FF4B4B" if is_hl_edge else "#888888"
        edge_width = 4 if is_hl_edge else 1
        
        size_h = 45 if is_hl_h else 25
        size_t = 45 if is_hl_t else 25
        
        if h not in added_nodes:
            nodes.append(Node(id=h, label=h, size=size_h, shape="box", color={"background": color_h, "border": "white"}, font={"color": "white", "size": 16}))
            added_nodes.add(h)
            
        if t not in added_nodes:
            nodes.append(Node(id=t, label=t, size=size_t, shape="box", color={"background": color_t, "border": "white"}, font={"color": "white", "size": 16}))
            added_nodes.add(t)
            
        edges.append(Edge(source=h, target=t, label=r, id=f"edge_{h}_{t}_{idx}", color=edge_color, width=edge_width))
        
    # Slightly alter height based on suffix to guarantee a unique Streamlit Component ID
    height_val = 700
    if key_suffix == "tab1": height_val = 701
    elif key_suffix == "tab2": height_val = 702
    
    config = Config(
        width='100%', 
        height=height_val, 
        directed=True, 
        physics=True, 
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F3B0AF",
        collapsible=False,
        edges={"smooth": {"type": "continuous"}},
        interaction={"hover": True, "navigationButtons": True, "zoomView": True}
    )
    
    if len(triplets_to_draw) > display_limit:
        st.caption(f"⚠️ Displaying a subset ({len(safe_triplets)}) of the full graph ({len(triplets_to_draw)} edges) to maintain browser performance.")
        
    return agraph(nodes=nodes, edges=edges, config=config)
