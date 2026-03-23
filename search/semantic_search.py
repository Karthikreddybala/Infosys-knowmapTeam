"""
search/semantic_search.py — Dense vector semantic search using sentence-transformers.
Reuses the proven SemanticSearchEngine from the original codebase.
"""
from __future__ import annotations
import torch
from sentence_transformers import SentenceTransformer, util


class SemanticSearchEngine:
    """
    Encodes knowledge graph triplets as sentence embeddings and provides
    fast cosine-similarity-based search.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        self.graph_triplets: list[dict] = []
        self.encoded_corpus = None
        self.corpus_sentences: list[str] = []

    def ingest_graph(self, triplets: list[dict]) -> None:
        """
        Convert triplets → text sentences and pre-encode them all as embeddings.
        """
        self.graph_triplets = triplets
        self.corpus_sentences = [
            f"{t['head']} {t['relation']} {t['tail']}"
            for t in triplets
        ]
        if self.corpus_sentences:
            self.encoded_corpus = self.model.encode(
                self.corpus_sentences, convert_to_tensor=True
            )

    def search(self, query: str, top_k: int = 7) -> list[tuple[dict, float]]:
        """
        Return top_k triplets most semantically similar to `query`.
        Each result is (triplet_dict, cosine_score).
        """
        if not self.corpus_sentences or self.encoded_corpus is None:
            return []

        query_emb = self.model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_emb, self.encoded_corpus)[0]
        top = torch.topk(scores, k=min(top_k, len(self.corpus_sentences)))

        return [
            (self.graph_triplets[idx], float(score.cpu()))
            for score, idx in zip(top[0], top[1])
        ]
