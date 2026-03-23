"""
pages/5_Semantic_Search.py — Module 5: Semantic search over saved knowledge graphs.
Reuses the proven SemanticSearchEngine with MiniLM embeddings.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.auth_manager import decode_token
from search.semantic_search import SemanticSearchEngine
from graph.graph_visualizer import draw_graph
from db.connection import run_query

st.set_page_config(page_title="KnowMap — Semantic Search", page_icon="🔍", layout="wide")
from ui_setup import add_background
add_background()

# ── Auth Guard ────────────────────────────────────────────
token = st.session_state.get("jwt_token")
payload = decode_token(token) if token else None
if not payload:
    st.warning("Please log in first.")
    st.switch_page("app.py")
    st.stop()
user_id = payload["user_id"]

with st.sidebar:
    st.markdown("### 🧬 KnowMap")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

st.markdown("<h1>🔍 Semantic Search & Query</h1>", unsafe_allow_html=True)
st.markdown("Query your knowledge graph using **natural language**. Results are ranked by semantic similarity.")
st.divider()

# ── Load SemanticSearchEngine (cached) ───────────────────
@st.cache_resource(show_spinner="Loading embedding model…")
def get_engine():
    return SemanticSearchEngine()

engine = get_engine()

# ── Select graph ──────────────────────────────────
st.markdown("### Select Knowledge Graph")

graph_source = st.radio("Load from:", ["📝 Current session graph", "💾 Saved graph (DB)"], horizontal=True)

triplets: list[dict] = []

if graph_source == "📝 Current session graph":
    raw_results = st.session_state.get("pipeline_results", [])
    domain = st.session_state.get("pipeline_domain", "General")
    for r in raw_results:
        for rel in r.get("relations", []):
            rel.setdefault("domain", domain)
            triplets.append(rel)
    # Also check if kg_triplets was populated on the Knowledge Graph page
    if not triplets:
        triplets = st.session_state.get("kg_triplets", [])
    if triplets:
        st.success(f"Loaded **{len(triplets)}** triplets from current session.")
    else:
        st.warning("No graph in current session. Run the NLP Pipeline first, or load a saved graph.")
        st.stop()

else:
    graphs = run_query(
        "SELECT id, name, created_at FROM graphs WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    if not graphs:
        st.info("No saved graphs found. Save a graph in the Knowledge Graph page first.")
        st.stop()
    g_opts = {f"{g['name']} ({str(g['created_at'])[:10]})": g["id"] for g in graphs}
    chosen = st.selectbox("Choose graph:", list(g_opts.keys()))
    g_id   = g_opts[chosen]
    if st.button("Load Graph", type="primary"):
        rows = run_query("SELECT head, relation, tail, domain FROM triplets WHERE graph_id=%s", (g_id,))
        triplets = [dict(r) for r in rows]
        st.session_state["search_triplets"] = triplets
        st.success(f"Loaded **{len(triplets)}** triplets.")
    triplets = st.session_state.get("search_triplets", triplets)
    if not triplets:
        st.stop()

# ── Index graph ───────────────────────────────────
st.divider()
st.markdown("### Query the Graph")

with st.spinner("Indexing graph embeddings…"):
    engine.ingest_graph(triplets)

top_k = st.slider("Number of results to return:", 3, 20, 7)
query = st.text_input("Enter your natural language query:",
                       placeholder="e.g. How does AI detect malware?")

if query:
    with st.spinner("Searching knowledge graph…"):
        results = engine.search(query, top_k=top_k)

    if not results:
        st.warning("No matching triplets found.")
    else:
        st.success(f"Found **{len(results)}** semantic matches.")
        result_triplets = [t for t, _ in results]

        # Results table
        with st.expander("📋 Top Matches (Structured)", expanded=True):
            st.table([{
                "Score":    f"{score:.3f}",
                "Subject":  t["head"],
                "Relation": t["relation"],
                "Object":   t["tail"],
                "Domain":   t.get("domain", ""),
            } for t, score in results])

        # Graph view
        st.divider()
        st.markdown("### Graph Visualisation")
        view_mode = st.radio("Display Mode:",
                              ["🔎 Isolated Subgraph", "🌐 Global Context (Highlighted)"],
                              horizontal=True)

        if view_mode == "🔎 Isolated Subgraph":
            st.markdown("#### Semantic Match Subgraph")
            draw_graph(result_triplets, key_suffix="tab2")
        else:
            st.markdown("#### Full Graph — Matches Highlighted in Red")
            draw_graph(triplets, highlight_triplets=result_triplets, key_suffix="tab2")
else:
    # Show full graph when no query entered
    st.markdown("### 🌐 Full Graph Discovery View")
    st.caption("Enter a query above to search. Currently showing the complete graph.")
    draw_graph(triplets, key_suffix="tab3")
