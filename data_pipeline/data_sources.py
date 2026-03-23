"""
data_pipeline/data_sources.py — Real data fetchers for all supported source types.
Supports: Wikipedia, ArXiv, CSV, TXT, PDF.
"""
import io
import fitz          # PyMuPDF
import pandas as pd
import arxiv
import wikipediaapi

from data_pipeline.preprocessing import segment_sentences


# ──────────────────────────────────────────────────────────
# Wikipedia
# ──────────────────────────────────────────────────────────

def fetch_wikipedia(topic: str, max_sentences: int = 500) -> list[str]:
    """
    Fetch the Wikipedia article for `topic` and return up to max_sentences sentences.
    """
    wiki = wikipediaapi.Wikipedia(language="en", user_agent="KnowMap/1.0")
    page = wiki.page(topic)
    if not page.exists():
        return []
    sentences = segment_sentences(page.text)
    return sentences[:max_sentences]


# ──────────────────────────────────────────────────────────
# ArXiv
# ──────────────────────────────────────────────────────────

def fetch_arxiv(topic: str, max_papers: int = 20) -> list[str]:
    """
    Search ArXiv for `topic`, combine title + abstract into sentences.
    """
    client = arxiv.Client()
    search = arxiv.Search(query=topic, max_results=max_papers,
                          sort_by=arxiv.SortCriterion.Relevance)
    sentences = []
    for result in client.results(search):
        combined = f"{result.title}. {result.summary}"
        sentences.extend(segment_sentences(combined))
    return sentences


# ──────────────────────────────────────────────────────────
# CSV
# ──────────────────────────────────────────────────────────

def load_csv(file_obj, text_column: str | None = None) -> list[str]:
    """
    Read a CSV file. If text_column is given, use that column as text.
    Otherwise concatenate all string columns per row.
    """
    df = pd.read_csv(file_obj)
    sentences = []
    if text_column and text_column in df.columns:
        for val in df[text_column].dropna():
            sentences.extend(segment_sentences(str(val)))
    else:
        str_cols = df.select_dtypes(include="object").columns.tolist()
        for _, row in df.iterrows():
            combined = ". ".join(str(row[c]) for c in str_cols if pd.notna(row[c]))
            sentences.extend(segment_sentences(combined))
    return sentences


def get_csv_columns(file_bytes: bytes) -> list[str]:
    """Return column names of a CSV (for UI column selector)."""
    df = pd.read_csv(io.BytesIO(file_bytes), nrows=0)
    return df.columns.tolist()


# ──────────────────────────────────────────────────────────
# Plain Text
# ──────────────────────────────────────────────────────────

def load_txt(file_bytes: bytes) -> list[str]:
    """Decode a .txt file and return its sentences."""
    content = file_bytes.decode("utf-8", errors="ignore")
    return segment_sentences(content)


# ──────────────────────────────────────────────────────────
# PDF
# ──────────────────────────────────────────────────────────

def load_pdf(file_bytes: bytes) -> list[str]:
    """Extract text from a PDF and return its sentences."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return segment_sentences(text)
    except Exception as e:
        raise RuntimeError(f"PDF parsing failed: {e}")
