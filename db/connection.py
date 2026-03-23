"""
db/connection.py — PostgreSQL connection using psycopg2.
Provides get_connection() and init_db() to set up schema on first run.
"""
import psycopg2
import psycopg2.extras
import os
import sys

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    """Return a new psycopg2 connection. Caller is responsible for closing it."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def init_db():
    """
    Creates all tables defined in db/schema.sql if they do not exist.
    Called once on application startup.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
    finally:
        conn.close()


def run_query(sql: str, params=None, fetch: bool = True):
    """
    Helper: run a SELECT and return list of dict rows.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            if fetch:
                return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
    return []


def run_insert(sql: str, params=None, returning: bool = False):
    """
    Helper: run an INSERT/UPDATE/DELETE.
    If returning=True, returns the first column of the first row (e.g. new id).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            result = None
            if returning:
                result = cur.fetchone()[0]
        conn.commit()
        return result
    finally:
        conn.close()
