import spacy

nlp = spacy.load("en_core_web_sm")

# Relevant entity types for AI + Cybersecurity domains
RELEVANT_LABELS = {
    "ORG",          # Google, OpenAI, Microsoft
    "PERSON",       # researchers, attackers
    "GPE",          # countries, locations
    "PRODUCT",      # software, tools
    "EVENT",        # attacks, breaches
    "LAW",          # regulations, compliance
    "NORP",         # nationalities, groups
    "WORK_OF_ART",  # papers, models
}

def extract_entities(text):
    """
    Extract named entities from text.
    Returns list of dicts: [{text, label}]
    """
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in RELEVANT_LABELS:
            entities.append({
                "text":  ent.text.strip(),
                "label": ent.label_
            })
    return entities


def extract_entities_with_domain(text, domain):
    """Same as extract_entities but also tags the domain."""
    entities = extract_entities(text)
    for ent in entities:
        ent["domain"] = domain
    return entities


# ── TEST ──────────────────────────────────────────────
if __name__ == "__main__":
    texts = [
        ("Google and OpenAI are advancing AI research in the United States.", "AI"),
        ("Ransomware attack targeted Microsoft systems. The threat was eradicated.", "Cybersecurity"),
        ("Deep learning model detects malware patterns in network traffic.", "AI"),
    ]
    for text, domain in texts:
        print(f"\n[{domain}] {text}")
        print("Entities:", extract_entities_with_domain(text, domain))
