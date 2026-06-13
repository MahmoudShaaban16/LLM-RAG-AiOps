"""
Exercise 3: Build a hybrid retriever

TODO:
  1. Complete HybridRetriever.search to combine a keyword score and a
     semantic score into a single hybrid score using `alpha`:
       hybrid_score = alpha * keyword_score + (1 - alpha) * semantic_score
  2. Run QUERY at alpha=0.0, alpha=1.0, and alpha=0.5 and print the top
     result for each.
  3. Bonus: which alpha would you pick for a support bot where users often
     type exact error codes? Which for conceptual "how does X work"
     questions?

No Anthropic API key is required -- this is purely about ranking mechanics.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOCUMENTS = [
    {
        "id": "doc1",
        "title": "Error SKU-9981 Out of Stock",
        "text": (
            "Product SKU-9981 is currently out of stock. Restocking is "
            "expected within 2 weeks. Customers can sign up for a "
            "back-in-stock notification email."
        ),
    },
    {
        "id": "doc2",
        "title": "Inventory and Availability",
        "text": (
            "When an item is unavailable for purchase, the product page "
            "displays an 'Out of Stock' badge and disables the add-to-cart "
            "button until inventory is replenished."
        ),
    },
    {
        "id": "doc3",
        "title": "Returns and Exchanges",
        "text": (
            "Items can be returned within 14 days in original packaging. "
            "Exchanges for a different size or color are processed as a "
            "return plus a new order."
        ),
    },
]

# Contains the exact SKU (favors keyword search) and a paraphrase of the
# underlying concept (favors semantic search).
QUERY = "Why does SKU-9981 show as unavailable for purchase?"


def normalize(scores: list[float]) -> list[float]:
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-9:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


class HybridRetriever:
    def __init__(self, documents: list[dict]):
        self.documents = documents
        texts = [d["text"] for d in documents]

        # Keyword-style index: single words, no sublinear scaling.
        self.keyword_vectorizer = TfidfVectorizer(ngram_range=(1, 1))
        self.keyword_matrix = self.keyword_vectorizer.fit_transform(texts)

        # Semantic-style index: unigrams + bigrams, sublinear scaling.
        self.semantic_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.semantic_matrix = self.semantic_vectorizer.fit_transform(texts)

    def keyword_scores(self, query: str) -> list[float]:
        query_vector = self.keyword_vectorizer.transform([query])
        return cosine_similarity(query_vector, self.keyword_matrix)[0].tolist()

    def semantic_scores(self, query: str) -> list[float]:
        query_vector = self.semantic_vectorizer.transform([query])
        return cosine_similarity(query_vector, self.semantic_matrix)[0].tolist()

    def search(self, query: str, alpha: float, k: int = 1) -> list[dict]:
        # TODO:
        #   1. Get keyword_scores and semantic_scores for `query`.
        #   2. Normalize both score lists with normalize().
        #   3. Combine into hybrid_score = alpha * keyword + (1 - alpha) * semantic
        #   4. Return the top-k documents (as dicts with their scores added),
        #      sorted by hybrid_score descending.
        return []


def main() -> None:
    retriever = HybridRetriever(DOCUMENTS)

    for alpha, label in ((0.0, "pure semantic"), (1.0, "pure keyword"), (0.5, "hybrid")):
        print(f"\n=== alpha={alpha} ({label}) ===")
        results = retriever.search(QUERY, alpha=alpha, k=1)
        if not results:
            print("  (search not implemented yet)")
            continue
        top = results[0]
        print(f"  top result: {top['id']} - {top['title']}")
        print(f"  hybrid_score={top.get('hybrid_score', 0):.3f}")


if __name__ == "__main__":
    main()
