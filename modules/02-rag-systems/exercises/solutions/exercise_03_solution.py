"""
Solution: Exercise 3 - Build a hybrid retriever
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

        self.keyword_vectorizer = TfidfVectorizer(ngram_range=(1, 1))
        self.keyword_matrix = self.keyword_vectorizer.fit_transform(texts)

        self.semantic_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.semantic_matrix = self.semantic_vectorizer.fit_transform(texts)

    def keyword_scores(self, query: str) -> list[float]:
        query_vector = self.keyword_vectorizer.transform([query])
        return cosine_similarity(query_vector, self.keyword_matrix)[0].tolist()

    def semantic_scores(self, query: str) -> list[float]:
        query_vector = self.semantic_vectorizer.transform([query])
        return cosine_similarity(query_vector, self.semantic_matrix)[0].tolist()

    def search(self, query: str, alpha: float, k: int = 1) -> list[dict]:
        keyword = normalize(self.keyword_scores(query))
        semantic = normalize(self.semantic_scores(query))

        results = []
        for i, doc in enumerate(self.documents):
            hybrid_score = alpha * keyword[i] + (1 - alpha) * semantic[i]
            results.append(
                {
                    **doc,
                    "keyword_score": keyword[i],
                    "semantic_score": semantic[i],
                    "hybrid_score": hybrid_score,
                }
            )

        return sorted(results, key=lambda r: r["hybrid_score"], reverse=True)[:k]


def main() -> None:
    retriever = HybridRetriever(DOCUMENTS)

    for alpha, label in ((0.0, "pure semantic"), (1.0, "pure keyword"), (0.5, "hybrid")):
        print(f"\n=== alpha={alpha} ({label}) ===")
        top = retriever.search(QUERY, alpha=alpha, k=1)[0]
        print(f"  top result: {top['id']} - {top['title']}")
        print(
            f"  keyword={top['keyword_score']:.3f} "
            f"semantic={top['semantic_score']:.3f} "
            f"hybrid={top['hybrid_score']:.3f}"
        )

    # Discussion:
    # - alpha=1.0 (pure keyword) tends to favor doc1, which contains the
    #   exact literal token "SKU-9981".
    # - alpha=0.0 (pure semantic) tends to favor doc2, which paraphrases the
    #   same concept ("unavailable for purchase" / "Out of Stock badge")
    #   without using the SKU code at all.
    # - alpha=0.5 blends both signals -- depending on the exact TF-IDF
    #   weights, doc1 may still win because it's strong on both signals
    #   (it mentions both the SKU and "out of stock").
    #
    # Bonus:
    # - A support bot where users frequently paste exact error codes, SKUs,
    #   or product names benefits from a higher alpha (more keyword weight)
    #   -- otherwise rare-but-exact tokens get "averaged away" by semantic
    #   similarity.
    # - A bot answering conceptual "how does X work" questions benefits from
    #   a lower alpha, since users describe problems in their own words that
    #   may not literally appear in the docs.
    # - In practice, a single fixed alpha rarely serves both well -- you'd
    #   either tune alpha per query type (e.g., detect if the query contains
    #   an ID-like token and boost alpha accordingly), or run both searches
    #   and merge/re-rank the combined candidate set (Section 5 of the
    #   module README).


if __name__ == "__main__":
    main()
