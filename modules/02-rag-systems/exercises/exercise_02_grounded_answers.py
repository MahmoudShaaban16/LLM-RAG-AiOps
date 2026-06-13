"""
Exercise 2: Add a "no relevant context" guard

TODO:
  1. Add a similarity-score threshold (SCORE_THRESHOLD). If the best
     retrieved chunk's score is below the threshold, skip the LLM call and
     return a fixed "I don't have information about that" message.
  2. Test with IN_DOMAIN_QUERY and OUT_OF_DOMAIN_QUERY and confirm the
     behavior differs.
  3. Bonus: print similarity scores for both queries and pick a threshold
     based on the gap between them.
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

# TODO: pick a threshold based on observed scores (try printing scores first)
SCORE_THRESHOLD = 0.0

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

        # TODO: if score < SCORE_THRESHOLD, print NO_CONTEXT_MESSAGE and
        # skip the LLM call. Otherwise, call answer() with the best
        # document's text as context and print the result.


if __name__ == "__main__":
    main()
