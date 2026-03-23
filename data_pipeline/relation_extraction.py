"""
data_pipeline/relation_extraction.py — Subject-Verb-Object triplet extraction
via spaCy dependency parsing. Reuses the proven SVO logic from the original codebase.
"""
from __future__ import annotations

def _get_full_noun_chunk(token, doc) -> str:
    """Expand a root token to its full noun phrase, stripping determiners."""
    for chunk in doc.noun_chunks:
        if chunk.root == token:
            clean = [t.text for t in chunk if t.pos_ not in ("DET", "PRON")]
            return " ".join(clean) if clean else chunk.text
    return token.text


def _get_verb_phrase(token) -> str:
    """Expand a verb with any particle or negation children."""
    phrase = [token.text]
    for child in token.children:
        if child.dep_ in ("prt", "neg"):
            if child.i < token.i:
                phrase.insert(0, child.text)
            else:
                phrase.append(child.text)
    return " ".join(phrase)


def extract_svo(doc) -> list[dict]:
    """
    Traverse the dependency tree and extract Subject–Verb–Object triplets.
    Returns list of {head, relation, tail} dicts.
    """
    triplets = []
    seen = set()

    for token in doc:
        if token.pos_ == "VERB":
            subjects = [c for c in token.children if c.dep_ in ("nsubj", "nsubjpass", "csubj")]
            objects  = [c for c in token.children if c.dep_ in ("dobj", "pobj", "attr", "prep")]

            # Expand prepositional objects
            expanded_objects = []
            for obj in objects:
                if obj.dep_ == "prep":
                    expanded_objects.extend(c for c in obj.children if c.dep_ == "pobj")
                else:
                    expanded_objects.append(obj)

            if subjects and expanded_objects:
                for subj in subjects:
                    for obj in expanded_objects:
                        h = _get_full_noun_chunk(subj, doc)
                        t = _get_full_noun_chunk(obj, doc)
                        r = _get_verb_phrase(token).lower()
                        key = (h.lower(), r, t.lower())
                        if key not in seen and h.lower() != t.lower():
                            seen.add(key)
                            triplets.append({"head": h, "relation": r, "tail": t})
    return triplets
