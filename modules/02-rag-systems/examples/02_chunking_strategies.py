"""
02 - Chunking Strategies

Compares fixed-size chunking vs. sentence-aware chunking on the same
sample document, and shows how chunk boundaries affect what gets
retrieved for a query.

No API key is required for this script — it's purely about chunking and
retrieval mechanics (TF-IDF + cosine similarity).
"""

import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SAMPLE_DOCUMENT = (
    "Our Enterprise plan includes priority support with a 1-hour response "
    "time SLA. Standard and Pro plans receive support within 24 hours. "
    "All plans include access to our knowledge base and community forum. "
    "To cancel a subscription, go to Account Settings, then Billing, then "
    "select Cancel Subscription. Cancellations take effect at the end of "
    "the current billing period, and no partial refunds are issued for "
    "unused time. If you cancel by mistake, you can reactivate your "
    "subscription within 7 days without losing your data."
)


def fixed_size_chunks(text: str, chunk_size: int = 80) -> list[str]:
    """Split into fixed-size character chunks, regardless of sentence
    boundaries. Simple and predictable, but can cut a sentence in half."""
    return [text[i : i + chunk_size].strip() for i in range(0, len(text), chunk_size)]


def sentence_aware_chunks(text: str, max_chunk_size: int = 150) -> list[str]:
    """Split into sentences, then group consecutive sentences together up
    to roughly max_chunk_size characters. Each chunk ends on a sentence
    boundary, so it's a complete thought."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > max_chunk_size:
            chunks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current.strip())

    return chunks


def best_match(query: str, chunks: list[str]) -> tuple[str, float]:
    """Return the chunk most similar to the query and its similarity score."""
    vectorizer = TfidfVectorizer()
    chunk_vectors = vectorizer.fit_transform(chunks)
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, chunk_vectors)[0]
    best_index = int(np.argmax(similarities))
    return chunks[best_index], similarities[best_index]


def main() -> None:
    query = "How do I cancel my subscription and get a refund?"

    print("=== Fixed-size chunking (80 chars) ===")
    fixed_chunks = fixed_size_chunks(SAMPLE_DOCUMENT, chunk_size=80)
    for i, chunk in enumerate(fixed_chunks):
        print(f"  [{i}] {chunk!r}")

    fixed_best, fixed_score = best_match(query, fixed_chunks)
    print(f"\nBest match for query (score={fixed_score:.3f}):")
    print(f"  {fixed_best!r}")

    print("\n\n=== Sentence-aware chunking (~150 chars) ===")
    sentence_chunks = sentence_aware_chunks(SAMPLE_DOCUMENT, max_chunk_size=150)
    for i, chunk in enumerate(sentence_chunks):
        print(f"  [{i}] {chunk!r}")

    sentence_best, sentence_score = best_match(query, sentence_chunks)
    print(f"\nBest match for query (score={sentence_score:.3f}):")
    print(f"  {sentence_best!r}")

    print("\n\n=== Takeaway ===")
    print(
        "Fixed-size chunking can split the cancellation instructions away "
        "from the no-refund/reactivation details, so the best-matching "
        "chunk may be missing half the relevant information. Sentence-aware "
        "chunking keeps each idea intact, usually producing a more complete "
        "and directly useful retrieved chunk — at the cost of variable chunk "
        "sizes."
    )


if __name__ == "__main__":
    main()
