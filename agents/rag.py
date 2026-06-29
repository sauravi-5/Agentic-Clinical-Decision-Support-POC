"""
Lightweight RAG engine.
On first call, encodes policy documents into a FAISS index.
Subsequent calls retrieve the top-k most relevant chunks.
"""

from __future__ import annotations
import numpy as np
from data.policies import POLICY_DOCUMENTS

_index = None
_embedder = None
_docs = POLICY_DOCUMENTS


def _build_index():
    global _index, _embedder
    try:
        from sentence_transformers import SentenceTransformer
        import faiss

        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        texts = [d["text"] for d in _docs]
        embeddings = _embedder.encode(texts, convert_to_numpy=True).astype("float32")

        dim = embeddings.shape[1]
        _index = faiss.IndexFlatL2(dim)
        _index.add(embeddings)
    except ImportError:
        # Fallback: keyword-based retrieval if deps unavailable
        _index = "keyword"


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    global _index, _embedder

    if _index is None:
        _build_index()

    if _index == "keyword":
        return _keyword_retrieve(query, top_k)

    import faiss
    query_vec = _embedder.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = _index.search(query_vec, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(_docs):
            results.append({
                "source": _docs[idx]["source"],
                "text": _docs[idx]["text"],
                "score": float(1 / (1 + dist)),  # convert L2 distance to similarity-ish score
            })
    return results


def _keyword_retrieve(query: str, top_k: int) -> list[dict]:
    """Simple TF-IDF-style keyword fallback."""
    query_words = set(query.lower().split())
    scored = []
    for doc in _docs:
        doc_words = set(doc["text"].lower().split())
        overlap = len(query_words & doc_words)
        scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"source": d["source"], "text": d["text"], "score": score / max(len(query_words), 1)}
        for score, d in scored[:top_k]
    ]
