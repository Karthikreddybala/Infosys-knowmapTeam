"""
pages/4_Knowledge_Graph.py — Modules 3 & 4: Graph construction, ontology alignment,
interactive visualisation, and PostgreSQL persistence.
"""
import streamlit as st
import json, io, csv
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.auth_manager import decode_token
from data_pipeline.triplet_formation import load_triplets_from_db
from graph.graph_builder     import build_graph, get_analytics
from graph.graph_visualizer  import draw_graph, DOMAIN_COLORS
from graph.ontology_alignment import align_triplets, detect_cross_domain, infer_domain
from db.connection import run_query, run_insert

st.set_page_config(page_title="KnowMap — Knowledge Graph", page_icon="🌐", layout="wide")

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

st.markdown("<h1>🌐 Knowledge Graph Explorer</h1>", unsafe_allow_html=True)
st.divider()

# ────────────────────────────────────────────────────────────────
#  STEP 1: Select source of triplets
# ────────────────────────────────────────────────────────────────
st.markdown("### Step 1 — Select Triplet Source")
source_mode = st.radio("Load triplets from:",
                        ["📝 Current pipeline session", "💾 Saved dataset (from DB)", "💾 Load saved graph"],
                        horizontal=True)

triplets: list[dict] = []

if source_mode == "📝 Current pipeline session":
    results = st.session_state.get("pipeline_results", [])
    domain  = st.session_state.get("pipeline_domain", "General")
    if results:
        for r in results:
            for rel in r.get("relations", []):
                rel.setdefault("domain", domain)
                triplets.append(rel)
        st.success(f"Loaded **{len(triplets)}** triplets from current session.")
    else:
        st.warning("No pipeline results in session. Run the NLP Pipeline first.")

elif source_mode == "💾 Saved dataset (from DB)":
    datasets = run_query(
        "SELECT id, name, source_type, created_at FROM datasets WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    if datasets:
        ds_opts = {f"{d['name']} [{d['source_type']}] ({str(d['created_at'])[:10]})": d["id"] for d in datasets}
        chosen = st.selectbox("Choose dataset:", list(ds_opts.keys()))
        ds_id  = ds_opts[chosen]
        if st.button("Load Dataset", type="primary"):
            with st.spinner("Loading triplets from DB…"):
                triplets = load_triplets_from_db(ds_id)
                st.session_state["kg_triplets"] = triplets
            st.success(f"Loaded **{len(triplets)}** triplets.")
        triplets = st.session_state.get("kg_triplets", triplets)
    else:
        st.info("No datasets saved yet. Run the NLP Pipeline first.")

else:  # Load saved graph
    graphs = run_query(
        "SELECT id, name, created_at FROM graphs WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    if graphs:
        g_opts = {f"{g['name']} ({str(g['created_at'])[:10]})": g["id"] for g in graphs}
        chosen = st.selectbox("Choose saved graph:", list(g_opts.keys()))
        g_id   = g_opts[chosen]
        if st.button("Load Graph", type="primary"):
            rows = run_query(
                "SELECT head, relation, tail, domain FROM triplets WHERE graph_id=%s",
                (g_id,)
            )
            triplets = [dict(r) for r in rows]
            st.session_state["kg_triplets"] = triplets
            st.success(f"Loaded **{len(triplets)}** triplets from saved graph.")
        triplets = st.session_state.get("kg_triplets", triplets)
    else:
        st.info("No saved graphs yet. Process a dataset and save a graph first.")

if not triplets:
    st.stop()

# ────────────────────────────────────────────────────────────────
#  STEP 2: Ontology Alignment
# ────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### Step 2 — Ontology Alignment & Domain Detection")
col_align1, col_align2 = st.columns(2)
run_align  = col_align1.checkbox("Apply synonym normalisation", value=True)
run_cross  = col_align2.checkbox("Detect cross-domain relations", value=True)

if run_align:
    triplets = align_triplets(triplets)
if run_cross:
    triplets = detect_cross_domain(triplets)

# Re-infer domain if it's still 'General' after detection
for t in triplets:
    if t.get("domain") in ("General", None, ""):
        t["domain"] = infer_domain(f"{t['head']} {t['relation']} {t['tail']}")

# ────────────────────────────────────────────────────────────────
#  STEP 3: Build & Visualise
# ────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### Step 3 — Graph Visualisation & Analytics")

G = build_graph(triplets)
analytics = get_analytics(G)

m1, m2, m3, m4 = st.columns(4)
m1.metric("🔵 Nodes",     analytics["nodes"])
m2.metric("🔗 Edges",     analytics["edges"])
m3.metric("📐 Density",   analytics["density"])
m4.metric("🏆 Top Entity", analytics["top_nodes"][0][0] if analytics["top_nodes"] else "—")

# Domain legend
legend_md = "  ".join([f"<span style='color:{c}'>■</span> {d}" for d, c in DOMAIN_COLORS.items()])
st.markdown(f"**Domain Legend:** {legend_md}", unsafe_allow_html=True)

tab_graph, tab_filter, tab_export, tab_save = st.tabs([
    "📊 Full Graph", "🔎 Filter View", "⬇️ Export", "💾 Save Graph"
])

with tab_graph:
    draw_graph(triplets, key_suffix="tab1")

with tab_filter:
    col_f1, col_f2 = st.columns(2)
    domain_filter = col_f1.multiselect(
        "Filter by domain:", list(DOMAIN_COLORS.keys()),
        default=list(DOMAIN_COLORS.keys())
    )
    degree_dict   = analytics.get("degree_dict", {})
    max_deg       = max(degree_dict.values(), default=1)
    min_degree    = col_f2.slider("Min connections per node:", 1, max(2, min(10, max_deg)), 1)

    filtered = [
        t for t in triplets
        if t.get("domain", "General") in domain_filter
        and degree_dict.get(t["head"], 0) >= min_degree
        and degree_dict.get(t["tail"], 0) >= min_degree
    ]
    st.caption(f"Showing **{len(filtered)}** of {len(triplets)} edges.")
    if filtered:
        draw_graph(filtered, key_suffix="tab2")
    else:
        st.info("No edges match the current filters.")

with tab_export:
    st.markdown("#### Export Knowledge Graph")
    json_data = json.dumps(triplets, indent=2)
    st.download_button("📥 Download JSON", data=json_data,
                        file_name="knowmap_graph.json", mime="application/json",
                        use_container_width=True)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Head", "Relation", "Tail", "Domain"])
    for t in triplets:
        w.writerow([t["head"], t["relation"], t["tail"], t.get("domain", "")])
    st.download_button("📥 Download CSV", data=buf.getvalue(),
                        file_name="knowmap_graph.csv", mime="text/csv",
                        use_container_width=True)

with tab_save:
    st.markdown("#### Save Graph to PostgreSQL")
    g_name = st.text_input("Graph Name", value=st.session_state.get("pipeline_dataset_name", "My Graph"))
    g_desc = st.text_area("Description (optional)", height=80)
    if st.button("💾 Save Graph", type="primary", use_container_width=True):
        if not g_name.strip():
            st.error("Please provide a graph name.")
        elif not triplets:
            st.error("No triplets to save.")
        else:
            with st.spinner("Saving graph to database…"):
                g_id = run_insert(
                    "INSERT INTO graphs (user_id, name, description) VALUES (%s,%s,%s) RETURNING id",
                    (user_id, g_name, g_desc), returning=True
                )
                for t in triplets:
                    run_insert(
                        "INSERT INTO triplets (graph_id, head, relation, tail, domain) VALUES (%s,%s,%s,%s,%s)",
                        (g_id, t["head"], t["relation"], t["tail"], t.get("domain", "General"))
                    )
                st.session_state["saved_graph_id"] = g_id
            st.success(f"✅ Graph **'{g_name}'** saved with {len(triplets)} triplets! (Graph ID: {g_id})")

# ── Inline graph editor ───────────────────────────────────
st.divider()
st.markdown("### ✏️ Edit Graph (Add / Remove Triplets)")
ec1, ec2, ec3, ec4 = st.columns([2, 2, 2, 1])
new_h  = ec1.text_input("Head (Subject)",   key="edit_h")
new_r  = ec2.text_input("Relation (Verb)",  key="edit_r")
new_t  = ec3.text_input("Tail (Object)",    key="edit_t")
new_d  = ec4.selectbox("Domain", list(DOMAIN_COLORS.keys()), key="edit_d")
if st.button("➕ Add Triplet"):
    if new_h and new_r and new_t:
        new_trip = {"head": new_h, "relation": new_r, "tail": new_t, "domain": new_d}
        triplets.append(new_trip)
        st.session_state["kg_triplets"] = triplets
        if "pipeline_results" in st.session_state:
            st.session_state.pipeline_results.append({"sentence": "", "entities": [], "relations": [new_trip]})
        st.success("Triplet added. The graph above will update on next interaction.")
    else:
        st.error("All three fields required.")
