import re
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """Remove noise from raw text."""
    text = str(text)
    text = re.sub(r'\s+', ' ', text)          # multiple spaces → single
    text = re.sub(r'[^\w\s.]', '', text)       # remove special chars (keep periods)
    text = re.sub(r'\n', ' ', text)            # remove newlines
    return text.strip()

def preprocess_text(text):
    """
    Clean + tokenize + lemmatize + remove stopwords.
    Returns list of cleaned sentence strings.
    """
    text = clean_text(text)
    doc = nlp(text)
    sentences = []
    for sent in doc.sents:
        tokens = [
            token.lemma_.lower()
            for token in sent
            if not token.is_stop and not token.is_punct and len(token.text) > 1
        ]
        if tokens:
            sentences.append(" ".join(tokens))
    return sentences


# ── TEST ──────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        ("Deep learning models are transforming AI security research.", "AI"),
        ("Attack type is Ransomware. Crime low this behind option tax product. Response action: Eradicated.", "Cybersecurity"),
    ]
    for text, domain in samples:
        print(f"\n[{domain}]")
        print("Original :", text)
        print("Processed:", preprocess_text(text))
