"""
data_pipeline/triplet_formation.py — Combines NER + SVO into final triplets.
Saves results to PostgreSQL processed_sentences table.
"""
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.ner_extraction import extract_entities, get_spacy_doc
from data_pipeline.relation_extraction import extract_svo
from data_pipeline.preprocessing import clean_text, segment_sentences
from db.connection import run_insert, run_query


def form_triplets(text: str, domain: str = "General") -> dict:
    """
    Full pipeline for a single sentence:
    clean → spaCy parse → NER entities → SVO triplets.
    Returns {sentence, entities, relations}.
    """
    cleaned = clean_text(text)
    doc = get_spacy_doc(cleaned)
    entities = extract_entities(cleaned)
    relations = extract_svo(doc)

    # Tag each relation with domain
    for r in relations:
        r["domain"] = domain

    return {
        "sentence": cleaned,
        "entities": entities,
        "relations": relations,
    }


def run_pipeline_on_sentences(sentences: list[str], domain: str = "General",
                               progress_callback=None) -> list[dict]:
    """
    Run the NLP pipeline over a list of sentences.
    Optionally call progress_callback(current, total) for UI updates.
    """
    results = []
    total = len(sentences)
    for i, sent in enumerate(sentences):
        try:
            results.append(form_triplets(sent, domain))
        except Exception:
            pass
        if progress_callback:
            progress_callback(i + 1, total)
    return results


def save_results_to_db(dataset_id: int, results: list[dict]):
    """
    Persist processed sentences (with entities + relations) to PostgreSQL.
    """
    for item in results:
        run_insert(
            """INSERT INTO processed_sentences
               (dataset_id, sentence, entities_json, relations_json, domain)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                dataset_id,
                item["sentence"],
                json.dumps(item["entities"]),
                json.dumps(item["relations"]),
                item["relations"][0]["domain"] if item["relations"] else "General",
            )
        )


def create_dataset_record(user_id: int, name: str, source_type: str, row_count: int) -> int:
    """Insert a dataset record and return its new id."""
    return run_insert(
        """INSERT INTO datasets (user_id, name, source_type, row_count)
           VALUES (%s, %s, %s, %s) RETURNING id""",
        (user_id, name, source_type, row_count),
        returning=True
    )


def load_triplets_from_db(dataset_id: int) -> list[dict]:
    """Load all relations extracted from a specific dataset."""
    rows = run_query(
        "SELECT relations_json, domain FROM processed_sentences WHERE dataset_id=%s",
        (dataset_id,)
    )
    triplets = []
    for row in rows:
        rels = json.loads(row["relations_json"])
        for r in rels:
            triplets.append({
                "head": r.get("head", ""),
                "relation": r.get("relation", ""),
                "tail": r.get("tail", ""),
                "domain": r.get("domain", row.get("domain", "General")),
            })
    return [t for t in triplets if t["head"] and t["tail"]]
