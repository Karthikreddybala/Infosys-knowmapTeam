"""
nlp_pipeline.py — Full NLP Pipeline for KNOWMAP
Datasets: ArXiv AI  ×  AI/ML Cybersecurity
-------------------------------------------------
Run:  python nlp_pipeline.py
Output: output_triples.json / output_triples.csv / output_entities.json
"""

import pandas as pd
import json
from data_loader        import load_combined_dataset
from ner_spacy          import extract_entities_with_domain
from relation_extraction import generate_triples


def run_pipeline_on_row(text, domain):
    """Process a single row through the full NLP pipeline."""
    result = {
        "original_text": text[:200],
        "domain":  domain,
        "entities": [],
        "triples":  []
    }
    try:
        result["entities"] = extract_entities_with_domain(text, domain)
        result["triples"]  = generate_triples(text, domain)
    except Exception as e:
        result["error"] = str(e)
    return result


def run_full_pipeline(max_rows=300):
    print("=" * 60)
    print("  KNOWMAP NLP Pipeline  —  AI × Cybersecurity")
    print("=" * 60)

    df = load_combined_dataset(max_rows=max_rows)

    all_results  = []
    all_triples  = []
    all_entities = []

    total = len(df)
    print(f"\nProcessing {total} texts...\n")

    for i, row in df.iterrows():
        if i % 50 == 0:
            print(f"  Progress: {i}/{total}")
        result = run_pipeline_on_row(row['text'], row['domain'])
        all_results.append(result)
        all_triples.extend(result["triples"])
        all_entities.extend(result["entities"])

    # ── Summary ──────────────────────────────────────
    ai_triples    = [t for t in all_triples if t['domain'] == 'AI']
    cyber_triples = [t for t in all_triples if t['domain'] == 'Cybersecurity']

    print(f"\n{'=' * 60}")
    print("  PIPELINE COMPLETE!")
    print(f"{'=' * 60}")
    print(f"  Total texts processed    : {total}")
    print(f"  Total entities found     : {len(all_entities)}")
    print(f"  Total triples found      : {len(all_triples)}")
    print(f"  AI triples               : {len(ai_triples)}")
    print(f"  Cybersecurity triples    : {len(cyber_triples)}")

    # ── Sample output ─────────────────────────────────
    print("\n--- Sample AI Triples ---")
    for t in ai_triples[:5]:
        print(f"  ({t['subject']}) --{t['relation']}--> ({t['object']})")

    print("\n--- Sample Cybersecurity Triples ---")
    for t in cyber_triples[:5]:
        print(f"  ({t['subject']}) --{t['relation']}--> ({t['object']})")

    # ── Cross-domain preview ──────────────────────────
    print("\n--- Potential Cross-Domain Triples (AI text mentioning security) ---")
    keywords = ["malware", "attack", "threat", "security", "intrusion",
                "detect", "ransomware", "encrypt", "vulnerability"]
    cross = [t for t in ai_triples
             if any(k in t['subject'].lower() or k in t['object'].lower()
                    for k in keywords)]
    for t in cross[:5]:
        print(f"  ({t['subject']}) --{t['relation']}--> ({t['object']})  [AI→Cyber bridge!]")

    # ── Save outputs ──────────────────────────────────
    with open("output_triples.json", "w") as f:
        json.dump(all_triples, f, indent=2)
    print("\n✅ Saved: output_triples.json")

    with open("output_entities.json", "w") as f:
        json.dump(all_entities, f, indent=2)
    print("✅ Saved: output_entities.json")

    pd.DataFrame(all_triples).to_csv("output_triples.csv", index=False)
    print("✅ Saved: output_triples.csv  ← open in Excel to verify!")

    return all_triples, all_entities


# ── RUN ───────────────────────────────────────────────
if __name__ == "__main__":
    triples, entities = run_full_pipeline(max_rows=800)
