# Module 05 — Examples

Runnable scripts demonstrating the concepts from the module README.

Unlike Module 01, these examples do **not** require an Anthropic API key —
embeddings are generated locally using
[`sentence-transformers`](https://www.sbert.net/) with the small
`all-MiniLM-L6-v2` model (downloaded automatically on first run).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The first run of `01_generate_embeddings.py` or `02_similarity_search.py`
will download the `all-MiniLM-L6-v2` model (~80MB) from Hugging Face. This
requires an internet connection the first time only — after that the model
is cached locally.

## Scripts

| Script | Demonstrates |
|---|---|
| [`01_generate_embeddings.py`](01_generate_embeddings.py) | Generating embeddings for sample sentences, inspecting their dimensionality, and computing pairwise cosine similarity |
| [`02_similarity_search.py`](02_similarity_search.py) | Building a small in-memory (numpy) vector index and running query-based similarity search |
| [`03_vector_store_comparison.py`](03_vector_store_comparison.py) | A conceptual comparison of vector store options (FAISS, Chroma, Pinecone, Weaviate, pgvector, Qdrant) — no extra libraries required |

Run any script directly:

```bash
python 01_generate_embeddings.py
```
