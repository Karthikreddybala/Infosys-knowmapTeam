import spacy
from typing import List

# We load a small lightweight NLP sentencizer model into memory once.
# This prevents the UI loop from reloading the model entirely every time a file is uploaded.
try:
    nlp_sent = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner", "lemmatizer", "textcat"])
except:
    nlp_sent = spacy.blank("en")
    nlp_sent.add_pipe("sentencizer")
    
if "sentencizer" not in nlp_sent.pipe_names:
    nlp_sent.add_pipe("sentencizer")

def segment_document(content: str) -> List[str]:
    """
    Takes a raw unstructured document string and chunks it into valid English sentences.
    Skips unparseable boilerplate lines under 10 characters long.
    """
    doc = nlp_sent(content)
    raw_sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
    return raw_sentences
