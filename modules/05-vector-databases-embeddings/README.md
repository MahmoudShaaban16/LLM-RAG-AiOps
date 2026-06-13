# Module 05 — Vector Databases & Embeddings

> Status: 🚧 Planned — structure below shows what this module will contain.

## What you'll learn

- What embeddings are: turning text into vectors that capture meaning
- How similarity search works (cosine similarity, nearest neighbors)
- Vector database options and tradeoffs (in-memory, managed, self-hosted)
- Indexing strategies and their impact on speed vs. accuracy
- How embeddings underpin RAG (Module 02) and semantic search

🧑‍💼 **PM view:** Embedding/vector infra is usually a small line-item compared to LLM API costs — but it's a new operational dependency (another service to run, monitor, and scale).

🧭 **Tech lead view:** Choice of vector store affects more than search quality — consider operational overhead, metadata filtering support, and whether you need it to scale beyond a single machine.

## Planned contents

```
modules/05-vector-databases-embeddings/
├── README.md
├── presentation/slides.md
├── examples/
│   ├── 01_generate_embeddings.py
│   ├── 02_similarity_search.py
│   └── 03_vector_store_comparison.py
└── exercises/
```
