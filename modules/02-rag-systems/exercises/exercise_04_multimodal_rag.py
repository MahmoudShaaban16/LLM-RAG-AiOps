"""
Exercise 4: Multimodal RAG - retrieving over text and image descriptions

Multimodal RAG extends the retrieval pattern from this module to a
knowledge base that contains both text passages AND images (diagrams,
screenshots, charts). A common, practical approach (no special vector DB
required): use a vision-capable model to generate a text description/
caption for each image *once*, at ingestion time, and then index those
descriptions alongside regular text chunks in the *same* TF-IDF/embedding
index from examples/01_basic_rag_pipeline.py. At query time, retrieval is
unchanged - it just may return an "image" item whose "text" field is the
caption, and your app then shows the actual image alongside the answer.

CORPUS below simulates this: some items are `type: "text"` (normal
chunks), others are `type: "image"` with a `caption` that stands in for
what a vision model would have produced from the image.

TODO:
  1. Implement `build_index(corpus)` using TfidfVectorizer over each item's
     `text` (for text items) or `caption` (for image items).
  2. Implement `search(query, corpus, vectorizer, matrix, k)` returning the
     top-k items by cosine similarity, each with a `score` added.
  3. Run the three QUERIES and print the top result type (`text` or
     `image`) and identifier for each - confirm that a query asking about
     a diagram retrieves the image item, not just text items.

No Anthropic API key is required - this is purely about indexing and
ranking mechanics. (Generating the captions themselves would use the
vision capabilities from Module 01.)
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
    # TODO: build a TfidfVectorizer over [_item_text(item) for item in corpus]
    # and return (vectorizer, matrix).
    pass


def search(query: str, corpus: list[dict], vectorizer, matrix, k: int = 1) -> list[dict]:
    # TODO:
    #   1. Transform `query` with `vectorizer`.
    #   2. Compute cosine_similarity against `matrix`.
    #   3. Return the top-k items from `corpus` (as dicts with a "score"
    #      key added), sorted by score descending.
    return []


def main() -> None:
    index = build_index(CORPUS)
    if index is None:
        print("(build_index not implemented yet)")
        return
    vectorizer, matrix = index

    for query in QUERIES:
        print(f"\nQuery: {query}")
        results = search(query, CORPUS, vectorizer, matrix, k=1)
        if not results:
            print("  (search not implemented yet)")
            continue
        top = results[0]
        print(f"  top result: [{top['type']}] {top['id']} (score={top['score']:.3f})")
        if top["type"] == "image":
            print(f"  -> would display image: {top['source']}")
        else:
            print(f"  -> text: {top['text'][:80]}...")


if __name__ == "__main__":
    main()
