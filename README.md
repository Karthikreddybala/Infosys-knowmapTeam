# 🧬 FusionGraph — Real-Time Knowledge Graph Extraction & Semantic Search

> Built with Streamlit · PostgreSQL · spaCy · sentence-transformers · PyTorch

FusionGraph is an AI-powered, full-stack web application that automatically extracts knowledge graphs from raw text, research papers, Wikipedia articles, CSV files, and PDFs. It then lets users interactively visualise, query, and semantically search the resulting graph — all through a clean, secure, multi-user platform.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🔐 **Authentication** | JWT-secured login & registration with bcrypt password hashing |
| 🏠 **Dashboard** | Personal stats — datasets processed, graphs saved, total triplets |
| ⚙️ **NLP Pipeline** | Named Entity Recognition + Relation Extraction from 5 source types |
| 🌐 **Knowledge Graph** | Interactive force-directed graph with ontology alignment & export |
| 🔍 **Semantic Search** | MiniLM sentence-embedding search across all saved triplets |
| 🛡️ **Admin Panel** | Pipeline monitor, graph refinement, quality metrics, user management |
| 💬 **Feedback** | Per-graph & platform-wide star ratings with admin review |

---

## 🗂️ Project Structure

```
knowmap/
├── app.py                      # Entry point — Login page
├── config.py                   # Centralised config loader (.env / Streamlit secrets)
├── ui_setup.py                 # Shared background & global UI helpers
├── requirements.txt            # Python dependencies
├── packages.txt                # System-level apt packages (Streamlit Cloud)
│
├── pages/
│   ├── 1_Register.py           # User registration
│   ├── 2_Dashboard.py          # Personal dashboard
│   ├── 3_NLP_Pipeline.py       # Data ingestion & NLP extraction
│   ├── 4_Knowledge_Graph.py    # Graph builder & visualiser
│   ├── 5_Semantic_Search.py    # Embedding-based search
│   ├── 6_Admin.py              # Admin-only control panel
│   └── 7_Feedback.py           # User feedback submission
│
├── auth/
│   └── auth_manager.py         # Login, registration, JWT encode/decode
├── data_pipeline/
│   ├── data_sources.py         # Wikipedia, ArXiv, CSV, TXT, PDF loaders
│   ├── ner_extraction.py       # spaCy NER
│   ├── preprocessing.py        # Text cleaning & sentence splitting
│   ├── relation_extraction.py  # Dependency-parse relation extraction
│   └── triplet_formation.py    # (Head, Relation, Tail) triplet builder
├── graph/
│   ├── graph_builder.py        # NetworkX graph assembly
│   ├── graph_visualizer.py     # streamlit-agraph renderer
│   └── ontology_alignment.py   # Cross-domain entity alignment
├── search/
│   └── semantic_search.py      # MiniLM cosine-similarity search
├── admin/
│   └── metrics.py              # System-wide stats & admin log helpers
├── db/
│   ├── connection.py           # psycopg2 pool, run_query / run_insert helpers
│   └── schema.sql              # Full PostgreSQL DDL (7 tables)
│
└── .streamlit/
    ├── config.toml             # Theme + server settings
    └── secrets.toml            # 🔒 LOCAL ONLY — never commit
```

---

## 🚀 Quick Start (Local)

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.11+   |
| PostgreSQL  | 14+     |
| pip         | Latest  |

### 1 — Clone the repo

```bash
git clone https://github.com/<your-org>/knowmap.git
cd knowmap
```

### 2 — Create the PostgreSQL database

```sql
CREATE DATABASE knowmap;
-- Optional: dedicated user
CREATE USER knowmap_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE knowmap TO knowmap_user;
```

### 3 — Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=knowmap
DB_USER=postgres
DB_PASSWORD=your_password_here

# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=paste_generated_secret_here

# Optional
NEWS_API_KEY=
```

### 4 — Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 5 — Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

### 6 — Create your first admin account

1. Click **Register Here** and sign up
2. In psql / pgAdmin, promote your account:

```sql
UPDATE users SET role='admin' WHERE username='your_username';
```

---

## ☁️ Deploy on Streamlit Cloud

### 1 — Push to GitHub

Make sure `.env` and `.streamlit/secrets.toml` are listed in `.gitignore` (they are by default).

### 2 — Connect the repo on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app** → select your repository
3. Set **Main file path** to `app.py`

### 3 — Add secrets

In the Streamlit Cloud dashboard → **Settings → Secrets**, paste:

```toml
DB_HOST     = "your-cloud-db-host"
DB_PORT     = "5432"
DB_NAME     = "knowmap"
DB_USER     = "knowmap_user"
DB_PASSWORD = "your_secure_password"
JWT_SECRET  = "your_generated_hex_secret"
NEWS_API_KEY = ""
```

> **Recommended cloud PostgreSQL providers:** [Neon](https://neon.tech) (free tier), [Supabase](https://supabase.com), [Railway](https://railway.app)

### 4 — System packages

`packages.txt` already lists the required apt packages for Streamlit Cloud:

```
libgomp1
libpq-dev
python3-dev
build-essential
```

### 5 — spaCy model

The `en_core_web_sm` model is included directly in `requirements.txt` as a wheel URL — no extra steps needed on Streamlit Cloud.

---

## 🗃️ Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Accounts with roles (`user` / `admin`) |
| `datasets` | Data ingestion records (source type, row count) |
| `processed_sentences` | NLP-extracted sentences + entities/relations JSON |
| `graphs` | Saved knowledge graph metadata |
| `triplets` | (head, relation, tail, domain) rows linked to graphs |
| `admin_logs` | Admin action audit trail |
| `feedback` | User star-ratings and comments |

Tables are created automatically on first run via `db/connection.py → init_db()`.  
You can also initialise manually:

```bash
psql -U postgres -d knowmap -f db/schema.sql
```

---

## ⚙️ Configuration Reference

All settings are loaded by `config.py` — it checks Streamlit secrets first, then `.env`, then falls back to defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `knowmap` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | *(empty)* | Database password |
| `JWT_SECRET` | `change_this_secret` | HMAC-SHA256 signing key |
| `JWT_EXPIRY_HOURS` | `24` | Token lifetime |
| `NEWS_API_KEY` | *(empty)* | Optional NewsAPI key |

---

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit >= 1.31` | Web UI framework |
| `streamlit-agraph` | Interactive force-directed graph |
| `psycopg2-binary` | PostgreSQL driver |
| `bcrypt` | Password hashing |
| `PyJWT` | JSON Web Token auth |
| `python-dotenv` | `.env` loader |
| `spacy` + `en_core_web_sm` | NER & dependency parsing |
| `wikipedia-api` | Live Wikipedia fetching |
| `arxiv` | Live ArXiv paper fetching |
| `sentence-transformers` | MiniLM semantic embeddings |
| `torch` (CPU) | PyTorch backend for embeddings |
| `PyMuPDF` | PDF text extraction |
| `pandas` | CSV handling & dataframes |
| `networkx` | Graph analytics |
| `transformers` | DistilBART summarisation (optional) |

---

## 🔒 Security Notes

- Passwords are hashed with **bcrypt** before storage — never stored in plain text.
- Sessions are authenticated via **signed JWTs** (HS256).
- `.env` and `secrets.toml` are excluded from version control via `.gitignore`.
- Admin routes are protected by a server-side role check on every page load.
- Never commit real credentials — rotate your `JWT_SECRET` before going public.

---

## 🛠️ Troubleshooting

| Error | Fix |
|-------|-----|
| `could not connect to server` | Check `DB_HOST` / `DB_PORT`, ensure PostgreSQL is running |
| `password authentication failed` | Verify `DB_USER` / `DB_PASSWORD` |
| `OSError: [E050] en_core_web_sm` | Run `python -m spacy download en_core_web_sm` |
| `ModuleNotFoundError: fitz` | Run `pip install PyMuPDF` |
| `streamlit-agraph not found` | Run `pip install streamlit-agraph` |
| Admin page shows "Admin access only" | Run `UPDATE users SET role='admin' WHERE username='...'` |
| Streamlit Cloud non-zero exit on install | Confirm `packages.txt` has `libgomp1` and `libpq-dev` |

---

## 🤝 Contributing

1. Fork the repository and create a feature branch
2. Make your changes with clear, descriptive commits
3. Open a pull request with a description of what was changed and why

---

## 📄 License

This project is developed for Infosys internal use. All rights reserved.

---

*FusionGraph — built by the KnowMap Team @ Infosys · 2025*
