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
                "score": float(1 / (1 + dist)),
            })
    return results


def _keyword_retrieve(query: str, top_k: int) -> list[dict]:
    import math
    docs = _docs
    N = len(docs)

    def tokenize(text):
        return text.lower().split()

    # Build IDF
    df: dict[str, int] = {}
    for doc in docs:
        for w in set(tokenize(doc["text"])):
            df[w] = df.get(w, 0) + 1
    idf = {w: math.log(N / freq) for w, freq in df.items()}

    # Score each doc with TF-IDF
    query_words = tokenize(query)
    scored = []
    for doc in docs:
        doc_words = tokenize(doc["text"])
        freq: dict[str, int] = {}
        for w in doc_words:
            freq[w] = freq.get(w, 0) + 1
        total = len(doc_words) or 1
        score = sum(
            (freq[w] / total) * idf.get(w, 0.0)
            for w in query_words if w in freq
        )
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"source": d["source"], "text": d["text"], "score": round(score, 4)}
        for score, d in scored[:top_k]
    ]