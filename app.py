"""
app.py — KnowMap Entry Point (Login Page).
Initialises the database and handles authentication. Authenticated users
are directed to the Dashboard via the sidebar.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.connection import init_db
from auth.auth_manager import login_user, decode_token

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="FusionGraph",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="auto",
)
from ui_setup import add_background
add_background()

# ── Init DB on first run ──────────────────────────────────
@st.cache_resource(show_spinner="Connecting to database...")
def _init():
    try:
        init_db()
        return True
    except Exception as e:
        return str(e)

db_status = _init()



# ── Auth state helper ─────────────────────────────────────
def get_current_user():
    token = st.session_state.get("jwt_token")
    if not token:
        return None
    payload = decode_token(token)
    return payload  # {user_id, role, exp} or None

# ── If already logged in, redirect ───────────────────────
user = get_current_user()
if user:
    st.switch_page("pages/2_Dashboard.py")

# ── Login UI ──────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;'>FusionGraph: A cross-domain knowledge mapping tool</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;'>Real-Time Knowledge Graph Extraction & Semantic Search</p>",
            unsafe_allow_html=True)
st.divider()

if isinstance(db_status, str):
    st.error(f"❌ Database connection failed: {db_status}\n\nPlease check your `.env` credentials and ensure PostgreSQL is running.")
    st.stop()

col1, col2, col3 = st.columns([1, 1.4, 1])
with col2:
    st.markdown("### 🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            token, msg = login_user(username, password)
            if token:
                st.session_state["jwt_token"] = token
                st.success(msg)
                st.switch_page("pages/2_Dashboard.py")
            else:
                st.error(msg)

    st.markdown("")
    st.markdown("""
    <div style="
        background: rgba(30,144,255,0.08);
        border: 1px solid rgba(30,144,255,0.25);
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.8rem;
        color: #7eb8f7;
        margin-bottom: 0.8rem;
    ">
        🔒 <strong>Secured with JWT</strong> — Sessions are authenticated using signed JSON Web Tokens.
        Your credentials are never stored in plain text.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("Don't have an account?")
    if st.button("📝 Register Here", use_container_width=True):
        st.switch_page("pages/1_Register.py")
