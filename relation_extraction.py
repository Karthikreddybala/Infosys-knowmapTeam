import spacy

nlp = spacy.load("en_core_web_sm")

def extract_relations(text):
    """
    Extract Subject → Verb → Object relations using spaCy dependency parsing.
    Returns list of dicts: [{subject, relation, object}]
    """
    doc = nlp(text)
    relations = []

    for token in doc:
        # ROOT token = main verb of the sentence
        if token.dep_ == "ROOT" and token.pos_ == "VERB":

            # Subject — left side of verb
            subjects = [w for w in token.lefts
                        if w.dep_ in ("nsubj", "nsubjpass")]

            # Object — right side of verb
            objects = [w for w in token.rights
                       if w.dep_ in ("dobj", "pobj", "attr")]

            if subjects and objects:
                relations.append({
                    "subject":  subjects[0].text,
                    "relation": token.lemma_,  # base form e.g. "detects" → "detect"
                    "object":   objects[0].text
                })
    return relations


def generate_triples(text, domain):
    """
    Convert text into (subject, relation, object, domain) triples.
    This is the direct input format for the Knowledge Graph.
    """
    relations = extract_relations(text)
    triples = []
    for r in relations:
        triples.append({
            "subject":  r["subject"],
            "relation": r["relation"],
            "object":   r["object"],
            "domain":   domain
        })
    return triples


# ── TEST ──────────────────────────────────────────────
if __name__ == "__main__":
    texts = [
        ("AI detects malware in network traffic.", "AI"),
        ("Ransomware encrypts sensitive data.", "Cybersecurity"),
        ("Deep learning improves intrusion detection systems.", "AI"),        # cross-domain!
        ("Machine learning identifies cybersecurity threats automatically.", "AI"),  # cross-domain!
        ("The system eradicated the ransomware attack.", "Cybersecurity"),
    ]

    for text, domain in texts:
        triples = generate_triples(text, domain)
        print(f"\n[{domain}] {text}")
        for t in triples:
            print(f"  ({t['subject']}) --{t['relation']}--> ({t['object']})")
