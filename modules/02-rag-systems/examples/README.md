# Module 02 — Examples

Runnable scripts demonstrating the concepts from the module README.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Scripts

| Script | Demonstrates |
|---|---|
| [`01_basic_rag_pipeline.py`](01_basic_rag_pipeline.py) | End-to-end RAG: chunk documents, retrieve with TF-IDF similarity, generate an answer with Claude using only retrieved context |
| [`02_chunking_strategies.py`](02_chunking_strategies.py) | Fixed-size vs. sentence-aware chunking on the same document, and how chunk boundaries affect what gets retrieved (no API key needed) |
| [`03_hybrid_search.py`](03_hybrid_search.py) | Combining keyword (lexical) search with embedding-style semantic search into a single hybrid ranking (no API key needed) |

Run any script directly:

```bash
python 01_basic_rag_pipeline.py
```

Scripts that don't call the Claude API (`02_chunking_strategies.py`,
`03_hybrid_search.py`) can be run without `ANTHROPIC_API_KEY` set.

## Notes on the "embeddings" used here

These examples use **TF-IDF vectors** (via `scikit-learn`) instead of a
neural embedding model, so the examples are self-contained and only require
an Anthropic API key (no separate embeddings API key or large model
downloads). The retrieval *interface* — turn text into a vector, compare
vectors with cosine similarity, return the top-k closest — is identical to
what you'd do with a real embedding model (e.g., via an embeddings API or
`sentence-transformers`); only the quality of the vectors differs.
