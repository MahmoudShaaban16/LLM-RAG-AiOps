"""
03 - Hybrid Search

Combines a keyword/lexical search (TF-IDF over raw terms, similar in
spirit to BM25 -- great for exact matches like product names, error
codes, and acronyms) with an embedding-style semantic search (TF-IDF
over the full chunk text, standing in for a neural embedding model as
in 01_basic_rag_pipeline.py).

The two ranked lists are merged into a single hybrid score, demonstrating
how hybrid search can surface a document that either method alone might
rank too low.

No API key is required -- this script is purely about retrieval/ranking.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOCUMENTS = [
    {
        "id": "doc1",
        "title": "Error Code E4042 - Payment Declined",
        "text": (
            "Error code E4042 indicates the payment processor declined the "
            "transaction. This usually happens when the card has "
            "insufficient funds or the billing address does not match."
        ),
    },
    {
        "id": "doc2",
        "title": "Troubleshooting Failed Charges",
        "text": (
            "If a customer's card is rejected, check that their billing "
            "details are up to date and that the card has not expired. "
            "Ask them to try a different payment method if the issue persists."
        ),
    },
    {
        "id": "doc3",
        "title": "Account Deletion",
        "text": (
            "Users can permanently delete their account from the Privacy "
            "settings page. Deletion removes all personal data within 30 days "
            "and cannot be undone."
        ),
    },
    {
        "id": "doc4",
        "title": "Subscription Plans Overview",
        "text": (
            "We offer Free, Pro, and Enterprise subscription tiers. Pro and "
            "Enterprise plans include priority support and higher API rate limits."
        ),
    },
]


def normalize(scores):
    """Scale scores to the 0-1 range so keyword and semantic scores are
    comparable before combining them."""
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-9:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


class HybridRetriever:
    """Combines a keyword-style TF-IDF index with a semantic-style TF-IDF
    index. In a production system, the "semantic" index would instead use
    a neural embedding model (e.g., a sentence-transformer or an embedding
    API) -- the merging logic below is identical either way.
    """

    def __init__(self, documents: list[dict]):
        self.documents = documents
        texts = [d["text"] for d in documents]

        # "Keyword" index: word-level TF-IDF, sensitive to exact terms
        # (error codes, product names) because of the (1, 1) ngram range
        # and no sublinear scaling.
        self.keyword_vectorizer = TfidfVectorizer(ngram_range=(1, 1))
        self.keyword_matrix = self.keyword_vectorizer.fit_transform(texts)

        # "Semantic" index: TF-IDF with sublinear scaling + bigrams, a rough
        # stand-in for an embedding model that captures broader meaning.
        self.semantic_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.semantic_matrix = self.semantic_vectorizer.fit_transform(texts)

    def keyword_search(self, query: str) -> list[float]:
        query_vec = self.keyword_vectorizer.transform([query])
        return cosine_similarity(query_vec, self.keyword_matrix)[0].tolist()

    def semantic_search(self, query: str) -> list[float]:
        query_vec = self.semantic_vectorizer.transform([query])
        return cosine_similarity(query_vec, self.semantic_matrix)[0].tolist()

    def hybrid_search(self, query: str, k: int = 3, alpha: float = 0.5) -> list[dict]:
        """alpha controls the keyword vs. semantic weighting:
        hybrid_score = alpha * keyword_score + (1 - alpha) * semantic_score
        """
        keyword_scores = normalize(self.keyword_search(query))
        semantic_scores = normalize(self.semantic_search(query))

        results = []
        for i, doc in enumerate(self.documents):
            hybrid_score = alpha * keyword_scores[i] + (1 - alpha) * semantic_scores[i]
            results.append(
                {
                    **doc,
                    "keyword_score": keyword_scores[i],
                    "semantic_score": semantic_scores[i],
                    "hybrid_score": hybrid_score,
                }
            )

        return sorted(results, key=lambda r: r["hybrid_score"], reverse=True)[:k]


def print_results(label: str, results: list[dict]) -> None:
    print(f"\n=== {label} ===")
    for r in results:
        print(
            f"  {r['id']} ({r['title']}) -- "
            f"keyword={r['keyword_score']:.3f} "
            f"semantic={r['semantic_score']:.3f} "
            f"hybrid={r['hybrid_score']:.3f}"
        )


def main() -> None:
    retriever = HybridRetriever(DOCUMENTS)

    # This query contains the exact error code (favors keyword search) and
    # a paraphrase of the underlying problem (favors semantic search).
    query = "Why is the customer getting E4042 when their card gets rejected?"

    results = retriever.hybrid_search(query, k=3, alpha=0.5)
    print_results(f"Hybrid search results for: {query!r}", results)

    print(
        "\nNote: doc1 matches strongly on the exact error code 'E4042' "
        "(keyword search), while doc2 matches on the paraphrased meaning "
        "'card gets rejected' (semantic search). Both signals contribute to "
        "the hybrid score, so both doc1 and doc2 rank highly -- whereas a "
        "search using only one signal could plausibly miss one of them "
        "depending on exact term overlap and corpus size."
    )


if __name__ == "__main__":
    main()
