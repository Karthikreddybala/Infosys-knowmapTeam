-- KnowMap PostgreSQL Schema
-- Run this as the postgres superuser:
--   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d knowmap -f db/schema.sql

-- (Note: Cloud database users from Neon or Supabase already own the schema and tables they create)

-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
    id                  SERIAL PRIMARY KEY,
    username            VARCHAR(80)  UNIQUE NOT NULL,
    email               VARCHAR(150) UNIQUE NOT NULL,
    password_hash       TEXT         NOT NULL,
    domain_preferences  TEXT[]       DEFAULT '{}',
    role                VARCHAR(20)  DEFAULT 'user',
    created_at          TIMESTAMP    DEFAULT NOW()
);

-- 2. DATASETS
CREATE TABLE IF NOT EXISTS datasets (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(200) NOT NULL,
    source_type VARCHAR(50)  NOT NULL,  -- 'wikipedia','arxiv','csv','txt','pdf'
    row_count   INTEGER      DEFAULT 0,
    created_at  TIMESTAMP    DEFAULT NOW()
);

-- 3. PROCESSED SENTENCES
CREATE TABLE IF NOT EXISTS processed_sentences (
    id              SERIAL PRIMARY KEY,
    dataset_id      INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    sentence        TEXT    NOT NULL,
    entities_json   TEXT    DEFAULT '[]',
    relations_json  TEXT    DEFAULT '[]',
    domain          VARCHAR(100) DEFAULT 'General',
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 4. GRAPHS
CREATE TABLE IF NOT EXISTS graphs (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(200) NOT NULL,
    description TEXT         DEFAULT '',
    created_at  TIMESTAMP    DEFAULT NOW()
);

-- 5. TRIPLETS
CREATE TABLE IF NOT EXISTS triplets (
    id         SERIAL PRIMARY KEY,
    graph_id   INTEGER REFERENCES graphs(id) ON DELETE CASCADE,
    head       TEXT NOT NULL,
    relation   TEXT NOT NULL,
    tail       TEXT NOT NULL,
    domain     VARCHAR(100) DEFAULT 'General',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. ADMIN LOGS
CREATE TABLE IF NOT EXISTS admin_logs (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action     VARCHAR(200) NOT NULL,
    details    TEXT         DEFAULT '',
    created_at TIMESTAMP    DEFAULT NOW()
);

-- 7. FEEDBACK
CREATE TABLE IF NOT EXISTS feedback (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
    feedback_type   VARCHAR(50) NOT NULL,  -- 'website' or 'graph'
    reference_id    INTEGER,               -- e.g., graph_id if feedback_type is 'graph'
    rating          INTEGER CHECK (rating >= 1 AND rating <= 5),
    comments        TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
