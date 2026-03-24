import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.auth_manager import decode_token
from db.connection import run_insert

st.set_page_config(page_title="KnowMap — Feedback", page_icon="💬", layout="wide")
from ui_setup import add_background, feedback_form
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

st.markdown("<h1>💬 Platform Feedback</h1>", unsafe_allow_html=True)
st.markdown("We'd love to hear your thoughts on how to improve the KnowMap platform!")
st.divider()

feedback_form(user_id=user_id, target_type="website")
