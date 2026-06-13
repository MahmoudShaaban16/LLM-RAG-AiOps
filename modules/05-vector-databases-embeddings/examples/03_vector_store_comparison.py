"""
03 - Vector Store Comparison

This script is intentionally lightweight: it does NOT require installing
FAISS, Chroma, Pinecone, Weaviate, pgvector, or Qdrant. It's a structured,
documented reference comparing common vector store options across the
dimensions that matter most when choosing one — printed as a formatted
table.

Use this as a discussion aid (e.g., with a tech lead or architecture
review), not as a benchmark.
"""

# Each entry summarizes one option across four practical dimensions.
# These are deliberately high-level — see the module README for the
# fuller discussion and tradeoffs.
VECTOR_STORES = {
    "FAISS": {
        "hosting_model": "In-process library (Meta), embedded in your app",
        "scalability": "Millions-billions of vectors with the right index type",
        "metadata_filtering": "Limited/manual - filter in application code",
        "operational_overhead": "Low - no server, but you manage persistence and scaling yourself",
    },
    "Chroma": {
        "hosting_model": "Embedded (in-process) or self-hosted server",
        "scalability": "Good for small-medium projects (thousands-low millions)",
        "metadata_filtering": "Built-in (where filters on metadata fields)",
        "operational_overhead": "Low-medium - easy to start, simple to self-host",
    },
    "Pinecone": {
        "hosting_model": "Fully managed cloud SaaS (serverless or pod-based)",
        "scalability": "Designed for very large scale with serverless scaling",
        "metadata_filtering": "Strong, built-in",
        "operational_overhead": "Very low - no infra to run, but ongoing cost and vendor dependency",
    },
    "Weaviate": {
        "hosting_model": "Self-hosted (Docker/Kubernetes) or managed (Weaviate Cloud)",
        "scalability": "Scales horizontally; large collections",
        "metadata_filtering": "Strong, built-in",
        "operational_overhead": "Medium (self-hosted) or low (managed)",
    },
    "pgvector": {
        "hosting_model": "PostgreSQL extension (self-hosted or managed Postgres)",
        "scalability": "Good for small-medium; scales with Postgres tuning/hardware",
        "metadata_filtering": "Full SQL - joins, WHERE clauses, existing relational data",
        "operational_overhead": "Low if you already operate Postgres",
    },
    "Qdrant": {
        "hosting_model": "Self-hosted (Docker/Kubernetes) or managed (Qdrant Cloud)",
        "scalability": "Scales to large collections; supports horizontal scaling",
        "metadata_filtering": "Strong, built-in (payload filtering)",
        "operational_overhead": "Medium (self-hosted) or low (managed)",
    },
}

COLUMNS = [
    ("hosting_model", "Hosting Model"),
    ("scalability", "Scalability"),
    ("metadata_filtering", "Metadata Filtering"),
    ("operational_overhead", "Operational Overhead"),
]


def print_table() -> None:
    name_width = max(len(name) for name in VECTOR_STORES) + 2

    for key, label in COLUMNS:
        print(f"=== {label} ===")
        col_width = max(len(str(info[key])) for info in VECTOR_STORES.values())
        for name, info in VECTOR_STORES.items():
            print(f"  {name:<{name_width}} {info[key]}")
        print()


def print_decision_notes() -> None:
    print("=== Quick decision guide ===")
    print(
        "- Already running Postgres, modest scale, want one less system to operate?\n"
        "    -> pgvector\n"
        "- Prototyping or small/medium dataset, want minimal setup?\n"
        "    -> Chroma (or numpy/FAISS for a pure in-memory baseline)\n"
        "- Need rich metadata filtering AND large scale, willing to self-host?\n"
        "    -> Qdrant or Weaviate\n"
        "- Want zero infrastructure to manage and large/elastic scale,\n"
        "  comfortable with a managed SaaS dependency?\n"
        "    -> Pinecone (or Weaviate Cloud)\n"
        "- Need maximum control over indexing algorithms and are embedding\n"
        "  the index directly into a Python service?\n"
        "    -> FAISS"
    )


def main() -> None:
    print("Vector Store Comparison (conceptual, see module README for full detail)\n")
    print_table()
    print_decision_notes()


if __name__ == "__main__":
    main()
