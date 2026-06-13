---
marp: true
title: Vector Databases & Embeddings
paginate: true
---

# Vector Databases & Embeddings
### Module 05

A practical introduction for PMs, engineers, and tech leads

---

## Agenda

1. What is an embedding?
2. How similarity search works
3. Vector database options & tradeoffs
4. Indexing strategies: exact vs. approximate
5. Embeddings, RAG, and semantic search
6. Common failure modes & mitigations

---

## 1. What is an Embedding?

- A vector (list of numbers) representing the *meaning* of text
- Produced by an embedding model (e.g., 384/768/1536 dimensions)
- Similar meaning → vectors close together, even with different words

```
"The cat sat on the mat"   → [0.12, -0.03, 0.88, ...]
"A kitten rested on a rug" → [0.14, -0.02, 0.85, ...]  (close!)
"Quarterly revenue grew 12%" → [-0.61, 0.77, -0.05, ...]  (far away)
```

> This is what enables "search by meaning," not just keyword match

---

## 2. Similarity Search

- **Cosine similarity**: angle between two vectors (1.0 = identical direction)
- **k-NN**: rank all stored vectors by similarity to a query, return top K
- **ANN indexes (e.g., HNSW)**: graph-based shortcuts that skip most comparisons
  - Trade a little accuracy (recall) for a lot of speed
  - Sub-linear search time at millions of vectors

**Engineer takeaway:** brute-force is fine under ~100K vectors; ANN matters beyond that.

---

## 3. Vector Database Options

| Option | Hosting | Scalability | Metadata filter | Ops overhead |
|---|---|---|---|---|
| numpy / FAISS | In-process | 10⁵–10⁹ | Manual | None–Low |
| Chroma | Embedded/self-hosted | Small–medium | Built-in | Low–Medium |
| pgvector | Postgres extension | Small–medium | Full SQL | Low (if on Postgres) |
| Qdrant | Self-hosted/managed | Large | Strong | Medium |
| Weaviate | Self-hosted/managed | Large | Strong | Medium–Low |
| Pinecone | Fully managed | Very large | Strong | Very Low |

**Tech lead takeaway:** choice depends on scale trajectory, existing infra, and vendor lock-in tolerance.

---

## 4. Indexing: Exact vs. Approximate

| Strategy | Recall | Speed | Use when |
|---|---|---|---|
| Exact / flat | 100% | Slow at scale | ≲100K vectors, or correctness baseline |
| Approximate (HNSW, IVF) | ~95–99%+ | Sub-linear | Production, large/growing datasets |

- Recall vs. speed is a tunable knob (e.g., HNSW's `M`, `ef_search`)
- A 99% → 96% recall drop is usually invisible to end users

---

## 5. Embeddings, RAG & Semantic Search

```
Ingestion:  docs → chunk → embed → store (vector + text + metadata)
Query time: query → embed → similarity search → top-K chunks
                                  ├─ RAG: feed chunks to LLM → answer
                                  └─ Semantic search: return chunks directly
```

> If a RAG feature "gives wrong answers," check **retrieval** first —
> often not an LLM problem at all (see Module 02)

---

## 6. Common Failure Modes

| Symptom | Cause | Mitigation |
|---|---|---|
| Irrelevant results | Embedding model mismatch (index vs. query) | Use the same model/version everywhere |
| Dimension mismatch error | Index dim ≠ model output dim | Configure index dimension to match model |
| Degrading quality over time | Stale index | Scheduled/event-driven re-indexing |
| Slow queries at scale | Flat search on large dataset | Switch to ANN (HNSW/IVF) |
| Filters not respected | No native metadata filtering | Choose a store with built-in filtering |

---

## Hands-on

- `examples/01_generate_embeddings.py`
- `examples/02_similarity_search.py`
- `examples/03_vector_store_comparison.py`
- `exercises/` — practice problems + solutions

---

# Questions?

Next module: **AI Agents** →
