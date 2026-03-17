import spacy
import json
from typing import Dict, List, Tuple

# Load English tokenizer, tagger, parser and NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_svo(doc) -> set:
    """
    Traverses the dependency tree of a spaCy doc to extract Subject-Verb-Object (SVO) triplets.
    Returns a set of tuples: (subject, relation_verb, object)
    """
    triplets = set()
    
    for token in doc:
        # We are looking for verbs that act as the root of a relational logic
        if token.pos_ == "VERB":
            subjects = [child for child in token.children if child.dep_ in ("nsubj", "nsubjpass", "csubj")]
            objects = [child for child in token.children if child.dep_ in ("dobj", "pobj", "attr", "prep")]
            
            # If prep acts as a modifier (e.g "investing IN tech"), traverse to its object
            expanded_objects = []
            for obj in objects:
                if obj.dep_ == "prep":
                    expanded_objects.extend([child for child in obj.children if child.dep_ == "pobj"])
                else:
                    expanded_objects.append(obj)

            if subjects and expanded_objects:
                for subj in subjects:
                    for obj in expanded_objects:
                        # Extract the full noun chunks so we don't just get "network" instead of "neural network"
                        full_subj = get_full_noun_chunk(subj, doc)
                        full_obj = get_full_noun_chunk(obj, doc)
                        
                        # Sometimes the relation is a compound verb phrase (e.g. "is designed for")
                        relation = get_verb_phrase(token)
                        
                        triplets.add((full_subj, relation, full_obj))
                        
    return triplets

def get_full_noun_chunk(token, doc) -> str:
    """
    Given a root token of a noun, expands it to its full noun chunk (e.g. 'attacks' -> 'brute force attacks').
    """
    for chunk in doc.noun_chunks:
        if chunk.root == token:
            # We strip determiners like "The", "A" for cleaner graph nodes
            clean_tokens = [t.text for t in chunk if t.pos_ != "DET" and t.pos_ != "PRON"]
            if clean_tokens:
                return " ".join(clean_tokens)
            return chunk.text
    return token.text

def get_verb_phrase(token) -> str:
    """
    Expands a single verb into a phrase by attaching particles or negations (e.g. 'prevents' -> 'does not prevent').
    """
    phrase = [token.text]
    for child in token.children:
        if child.dep_ == "prt" or child.dep_ == "neg": # e.g. "shut down" or "not prevent"
            if child.i < token.i:
                phrase.insert(0, child.text)
            else:
                phrase.append(child.text)
    return " ".join(phrase)


def get_entities_from_ner(doc) -> List[Dict]:
    """
    Fallback dynamic entity extraction focusing on Organizations, Products, Persons etc.
    """
    entities = []
    seen = set()
    for ent in doc.ents:
        if ent.text.lower() not in seen and ent.label_ in ("ORG", "PRODUCT", "PERSON", "GPE", "LOC", "NORP", "FAC"):
            entities.append({
                "text": ent.text,
                "label": ent.label_
            })
            seen.add(ent.text.lower())
            
    # Also add standard noun chunks that weren't caught as specific NERs
    for chunk in doc.noun_chunks:
        clean_text = " ".join([t.text for t in chunk if t.pos_ != "DET" and t.pos_ != "PRON"])
        if clean_text and clean_text.lower() not in seen and len(clean_text) > 3:
            entities.append({
                "text": clean_text,
                "label": "CONCEPT"
            })
            seen.add(clean_text.lower())
            
    return entities

def advanced_process_sentence(text: str) -> Dict:
    """
    The main driver replacing `process_sentence` from weak supervision.
    Dynamically extracts Entities and Relational Triplets from raw unstructured text.
    """
    # Clean excessive whitespace
    clean_text = " ".join(text.split())
    doc = nlp(clean_text)
    
    # Extract Entities dynamically (NER + Noun Chunks)
    entities = get_entities_from_ner(doc)
    
    # Extract Relational Logic dynamically (Subject-Verb-Object parse tree)
    triplets = extract_svo(doc)
    
    relations = []
    for h, r, t in triplets:
        relations.append({
            "head": h,
            "relation": r.lower(),
            "tail": t
        })
        
    # We still return BIO labels for downstream model training compatibility, 
    # but we generate them automatically from the noun chunks instead of hardcoded keywords.
    tokens = [t.text for t in doc]
    labels = ["O"] * len(tokens)
    
    for ent in entities:
        ent_tokens = ent["text"].split()
        kw_len = len(ent_tokens)
        
        for i in range(len(tokens) - kw_len + 1):
             if tokens[i:i+kw_len] == ent_tokens:
                 if all(l == "O" for l in labels[i:i+kw_len]):
                     labels[i] = f"B-{ent['label']}"
                     for j in range(1, kw_len):
                         labels[i+j] = f"I-{ent['label']}"

    return {
        "sentence": clean_text,
        "tokens": tokens,
        "ner_labels": labels,
        "entities": entities,
        "relations": relations
    }

if __name__ == "__main__":
    sample = "The new Google transformer model actively prevents sophisticated brute force attacks dynamically."
    print("Testing Advanced SVO Pipeline:")
    res = advanced_process_sentence(sample)
    print(json.dumps(res, indent=2))
