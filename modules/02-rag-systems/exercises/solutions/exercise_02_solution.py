"""
Solution: Exercise 2 - Add a "no relevant context" guard
"""

import os

import numpy as np
from anthropic import Anthropic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODEL = "claude-sonnet-4-6"

DOCUMENTS = [
    {
        "title": "Password Reset",
        "text": (
            "To reset your password, go to the login page and click "
            "'Forgot password'. You'll receive an email with a reset link "
            "that expires after 1 hour."
        ),
    },
    {
        "title": "Two-Factor Authentication",
        "text": (
            "Enable two-factor authentication from Account Settings > "
            "Security. We support authenticator apps and SMS codes."
        ),
    },
]

IN_DOMAIN_QUERY = "How do I reset my password?"
OUT_OF_DOMAIN_QUERY = "What's the weather like today?"

# Chosen by observing that the in-domain query scores well above 0.1
# while the out-of-domain query scores near 0 (no shared vocabulary at all
# with either document).
SCORE_THRESHOLD = 0.1

NO_CONTEXT_MESSAGE = "I don't have information about that in my knowledge base."


def build_index(documents: list[dict]):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([d["text"] for d in documents])
    return vectorizer, vectors


def retrieve_best(query: str, vectorizer, vectors, documents) -> tuple[dict, float]:
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, vectors)[0]
    best_index = int(np.argmax(similarities))
    return documents[best_index], float(similarities[best_index])


def answer(client: Anthropic, query: str, context: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system="Answer using only the provided context.",
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}],
    )
    return response.content[0].text


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    vectorizer, vectors = build_index(DOCUMENTS)

    for query in (IN_DOMAIN_QUERY, OUT_OF_DOMAIN_QUERY):
        print(f"\n=== Query: {query} ===")
        best_doc, score = retrieve_best(query, vectorizer, vectors, DOCUMENTS)
        print(f"  best score: {score:.3f} ({best_doc['title']})")

        if score < SCORE_THRESHOLD:
            print(f"  -> {NO_CONTEXT_MESSAGE}")
            continue

        result = answer(client, query, best_doc["text"])
        print(f"  -> {result}")

    # Discussion:
    # - The in-domain query ("How do I reset my password?") shares
    #   vocabulary directly with the "Password Reset" document, producing a
    #   high TF-IDF similarity score well above the threshold.
    # - The out-of-domain query ("What's the weather like today?") shares
    #   essentially no vocabulary with either document, so its best score
    #   is near zero -- below the threshold, so we never call the LLM and
    #   instead return a fixed "I don't know" message.
    # - Bonus: in a real system, you'd tune SCORE_THRESHOLD against a labeled
    #   set of in-domain vs. out-of-domain queries rather than picking a
    #   single magic number -- and TF-IDF scores in particular are sensitive
    #   to corpus size, so the right threshold for a 2-document toy index
    #   will not transfer directly to a 10,000-document production index.


if __name__ == "__main__":
    main()
