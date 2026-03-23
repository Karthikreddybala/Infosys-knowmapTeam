"""
auth/auth_manager.py — User authentication: bcrypt password hashing + PyJWT tokens.
"""
from __future__ import annotations
import bcrypt
import jwt
import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import JWT_SECRET, JWT_ALGO, JWT_EXPIRY_HOURS
from db.connection import run_query, run_insert


# ──────────────────────────────────────────────
# Password helpers
# ──────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt. Returns the hash as a UTF-8 string."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Returns True if plain matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ──────────────────────────────────────────────
# JWT helpers
# ──────────────────────────────────────────────

def create_token(user_id: int, role: str = "user") -> str:
    """Create a signed JWT token containing user_id and role."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT. Returns payload dict or None if invalid/expired."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ──────────────────────────────────────────────
# DB helpers
# ──────────────────────────────────────────────

def register_user(username: str, email: str, password: str, domains: list) -> tuple[bool, str]:
    """
    Insert a new user into the DB.
    Returns (success: bool, message: str).
    """
    # Check duplicates
    existing = run_query(
        "SELECT id FROM users WHERE username=%s OR email=%s",
        (username, email)
    )
    if existing:
        return False, "Username or email already exists."

    pw_hash = hash_password(password)
    run_insert(
        "INSERT INTO users (username, email, password_hash, domain_preferences) VALUES (%s,%s,%s,%s)",
        (username, email, pw_hash, domains)
    )
    return True, "Registration successful!"


def login_user(username: str, password: str) -> tuple[str | None, str]:
    """
    Verify credentials.
    Returns (token: str | None, message: str).
    """
    rows = run_query(
        "SELECT id, password_hash, role FROM users WHERE username=%s",
        (username,)
    )
    if not rows:
        return None, "User not found."

    user = rows[0]
    if not verify_password(password, user["password_hash"]):
        return None, "Incorrect password."

    token = create_token(user["id"], user["role"])
    return token, "Login successful!"


def get_user_by_id(user_id: int) -> dict | None:
    """Fetch user record by ID."""
    rows = run_query(
        "SELECT id, username, email, domain_preferences, role, created_at FROM users WHERE id=%s",
        (user_id,)
    )
    return rows[0] if rows else None


def update_user_preferences(user_id: int, domains: list):
    """Update domain preferences for a user."""
    run_insert(
        "UPDATE users SET domain_preferences=%s WHERE id=%s",
        (domains, user_id)
    )
