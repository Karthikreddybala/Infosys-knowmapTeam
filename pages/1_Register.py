"""
pages/1_Register.py — User Registration Page.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.auth_manager import register_user

st.set_page_config(page_title="KnowMap — Register", page_icon="📝", layout="centered")
from ui_setup import add_background
add_background()

st.markdown("<h1 style='text-align:center;color:#7eb8f7;'>📝 Create Account</h1>", unsafe_allow_html=True)
st.markdown("""
<div style="
    background: rgba(30,144,255,0.08);
    border: 1px solid rgba(30,144,255,0.25);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
    color: #7eb8f7;
    margin-bottom: 1rem;
    text-align: center;
">
    🔒 <strong>Secured with JWT</strong> — Your session will be protected by a signed JSON Web Token.
    Passwords are hashed and never stored in plain text.
</div>
""", unsafe_allow_html=True)
st.divider()

DOMAINS = ["AI", "Cybersecurity"]

with st.form("register_form"):
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username *")
        password = st.text_input("Password *", type="password")
    with col2:
        email = st.text_input("Email *")
        confirm = st.text_input("Confirm Password *", type="password")

    st.markdown("**Select your Knowledge Domains:**")
    selected_domains = []
    cols = st.columns(len(DOMAINS))
    for i, d in enumerate(DOMAINS):
        if cols[i].checkbox(d, value=(d == "AI")):
            selected_domains.append(d)

    submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

if submitted:
    if not username or not email or not password or not confirm:
        st.error("All fields are required.")
    elif password != confirm:
        st.error("Passwords do not match.")
    elif len(password) < 6:
        st.error("Password must be at least 6 characters.")
    elif not selected_domains:
        st.error("Select at least one domain.")
    else:
        ok, msg = register_user(username, email, password, selected_domains)
        if ok:
            st.success(f"✅ {msg} Please log in.")
            st.balloons()
        else:
            st.error(msg)

st.divider()
if st.button("← Back to Login"):
    st.switch_page("app.py")
