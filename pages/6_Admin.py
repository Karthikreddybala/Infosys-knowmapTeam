"""
pages/6_Admin.py — Module 6: Admin Dashboard.
Pipeline monitoring, graph refinement (merge/delete/edit), quality metrics, user management.
Only accessible by users with role='admin'.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.auth_manager import decode_token
from admin.metrics import (
    get_pipeline_stats, get_graph_metrics, get_all_users,
    get_all_datasets, log_admin_action, get_admin_logs
)
from db.connection import run_query, run_insert

st.set_page_config(page_title="KnowMap — Admin", page_icon="🛡️", layout="wide")

# ── Auth Guard ────────────────────────────────────────────
token   = st.session_state.get("jwt_token")
payload = decode_token(token) if token else None
if not payload:
    st.warning("Please log in first.")
    st.switch_page("app.py")
    st.stop()
if payload.get("role") != "admin":
    st.error("🚫 Admin access only. Contact an administrator to upgrade your account.")
    st.stop()

user_id = payload["user_id"]

with st.sidebar:
    st.markdown("### 🧬 KnowMap")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

st.markdown("<h1>🛡️ Admin Dashboard</h1>", unsafe_allow_html=True)
st.divider()

tab_monitor, tab_refine, tab_metrics, tab_users, tab_logs = st.tabs([
    "📡 Pipeline Monitor", "✏️ Graph Refinement", "📊 Quality Metrics",
    "👥 User Management", "📋 Action Logs"
])

# ────────────────────────────────────────────────────────────────
#  Tab 1 — Pipeline Monitor
# ────────────────────────────────────────────────────────────────
with tab_monitor:
    st.markdown("### System-Wide Pipeline Statistics")
    all_ds = get_all_datasets()
    if all_ds:
        st.dataframe(all_ds, use_container_width=True)
        total_rows = sum(d.get("row_count", 0) for d in all_ds)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Datasets", len(all_ds))
        c2.metric("Total Sentences", total_rows)
        # count all triplets system-wide
        total_t = run_query("SELECT COUNT(*) AS cnt FROM triplets")
        c3.metric("Total Triplets (All Users)", total_t[0]["cnt"] if total_t else 0)
    else:
        st.info("No datasets processed yet.")

# ────────────────────────────────────────────────────────────────
#  Tab 2 — Graph Refinement
# ────────────────────────────────────────────────────────────────
with tab_refine:
    st.markdown("### Select a Graph to Refine")
    all_graphs = run_query(
        """SELECT g.id, g.name, u.username, g.created_at
           FROM graphs g JOIN users u ON g.user_id=u.id ORDER BY g.created_at DESC"""
    )
    if not all_graphs:
        st.info("No graphs saved yet.")
    else:
        g_opts = {f"{g['name']} (by {g['username']})": g["id"] for g in all_graphs}
        chosen_g = st.selectbox("Choose graph:", list(g_opts.keys()), key="admin_g")
        g_id     = g_opts[chosen_g]

        triplets = run_query(
            "SELECT id, head, relation, tail, domain FROM triplets WHERE graph_id=%s ORDER BY id",
            (g_id,)
        )
        st.caption(f"**{len(triplets)}** triplets in this graph.")

        # Delete individual triplet
        st.markdown("#### Delete a Triplet")
        if triplets:
            t_labels = {f"[{t['id']}] {t['head']} —{t['relation']}→ {t['tail']}": t["id"] for t in triplets}
            to_delete = st.selectbox("Select triplet to delete:", list(t_labels.keys()), key="del_t")
            if st.button("🗑️ Delete Selected Triplet", type="secondary"):
                t_del_id = t_labels[to_delete]
                run_insert("DELETE FROM triplets WHERE id=%s", (t_del_id,))
                log_admin_action(user_id, "DELETE_TRIPLET", f"Deleted triplet id={t_del_id} from graph {g_id}")
                st.success("Triplet deleted.")
                st.rerun()

        st.markdown("#### Merge Nodes (Rename Head/Tail Globally)")
        col_m1, col_m2 = st.columns(2)
        old_name = col_m1.text_input("Current entity name:", key="merge_old")
        new_name = col_m2.text_input("Replace with:", key="merge_new")
        if st.button("🔀 Merge / Rename Entity", type="primary"):
            if old_name and new_name:
                run_insert("UPDATE triplets SET head=%s WHERE head=%s AND graph_id=%s",
                           (new_name, old_name, g_id))
                run_insert("UPDATE triplets SET tail=%s WHERE tail=%s AND graph_id=%s",
                           (new_name, old_name, g_id))
                log_admin_action(user_id, "MERGE_NODES",
                                 f"Renamed '{old_name}'→'{new_name}' in graph {g_id}")
                st.success(f"All occurrences of '{old_name}' renamed to '{new_name}'.")
            else:
                st.error("Both fields required.")

        # View all triplets in a table
        with st.expander("View all triplets in this graph"):
            st.dataframe(triplets, use_container_width=True)

# ────────────────────────────────────────────────────────────────
#  Tab 3 — Quality Metrics
# ────────────────────────────────────────────────────────────────
with tab_metrics:
    st.markdown("### Knowledge Graph Quality Metrics")
    all_graphs2 = run_query(
        "SELECT g.id, g.name, u.username FROM graphs g JOIN users u ON g.user_id=u.id"
    )
    if not all_graphs2:
        st.info("No saved graphs yet.")
    else:
        g_opts2 = {f"{g['name']} (by {g['username']})": g["id"] for g in all_graphs2}
        chosen_m = st.selectbox("Graph to analyse:", list(g_opts2.keys()), key="metrics_g")
        gm_id    = g_opts2[chosen_m]
        metrics  = get_graph_metrics(gm_id)

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Nodes",          metrics["nodes"])
        mc2.metric("Edges",          metrics["edges"])
        mc3.metric("Avg Degree",     metrics["avg_degree"])
        mc4.metric("Coverage %",     f"{metrics['coverage_pct']}%")

        if metrics["domain_counts"]:
            import pandas as pd
            dc_df = pd.DataFrame(
                list(metrics["domain_counts"].items()), columns=["Domain", "Triplets"]
            ).sort_values("Triplets", ascending=False)
            st.bar_chart(dc_df.set_index("Domain"))

# ────────────────────────────────────────────────────────────────
#  Tab 4 — User Management
# ────────────────────────────────────────────────────────────────
with tab_users:
    st.markdown("### All Users")
    users = get_all_users()
    if users:
        import pandas as pd
        user_df = pd.DataFrame(users)[["id", "username", "email", "role", "created_at"]]
        st.dataframe(user_df, use_container_width=True)

        st.markdown("#### Toggle Admin Role")
        non_admin = [u for u in users if u["role"] != "admin"]
        if non_admin:
            u_opts = {f"{u['username']} ({u['email']})": u["id"] for u in non_admin}
            promote_user = st.selectbox("Make admin:", list(u_opts.keys()), key="promo")
            if st.button("⬆️ Grant Admin Role"):
                uid = u_opts[promote_user]
                run_insert("UPDATE users SET role='admin' WHERE id=%s", (uid,))
                log_admin_action(user_id, "GRANT_ADMIN", f"Granted admin to user id={uid}")
                st.success(f"Admin role granted to {promote_user}!")
                st.rerun()

        admin_users = [u for u in users if u["role"] == "admin" and u["id"] != user_id]
        if admin_users:
            a_opts = {f"{u['username']} ({u['email']})": u["id"] for u in admin_users}
            revoke_user = st.selectbox("Revoke admin from:", list(a_opts.keys()), key="revoke")
            if st.button("⬇️ Revoke Admin Role"):
                uid = a_opts[revoke_user]
                run_insert("UPDATE users SET role='user' WHERE id=%s", (uid,))
                log_admin_action(user_id, "REVOKE_ADMIN", f"Revoked admin from user id={uid}")
                st.success(f"Admin revoked from {revoke_user}.")
                st.rerun()
    else:
        st.info("No users found.")

# ────────────────────────────────────────────────────────────────
#  Tab 5 — Action Logs
# ────────────────────────────────────────────────────────────────
with tab_logs:
    st.markdown("### Recent Admin Actions")
    logs = get_admin_logs(limit=100)
    if logs:
        st.dataframe(logs, use_container_width=True)
    else:
        st.info("No admin actions logged yet.")
