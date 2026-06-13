"""
Solution: Exercise 1 - Tune chunk size and k
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
    return [text[i : i + chunk_size].strip() for i in range(0, len(text), chunk_size)]


def retrieve(query: str, chunks: list[str], k: int) -> list[tuple[str, float]]:
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

        results = retrieve(QUERY, chunks, k=2)
        for chunk, score in results:
            print(f"  score={score:.3f}: {chunk!r}")

    # Discussion:
    # - chunk_size=50: chunks are so small they often split "gym memberships"
    #   from "Reimbursement Process", so the top result may contain only
    #   part of the relevant information (e.g., the eligibility sentence
    #   without the reimbursement steps, or vice versa).
    # - chunk_size=150: chunks roughly align with each "Section", so the
    #   retrieved chunk is more likely to contain a complete, useful answer.
    # - chunk_size=400: chunks span multiple sections, so the relevant
    #   sentence is "diluted" by unrelated restriction/eligibility text --
    #   the similarity score for the best chunk may actually be *lower*
    #   than at 150, even though more relevant text is technically present.

    print("\n=== Comparing k=1 vs k=3 at chunk_size=150 ===")
    chunks = chunk_text(DOCUMENT, 150)
    for k in (1, 3):
        print(f"\n--- k={k} ---")
        for chunk, score in retrieve(QUERY, chunks, k=k):
            print(f"  score={score:.3f}: {chunk!r}")

    # Discussion:
    # - k=1 returns only the single best-matching chunk -- if the answer
    #   spans two sections (eligibility + reimbursement process), k=1 may
    #   miss half of it.
    # - k=3 returns more context, increasing the chance the full answer is
    #   present, but also adds more (possibly irrelevant) text to the prompt,
    #   which costs tokens and can dilute the model's focus.


if __name__ == "__main__":
    main()
