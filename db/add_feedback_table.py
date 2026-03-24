import sys
import os
import psycopg2

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def add_feedback_table():
    sql = """
    CREATE TABLE IF NOT EXISTS feedback (
        id              SERIAL PRIMARY KEY,
        user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
        feedback_type   VARCHAR(50) NOT NULL,  -- 'website' or 'graph'
        reference_id    INTEGER,               -- e.g., graph_id if feedback_type is 'graph'
        rating          INTEGER CHECK (rating >= 1 AND rating <= 5),
        comments        TEXT,
        created_at      TIMESTAMP DEFAULT NOW()
    );
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("Feedback table created successfully (if it didn't already exist).")
    except Exception as e:
        print(f"Error creating feedback table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_feedback_table()
