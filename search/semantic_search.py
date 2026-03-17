import torch
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util

class SemanticSearchEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the sentence transformer model.
        """
        print(f"Loading SentenceTransformer Model: '{model_name}'...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        self.graph_triplets = []
        self.encoded_corpus = None
        self.corpus_sentences = []
        
    def ingest_graph(self, triplets: List[Dict[str, str]]):
        """
        Takes a list of triplets `{"head": H, "relation": R, "tail": T}`
        Converts them into a searchable continuous corpus of text and embeds them.
        """
        self.graph_triplets = triplets
        self.corpus_sentences = []
        
        # We represent the graph edges as sentences: "Head Relation Tail"
        for trip in triplets:
            sentence_form = f"{trip['head']} {trip['relation']} {trip['tail']}"
            self.corpus_sentences.append(sentence_form)
            
        print(f"Embedding {len(self.corpus_sentences)} Knowledge Graph relations...")
        
        # Pre-compute all embeddings for fast search
        if self.corpus_sentences:
            self.encoded_corpus = self.model.encode(self.corpus_sentences, convert_to_tensor=True)
            
    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict[str, str], float]]:
        """
        Returns the top_k most similar triplets for a given semantic search query.
        """
        if not self.corpus_sentences or self.encoded_corpus is None:
            return []
            
        # Encode the specific query
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Compute Cosine Similarity against all graph edges
        cos_scores = util.cos_sim(query_embedding, self.encoded_corpus)[0]
        
        # Get Top K results
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.corpus_sentences)))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            # Move scalar to CPU float
            score_val = score.cpu().item() 
            triplet = self.graph_triplets[idx]
            results.append((triplet, score_val))
            
        return results

if __name__ == "__main__":
    # Dummy Graph Data based on Module 5 specifications
    dummy_triplets = [
        {"head": "AI", "relation": "used_for", "tail": "Medical Imaging"},
        {"head": "AI", "relation": "used_for", "tail": "Disease Prediction"},
        {"head": "AI", "relation": "used_for", "tail": "Drug Discovery"},
        {"head": "Malware", "relation": "targets", "tail": "Windows"},
        {"head": "BERT", "relation": "used_for", "tail": "Named Entity Recognition"}
    ]
    
    engine = SemanticSearchEngine()
    engine.ingest_graph(dummy_triplets)
    
    target_query = "AI applications in healthcare"
    print(f"\nQuery: '{target_query}'")
    hits = engine.search(target_query, top_k=3)
    
    for triplet, score in hits:
        print(f"[Score: {score:.3f}] {triplet['head']} -> {triplet['relation']} -> {triplet['tail']}")
