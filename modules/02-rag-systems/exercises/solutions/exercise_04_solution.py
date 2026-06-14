"""
Solution: Exercise 4 - Multimodal RAG over text and image descriptions
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CORPUS = [
    {
        "id": "text1",
        "type": "text",
        "text": (
            "Our deployment pipeline runs unit tests, then integration "
            "tests, then deploys to staging for manual QA before a "
            "production release."
        ),
    },
    {
        "id": "image1",
        "type": "image",
        "source": "architecture_diagram.png",
        "caption": (
            "A diagram showing the deployment pipeline: a 'Build' box "
            "connects to 'Unit Tests', then 'Integration Tests', then "
            "'Staging', then 'Production', with arrows showing the flow "
            "left to right."
        ),
    },
    {
        "id": "text2",
        "type": "text",
        "text": (
            "Refunds are processed within 5-7 business days after approval. "
            "Customers receive an email confirmation once the refund is "
            "issued."
        ),
    },
    {
        "id": "image2",
        "type": "image",
        "source": "refund_status_chart.png",
        "caption": (
            "A bar chart titled 'Average Refund Processing Time by Month', "
            "showing values between 4 and 7 days across the past six "
            "months, with a downward trend."
        ),
    },
]

QUERIES = [
    "What does the deployment pipeline look like?",
    "How long do refunds take?",
    "Show me the chart of refund processing times.",
]


def _item_text(item: dict) -> str:
    return item["text"] if item["type"] == "text" else item["caption"]


def build_index(corpus: list[dict]):
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([_item_text(item) for item in corpus])
    return vectorizer, matrix


def search(query: str, corpus: list[dict], vectorizer, matrix, k: int = 1) -> list[dict]:
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, matrix)[0]

    ranked = sorted(zip(corpus, scores), key=lambda pair: pair[1], reverse=True)
    return [{**item, "score": float(score)} for item, score in ranked[:k]]


def main() -> None:
    vectorizer, matrix = build_index(CORPUS)

    for query in QUERIES:
        print(f"\nQuery: {query}")
        results = search(query, CORPUS, vectorizer, matrix, k=1)
        top = results[0]
        print(f"  top result: [{top['type']}] {top['id']} (score={top['score']:.3f})")
        if top["type"] == "image":
            print(f"  -> would display image: {top['source']}")
        else:
            print(f"  -> text: {top['text'][:80]}...")

    # Discussion:
    # - "What does the deployment pipeline look like?" and "Show me the
    #   chart of refund processing times" both retrieve the *image* items,
    #   because their captions were written to describe what's visually in
    #   the image - the text passages don't mention "diagram" or "chart" at
    #   all. "How long do refunds take?" retrieves the text passage, which
    #   states the answer directly in prose.
    # - The key idea: captioning images once at ingestion time lets a
    #   single text-based index (TF-IDF here, embeddings in production)
    #   retrieve across both modalities without any special-casing at query
    #   time. The app then renders the image alongside (or instead of) the
    #   text snippet based on `item["type"]`.


if __name__ == "__main__":
    main()
