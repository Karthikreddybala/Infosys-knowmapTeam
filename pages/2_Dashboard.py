"""
pages/2_Dashboard.py — User Dashboard: profile, saved graphs, datasets.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.auth_manager import decode_token, get_user_by_id, update_user_preferences
from db.connection import run_query

st.set_page_config(page_title="KnowMap — Dashboard", page_icon="🏠", layout="wide")
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
user = get_user_by_id(user_id)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {user['username']}")
    st.caption(f"Role: **{user['role']}**")
    st.caption(f"Email: {user['email']}")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# ── Header ────────────────────────────────────────────────
st.markdown("<h1>🏠 Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"Welcome back, **{user['username']}**!")
st.divider()

# ── Stats row ────────────────────────────────────────────
datasets = run_query("SELECT COUNT(*) AS cnt FROM datasets WHERE user_id=%s", (user_id,))
graphs   = run_query("SELECT COUNT(*) AS cnt FROM graphs WHERE user_id=%s", (user_id,))
triplets = run_query(
    "SELECT COUNT(t.id) AS cnt FROM triplets t JOIN graphs g ON t.graph_id=g.id WHERE g.user_id=%s",
    (user_id,)
)
c1, c2, c3 = st.columns(3)
c1.metric("📂 Datasets Processed", datasets[0]["cnt"] if datasets else 0)
c2.metric("🌐 Graphs Saved",        graphs[0]["cnt"]   if graphs   else 0)
c3.metric("🔗 Total Triplets",      triplets[0]["cnt"] if triplets else 0)
st.divider()

# ── Two columns: preferences + recent graphs ──────────────
col_pref, col_graphs = st.columns([1, 2])

with col_pref:
    st.markdown("### ⚙️ Domain Preferences")
    DOMAINS = ["AI", "Cybersecurity"]
    current = list(user.get("domain_preferences") or [])
    new_sel = []
    for d in DOMAINS:
        if st.checkbox(d, value=(d in current), key=f"pref_{d}"):
            new_sel.append(d)
    if st.button("Save Preferences", use_container_width=True):
        update_user_preferences(user_id, new_sel)
        st.success("Preferences saved!")

with col_graphs:
    st.markdown("### 🌐 Saved Knowledge Graphs")
    saved = run_query(
        "SELECT id, name, description, created_at FROM graphs WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    if saved:
        for g in saved:
            with st.expander(f"📊 {g['name']}  —  {str(g['created_at'])[:10]}"):
                st.write(g["description"] or "No description.")
                tc = run_query("SELECT COUNT(*) AS cnt FROM triplets WHERE graph_id=%s", (g["id"],))
                st.caption(f"Triplets: **{tc[0]['cnt'] if tc else 0}**")
    else:
        st.info("No saved graphs yet. Go to **NLP Pipeline** to create one.")

st.divider()
st.markdown("### 📂 Recent Datasets")
ds = run_query(
    "SELECT name, source_type, row_count, created_at FROM datasets WHERE user_id=%s ORDER BY created_at DESC LIMIT 10",
    (user_id,)
)
if ds:
    st.dataframe(ds, use_container_width=True)
else:
    st.info("No datasets ingested yet. Go to **NLP Pipeline** to start.")
