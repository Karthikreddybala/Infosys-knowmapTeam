# KnowMap — Installation & Setup Guide

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.11+   |
| PostgreSQL  | 14+     |
| pip         | Latest  |

---

## Step 1 — Create the PostgreSQL Database

Open **pgAdmin** or **psql** and run:

```sql
CREATE DATABASE knowmap;
```

If you want a dedicated user (recommended):

```sql
CREATE USER knowmap_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE knowmap TO knowmap_user;
```

---

## Step 2 — Configure the `.env` File

Open `.env` in the project root and fill in your credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=knowmap
DB_USER=postgres          # or knowmap_user
DB_PASSWORD=your_password_here

# Generate a secret: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=paste_your_generated_secret_here

# Optional — leave blank if you don't have one
NEWS_API_KEY=
```

---

## Step 3 — Install Python Dependencies

Open a terminal in the project root and run:

```powershell
pip install -r requirements.txt
```

Then download the spaCy English model:

```powershell
python -m spacy download en_core_web_sm
```

---

## Step 4 — Initialise the Database Schema

The database tables are created **automatically** when you first run the app.
But you can also run it manually:

```powershell
psql -U postgres -d knowmap -f db/schema.sql
```

---

## Step 5 — Run the Application

```powershell
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## Step 6 — Create Your First Admin Account

1. Open the app → click **Register Here**
2. Create an account (any username/password)
3. In **psql** or **pgAdmin**, promote your user to admin:

```sql
UPDATE users SET role='admin' WHERE username='your_username';
```

---

## Full Dependency List (installed by requirements.txt)

| Package | Purpose |
|---------|---------|
| `streamlit>=1.31` | Web UI |
| `streamlit-agraph` | Interactive graph rendering |
| `psycopg2-binary` | PostgreSQL driver |
| `bcrypt` | Password hashing |
| `PyJWT` | JSON Web Tokens |
| `python-dotenv` | Load `.env` file |
| `spacy` + `en_core_web_sm` | NLP: NER, dependency parse |
| `wikipedia-api` | Real Wikipedia data fetching |
| `arxiv` | Real ArXiv paper fetching |
| `sentence-transformers` | MiniLM semantic search embeddings |
| `torch` | PyTorch backend for embeddings |
| `PyMuPDF (fitz)` | PDF text extraction |
| `pandas` | CSV loading and data handling |
| `networkx` | Graph analytics |
| `transformers` | DistilBART document summarisation (optional) |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `could not connect to server` | Check DB_HOST/PORT in `.env`, ensure PostgreSQL is running |
| `password authentication failed` | Check DB_USER/DB_PASSWORD in `.env` |
| `OSError: [E050] ... en_core_web_sm` | Run `python -m spacy download en_core_web_sm` |
| `ModuleNotFoundError: No module named 'fitz'` | Run `pip install PyMuPDF` |
| `streamlit-agraph not found` | Run `pip install streamlit-agraph` |
| Admin page shows "Admin access only" | Run the SQL `UPDATE users SET role='admin'...` above |
