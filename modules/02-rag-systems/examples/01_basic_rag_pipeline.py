"""
01 - Basic RAG Pipeline

A minimal, end-to-end RAG example:
  1. A small hardcoded set of documents (our "knowledge base")
  2. Chunk each document
  3. Embed all chunks using TF-IDF (no extra embedding API needed)
  4. Given a user query, retrieve the top-k most similar chunks
  5. Call Claude with the retrieved chunks as context to answer the query

TF-IDF is used here purely as a lightweight, dependency-friendly stand-in
for a real embedding model. The retrieval mechanics (vectorize, compute
similarity, take top-k) are the same shape as with a "real" embedding
model — only the vectors themselves differ.
"""

import os

import numpy as np
from anthropic import Anthropic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODEL = "claude-sonnet-4-6"

# Our tiny "knowledge base" — in a real system these would be loaded from
# files, a wiki, a database, etc.
DOCUMENTS = [
    {
        "id": "doc1",
        "title": "Refund Policy",
        "text": (
            "Customers can request a refund within 30 days of purchase. "
            "Refunds are issued to the original payment method and typically "
            "take 5-7 business days to appear. Digital products that have "
            "been downloaded are not eligible for a refund."
        ),
    },
    {
        "id": "doc2",
        "title": "Shipping Information",
        "text": (
            "Standard shipping takes 3-5 business days within the country. "
            "Express shipping takes 1-2 business days and costs an additional "
            "$15. International orders may take 10-20 business days and are "
            "subject to customs fees in the destination country."
        ),
    },
    {
        "id": "doc3",
        "title": "Account Security",
        "text": (
            "We recommend enabling two-factor authentication (2FA) on your "
            "account. If you suspect unauthorized access, reset your password "
            "immediately and contact support. We never ask for your password "
            "via email or phone."
        ),
    },
    {
        "id": "doc4",
        "title": "Subscription Plans",
        "text": (
            "We offer Basic, Pro, and Enterprise subscription tiers, billed "
            "monthly or annually. Annual billing gives a 20% discount. You can "
            "upgrade or downgrade your plan at any time from account settings; "
            "changes take effect at the start of the next billing cycle."
        ),
    },
]


def chunk_text(text: str, chunk_size: int = 200) -> list[str]:
    """Naive fixed-size chunking by characters (see 02_chunking_strategies.py
    for a closer look at chunking tradeoffs)."""
    return [text[i : i + chunk_size].strip() for i in range(0, len(text), chunk_size)]


def build_index(documents: list[dict]) -> tuple[TfidfVectorizer, np.ndarray, list[dict]]:
    """Chunk every document and fit a TF-IDF vectorizer over all chunks."""
    chunks = []
    for doc in documents:
        for chunk in chunk_text(doc["text"]):
            chunks.append({"doc_id": doc["id"], "title": doc["title"], "text": chunk})

    vectorizer = TfidfVectorizer()
    chunk_vectors = vectorizer.fit_transform([c["text"] for c in chunks])
    return vectorizer, chunk_vectors, chunks


def retrieve(query: str, vectorizer, chunk_vectors, chunks, k: int = 3) -> list[dict]:
    """Embed the query with the same vectorizer and return the top-k most
    similar chunks by cosine similarity."""
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, chunk_vectors)[0]
    top_indices = np.argsort(similarities)[::-1][:k]
    return [chunks[i] for i in top_indices if similarities[i] > 0]


def generate_answer(client: Anthropic, query: str, retrieved_chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{c['title']}]\n{c['text']}" for c in retrieved_chunks
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=(
            "You are a customer support assistant. Answer the user's question "
            "using ONLY the information in the provided context. If the context "
            "doesn't contain the answer, say you don't have that information — "
            "do not make anything up."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}",
            }
        ],
    )
    return response.content[0].text


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    vectorizer, chunk_vectors, chunks = build_index(DOCUMENTS)

    queries = [
        "How long do I have to return something for a refund?",
        "What's your policy on remote work?",  # not in the knowledge base
    ]

    for query in queries:
        print(f"=== Query: {query} ===")

        retrieved = retrieve(query, vectorizer, chunk_vectors, chunks, k=2)
        print("\nRetrieved chunks:")
        for c in retrieved:
            print(f"  - [{c['title']}] {c['text'][:80]}...")

        answer = generate_answer(client, query, retrieved)
        print(f"\nAnswer:\n{answer}\n")


if __name__ == "__main__":
    main()
