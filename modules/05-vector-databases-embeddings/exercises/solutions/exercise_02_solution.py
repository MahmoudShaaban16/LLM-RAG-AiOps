"""
Solution: Exercise 2 - Build a top-k search function
"""

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

DOCUMENTS = [
    "To reset your password, go to Settings > Security and click 'Reset Password'.",
    "Our return policy allows returns within 30 days of purchase with a receipt.",
    "The mobile app supports both iOS 16+ and Android 12+.",
    "You can upgrade your subscription plan at any time from the billing page.",
    "If you forgot your password, use the 'Forgot password?' link on the login screen.",
    "Refunds are processed within 5-7 business days after the return is received.",
    "Two-factor authentication can be enabled under Settings > Security.",
    "Our support team is available 24/7 via live chat.",
]

QUERIES = [
    "How do I get my money back for an order?",
    "I can't log in, what should I do?",
    "What's the weather like today?",  # intentionally unrelated to any document
]


def build_index(model: SentenceTransformer, documents: list[str]) -> np.ndarray:
    """Embed all documents and L2-normalize so dot product == cosine similarity."""
    embeddings = model.encode(documents)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms


def top_k(
    query_vector: np.ndarray,
    index: np.ndarray,
    k: int = 3,
    min_score: float | None = None,
) -> list[tuple[int, float]]:
    """Return (document_index, score) for the k most similar rows of `index`."""
    normalized_query = query_vector / np.linalg.norm(query_vector)

    similarities = index @ normalized_query

    # argsort ascending, then reverse for descending order
    ranked_indices = np.argsort(similarities)[::-1]

    results = [(int(i), float(similarities[i])) for i in ranked_indices]

    if min_score is not None:
        results = [r for r in results if r[1] >= min_score]

    return results[:k]


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    index = build_index(model, DOCUMENTS)

    for query in QUERIES:
        print(f"Query: {query!r}")
        query_vector = model.encode([query])[0]

        results = top_k(query_vector, index, k=3, min_score=0.2)
        if not results:
            print("  (no results above min_score threshold)")
        for rank, (doc_idx, score) in enumerate(results, start=1):
            print(f"  {rank}. (score={score:.3f}) {DOCUMENTS[doc_idx]}")
        print()

    # Discussion:
    # - The "weather" query is unrelated to all documents, so all similarity
    #   scores will be low (often in the 0.0-0.2 range). With a min_score
    #   threshold, this query may legitimately return zero results - which
    #   is the *correct* behavior for a RAG system (better to say "I don't
    #   have information about that" than to force-feed an irrelevant chunk
    #   to the LLM as context).
    # - At 1 million vectors, `index @ normalized_query` is still just one
    #   matrix-vector multiply - numpy handles this reasonably well on
    #   modern hardware, but you'd start to feel latency, especially with
    #   many concurrent queries, and memory becomes a concern (1M x 384
    #   floats x 4 bytes ~= 1.5GB just for the embeddings).
    # - Beyond roughly 100K-1M vectors, or under tight latency/concurrency
    #   requirements, you'd switch to an ANN index (FAISS with an HNSW or
    #   IVF index, or a dedicated vector database) which avoids comparing
    #   against every vector for every query.


if __name__ == "__main__":
    main()
