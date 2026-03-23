"""
data_pipeline/ner_extraction.py — Named Entity Recognition using spaCy.
"""
import spacy

try:
    _nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    _nlp = spacy.load("en_core_web_sm")

NAMED_LABELS = {"ORG", "PERSON", "GPE", "LOC", "PRODUCT", "EVENT", "LAW", "NORP", "WORK_OF_ART"}


def extract_entities(text: str) -> list[dict]:
    """
    Extract named entities + noun chunks from a sentence.
    Returns list of {text, label} dicts.
    """
    doc = _nlp(text)
    seen = set()
    entities = []

    # spaCy NER
    for ent in doc.ents:
        key = ent.text.strip().lower()
        if key not in seen and ent.label_ in NAMED_LABELS:
            entities.append({"text": ent.text.strip(), "label": ent.label_})
            seen.add(key)

    # Noun chunks as CONCEPT fallback
    for chunk in doc.noun_chunks:
        clean = " ".join(t.text for t in chunk if t.pos_ not in ("DET", "PRON"))
        key = clean.strip().lower()
        if key and key not in seen and len(clean) > 3:
            entities.append({"text": clean.strip(), "label": "CONCEPT"})
            seen.add(key)

    return entities


def get_spacy_doc(text: str):
    """Return a spaCy Doc for shared use in relation extraction."""
    return _nlp(text)
