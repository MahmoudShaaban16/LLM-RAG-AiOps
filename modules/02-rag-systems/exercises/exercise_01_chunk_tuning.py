"""
Exercise 1: Tune chunk size and k

TODO:
  1. Implement chunk_text(text, chunk_size) -- fixed-size character chunking.
  2. For QUERY, build a TF-IDF index at each chunk size in CHUNK_SIZES and
     print the retrieved chunk(s) for k=2.
  3. At your best chunk size, compare k=1 vs k=3.

No Anthropic API key is required for this exercise -- it's purely about
chunking and retrieval mechanics.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOCUMENT = (
    "Section 1: Eligibility. Employees become eligible for the wellness "
    "stipend after completing 90 days of employment. The stipend is $50 "
    "per month and can be used for gym memberships, fitness classes, or "
    "wellness apps. "
    "Section 2: Reimbursement Process. To claim the stipend, submit a "
    "receipt through the expense portal within 60 days of purchase. "
    "Reimbursements are processed within two pay cycles. "
    "Section 3: Restrictions. The stipend cannot be used for medical "
    "equipment, supplements, or food purchases. Unused stipend amounts do "
    "not roll over to the following month."
)

QUERY = "How do I get reimbursed for my gym membership?"

CHUNK_SIZES = [50, 150, 400]


def chunk_text(text: str, chunk_size: int) -> list[str]:
    # TODO: split `text` into fixed-size character chunks of length
    # `chunk_size`, stripping whitespace, and return the list of chunks.
    return []


def retrieve(query: str, chunks: list[str], k: int) -> list[tuple[str, float]]:
    """Returns the top-k (chunk, score) pairs for the query."""
    vectorizer = TfidfVectorizer()
    chunk_vectors = vectorizer.fit_transform(chunks)
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, chunk_vectors)[0]
    top_indices = np.argsort(similarities)[::-1][:k]
    return [(chunks[i], float(similarities[i])) for i in top_indices]


def main() -> None:
    for chunk_size in CHUNK_SIZES:
        print(f"\n=== chunk_size={chunk_size} ===")
        chunks = chunk_text(DOCUMENT, chunk_size)
        if not chunks:
            print("  (chunk_text not implemented yet)")
            continue

        results = retrieve(QUERY, chunks, k=2)
        for chunk, score in results:
            print(f"  score={score:.3f}: {chunk!r}")

    # TODO: at your best chunk size, compare k=1 vs k=3
    # best_chunk_size = ...
    # chunks = chunk_text(DOCUMENT, best_chunk_size)
    # for k in (1, 3):
    #     print(f"\n=== k={k} ===")
    #     for chunk, score in retrieve(QUERY, chunks, k=k):
    #         print(f"  score={score:.3f}: {chunk!r}")


if __name__ == "__main__":
    main()
