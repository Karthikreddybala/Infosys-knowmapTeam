"""
config.py — Centralised configuration loader for KnowMap.
Reads all settings from the .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 5432))
DB_NAME     = os.getenv("DB_NAME", "knowmap")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# JWT
JWT_SECRET  = os.getenv("JWT_SECRET", "change_this_secret")
JWT_ALGO    = "HS256"
JWT_EXPIRY_HOURS = 24

# Optional APIs
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
