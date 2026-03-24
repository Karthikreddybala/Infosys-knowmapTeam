"""
config.py — Centralised configuration loader for KnowMap.
On Streamlit Cloud: reads from st.secrets (set in the Cloud dashboard).
Locally:           reads from .env via python-dotenv.
"""
import os

# Load .env for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _get(key: str, default: str = "") -> str:
    """Read from Streamlit secrets first, then env vars, then default."""
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)

# PostgreSQL
DATABASE_URL = _get("DATABASE_URL", "")
DB_HOST     = _get("DB_HOST", "localhost")
DB_PORT     = int(_get("DB_PORT", "5432"))
DB_NAME     = _get("DB_NAME", "knowmap")
DB_USER     = _get("DB_USER", "postgres")
DB_PASSWORD = _get("DB_PASSWORD", "")

# JWT
JWT_SECRET  = _get("JWT_SECRET", "change_this_secret")
JWT_ALGO    = "HS256"
JWT_EXPIRY_HOURS = 24

# Optional APIs
NEWS_API_KEY = _get("NEWS_API_KEY", "")
