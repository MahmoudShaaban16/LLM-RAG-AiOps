"""
Exercise 3: Choose a vector store for a scenario

This is a written/reasoning exercise - no embedding model required.

For each scenario below, fill in:
  - recommendation: one of "numpy/FAISS", "Chroma", "Qdrant", "pgvector",
    "Pinecone", "Weaviate"
  - justification: 2-3 sentences referencing hosting model, scalability,
    metadata filtering, and/or operational overhead
  - watch_for: one failure mode from the module README's failure-modes
    table that's especially relevant to this scenario

Check your answers against solutions/exercise_03_solution.py once done.
"""

SCENARIOS = {
    "A": {
        "description": (
            "A two-person startup is prototyping a document Q&A feature. "
            "They have ~2,000 internal documents, no dedicated infra team, "
            "and want to ship a demo within a week. They already have a "
            "small Postgres database for user accounts."
        ),
        "recommendation": None,  # TODO
        "justification": None,  # TODO
        "watch_for": None,  # TODO
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
        "recommendation": None,  # TODO
        "justification": None,  # TODO
        "watch_for": None,  # TODO
    },
    "C": {
        "description": (
            "A large enterprise wants to launch a RAG-based assistant across "
            "billions of documents globally, with strict uptime SLAs, but "
            "has explicitly decided they do not want to operate any new "
            "infrastructure themselves and are comfortable with a SaaS "
            "vendor relationship and its ongoing cost."
        ),
        "recommendation": None,  # TODO
        "justification": None,  # TODO
        "watch_for": None,  # TODO
    },
}


def main() -> None:
    for name, scenario in SCENARIOS.items():
        print(f"=== Scenario {name} ===")
        print(scenario["description"])
        print(f"Recommendation: {scenario['recommendation']}")
        print(f"Justification: {scenario['justification']}")
        print(f"Watch for: {scenario['watch_for']}")
        print()


if __name__ == "__main__":
    main()
