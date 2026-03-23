"""
data_pipeline/preprocessing.py — Text cleaning and sentence segmentation.
"""
from __future__ import annotations
import re
import spacy

try:
    _nlp_sent = spacy.load("en_core_web_sm", disable=["tagger", "ner", "lemmatizer"])
except OSError:
    _nlp_sent = spacy.blank("en")

if "sentencizer" not in _nlp_sent.pipe_names and "senter" not in _nlp_sent.pipe_names:
    _nlp_sent.add_pipe("sentencizer")


def clean_text(text: str) -> str:
    """Remove noise from raw text."""
    text = str(text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s.,!?;:]", "", text)
    text = text.strip()
    return text


def segment_sentences(text: str) -> list[str]:
    """
    Split a document into valid English sentences.
    Skips very short fragments (< 10 chars).
    """
    cleaned = clean_text(text)
    doc = _nlp_sent(cleaned)
    return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
