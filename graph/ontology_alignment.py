"""
graph/ontology_alignment.py — Synonym normalisation and cross-domain detection.
"""

# Canonical synonym map: any key is mapped to its canonical concept
SYNONYM_MAP: dict[str, str] = {
    # Medical
    "doctor": "MedicalPractitioner", "physician": "MedicalPractitioner",
    "nurse": "MedicalPractitioner",
    # AI
    "deep learning": "Neural Network","machine learning": "Machine Learning",
    "ml": "Machine Learning", "dl": "Deep Learning",
    "artificial intelligence": "AI", "transformer model": "Transformer",
    "large language model": "LLM", "llm": "LLM",
    # Cybersecurity
    "ransomware attack": "Ransomware", "malware attack": "Malware",
    "intrusion detection system": "IDS", "ids": "IDS",
    "firewall system": "Firewall",
    # General
    "car": "Vehicle", "automobile": "Vehicle", "autonomous vehicle": "Autonomous Car",
    "autonomous car": "Autonomous Car",
}

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "AI": ["neural", "deep learning", "machine learning", "transformer", "bert", "gpt",
           "llm", "model", "training", "dataset", "prediction", "classification",
           "reinforcement", "supervised", "unsupervised", "embedding"],
    "Cybersecurity": ["malware", "ransomware", "phishing", "ddos", "threat", "attack",
                      "ids", "firewall", "intrusion", "vulnerability", "exploit",
                      "brute force", "zero day", "encryption", "botnet"],
    "Climate": ["climate", "carbon", "emission", "temperature", "greenhouse", "fossil",
                "renewable", "solar", "wind energy", "glacier", "deforestation"],
    "Business": ["revenue", "profit", "market", "strategy", "enterprise", "startup",
                 "investment", "shareholder", "acquisition", "merger", "gdp"],
}


def normalize_entity(text: str) -> str:
    """Map an entity text to its canonical form if a synonym exists."""
    return SYNONYM_MAP.get(text.lower().strip(), text)


def align_triplets(triplets: list[dict]) -> list[dict]:
    """Apply synonym normalisation to all heads and tails."""
    aligned = []
    for t in triplets:
        aligned.append({
            **t,
            "head": normalize_entity(t["head"]),
            "tail": normalize_entity(t["tail"]),
        })
    return aligned


def infer_domain(text: str) -> str:
    """Guess the domain of a text fragment based on keyword matching."""
    text_lower = text.lower()
    scores = {domain: 0 for domain in DOMAIN_KEYWORDS}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[domain] += 1
    best = max(scores, key=lambda d: scores[d])
    return best if scores[best] > 0 else "General"


def detect_cross_domain(triplets: list[dict]) -> list[dict]:
    """
    For each triplet, check if the head and tail belong to different domains.
    If so, set domain = 'Cross'.
    """
    result = []
    for t in triplets:
        head_domain = infer_domain(t["head"])
        tail_domain = infer_domain(t["tail"])
        domain = t.get("domain", "General")
        if head_domain != "General" and tail_domain != "General" and head_domain != tail_domain:
            domain = "Cross"
        result.append({**t, "domain": domain})
    return result
