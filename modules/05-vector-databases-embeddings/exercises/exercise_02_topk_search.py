"""
Exercise 2: Build a top-k search function

TODO:
  1. Implement top_k(query_vector, index, k) returning the indices and
     scores of the k most similar rows in `index`, sorted descending.
  2. Apply it to DOCUMENTS for each query in QUERIES.
  3. Bonus: add an optional min_score threshold.
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
    """
    TODO: return a list of (document_index, score) tuples for the `k` most
    similar rows of `index` to `query_vector`, sorted by score descending.

    - Assume `query_vector` is NOT yet normalized.
    - If `min_score` is provided, exclude results with score < min_score.
    """
    # 1. normalize query_vector
    # 2. compute similarities = index @ normalized_query_vector
    # 3. sort indices by similarity, descending
    # 4. take the top k
    # 5. apply min_score filter if provided
    raise NotImplementedError


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    index = build_index(model, DOCUMENTS)

    for query in QUERIES:
        print(f"Query: {query!r}")
        query_vector = model.encode([query])[0]

        # TODO: results = top_k(query_vector, index, k=3)
        # for rank, (doc_idx, score) in enumerate(results, start=1):
        #     print(f"  {rank}. (score={score:.3f}) {DOCUMENTS[doc_idx]}")
        print()


if __name__ == "__main__":
    main()
