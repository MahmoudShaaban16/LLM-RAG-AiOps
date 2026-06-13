"""
Solution: Exercise 3 - Choose a vector store for a scenario

There is rarely a single "correct" answer for these scenarios - the goal is
sound reasoning grounded in the tradeoffs from the module README. The
recommendations below are reasonable defaults; a different choice with a
well-reasoned justification is equally valid.
"""

SCENARIOS = {
    "A": {
        "description": (
            "A two-person startup is prototyping a document Q&A feature. "
            "They have ~2,000 internal documents, no dedicated infra team, "
            "and want to ship a demo within a week. They already have a "
            "small Postgres database for user accounts."
        ),
        "recommendation": "pgvector (or, for an even faster first pass, an in-memory numpy index)",
        "justification": (
            "At ~2,000 documents, scale is a non-issue - the deciding factor is "
            "operational overhead. Since they already run Postgres, adding the "
            "pgvector extension means zero new infrastructure to deploy, monitor, "
            "or back up - they get vector search via SQL they already know. "
            "An in-memory numpy index (examples/02_similarity_search.py) is even "
            "simpler for a one-week demo, but pgvector is a better long-term home "
            "since the data already lives in Postgres."
        ),
        "watch_for": (
            "Embedding model mismatch between index time and query time - with a "
            "small team moving fast, it's easy to change the embedding model "
            "during iteration and forget to re-embed the existing 2,000 documents, "
            "leading to a 'dimension mismatch' error or silently poor results."
        ),
    },
    "B": {
        "description": (
            "A mid-size SaaS company is adding semantic search across "
            "customer-uploaded documents. Each customer (tenant) must only "
            "ever see results from their own documents. They expect to grow "
            "to tens of millions of vectors across all tenants within a "
            "year, and have a small platform team comfortable running "
            "Docker/Kubernetes services."
        ),
        "recommendation": "Qdrant (self-hosted)",
        "justification": (
            "Strict per-tenant isolation requires strong, native metadata filtering "
            "(filter by tenant_id *during* the search, not after) - Qdrant provides "
            "this via payload filtering. Tens of millions of vectors is well within "
            "Qdrant's scaling envelope, including horizontal scaling. The team "
            "already operates Docker/Kubernetes services, so self-hosting keeps "
            "costs predictable and avoids vendor lock-in while staying within their "
            "existing operational skill set."
        ),
        "watch_for": (
            "Irrelevant results for filtered queries - if metadata filtering is "
            "applied *after* retrieval (or not enforced at the database level), a "
            "bug could leak one tenant's documents into another tenant's search "
            "results. Filtering must happen as part of the vector search itself, "
            "and should be tested explicitly per tenant."
        ),
    },
    "C": {
        "description": (
            "A large enterprise wants to launch a RAG-based assistant across "
            "billions of documents globally, with strict uptime SLAs, but "
            "has explicitly decided they do not want to operate any new "
            "infrastructure themselves and are comfortable with a SaaS "
            "vendor relationship and its ongoing cost."
        ),
        "recommendation": "Pinecone",
        "justification": (
            "Billions of vectors with strict SLAs and an explicit preference for "
            "zero self-managed infrastructure points directly at a fully managed "
            "option. Pinecone is built for very large scale with serverless scaling "
            "and built-in metadata filtering, and operational overhead is minimal - "
            "the tradeoff (ongoing cost and vendor dependency) is one this team has "
            "already decided to accept."
        ),
        "watch_for": (
            "Search quality degrading over time due to a stale index - at this "
            "scale, ingestion and re-indexing pipelines must be robust and "
            "monitored, since manually rebuilding a billions-of-vectors index is "
            "not a viable recovery path if it falls behind."
        ),
    },
}


def main() -> None:
    for name, scenario in SCENARIOS.items():
        print(f"=== Scenario {name} ===")
        print(scenario["description"])
        print()
        print(f"Recommendation: {scenario['recommendation']}")
        print(f"Justification: {scenario['justification']}")
        print(f"Watch for: {scenario['watch_for']}")
        print()


if __name__ == "__main__":
    main()
