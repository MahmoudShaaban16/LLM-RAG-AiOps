"""
02 - Similarity Search (in-memory)

Demonstrates:
  1. Building a small in-memory vector index over a set of documents using
     numpy (no external vector database required).
  2. Embedding a query and finding the most similar documents via
     cosine similarity (k-nearest-neighbor / "flat" search).
  3. Printing ranked results with their similarity scores.

This is the same approach described in the module README as appropriate
for small datasets (roughly up to ~100K vectors) — at larger scale you'd
reach for an ANN index (HNSW, etc.) or a dedicated vector database.
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


def build_index(model: SentenceTransformer, documents: list[str]) -> np.ndarray:
    """Embed all documents and return a (num_docs, dim) matrix of vectors."""
    embeddings = model.encode(documents)
    # Normalize so dot product == cosine similarity.
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms


def search(
    model: SentenceTransformer,
    index: np.ndarray,
    documents: list[str],
    query: str,
    top_k: int = 3,
) -> list[tuple[str, float]]:
    """Embed the query and return the top_k most similar documents."""
    query_embedding = model.encode([query])[0]
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    # Cosine similarity between query and every document vector.
    similarities = index @ query_embedding

    # Rank documents by similarity, descending.
    top_indices = np.argsort(similarities)[::-1][:top_k]

    return [(documents[i], float(similarities[i])) for i in top_indices]


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    index = build_index(model, DOCUMENTS)

    queries = [
        "How do I get my money back for an order?",
        "I can't log in, what should I do?",
        "Is there a way to make my account more secure?",
    ]

    for query in queries:
        print(f"Query: {query!r}")
        results = search(model, index, DOCUMENTS, query, top_k=3)
        for rank, (doc, score) in enumerate(results, start=1):
            print(f"  {rank}. (score={score:.3f}) {doc}")
        print()


if __name__ == "__main__":
    main()
