# Module 05 — Vector Databases & Embeddings

> **Goal:** Understand what embeddings are, how similarity search finds relevant content, and how to choose and operate a vector store for semantic search and RAG.

## Contents

- [1. What is an embedding?](#1-what-is-an-embedding)
- [2. How similarity search works](#2-how-similarity-search-works)
- [3. Vector database options and tradeoffs](#3-vector-database-options-and-tradeoffs)
- [4. Indexing strategies: exact vs. approximate](#4-indexing-strategies-exact-vs-approximate)
- [5. Embeddings, RAG, and semantic search](#5-embeddings-rag-and-semantic-search)
- [6. Common failure modes](#6-common-failure-modes)
- [Hands-on](#hands-on)

---

## 1. What is an embedding?

An **embedding** is a list of numbers (a vector) that represents a piece of text (or an image, audio clip, etc.) in a way that captures its *meaning*. A specialized model — an **embedding model** — converts text into this vector.

```
"The cat sat on the mat"   → [0.12, -0.03, 0.88, ..., 0.41]   (e.g., 384 numbers)
"A kitten rested on a rug" → [0.14, -0.02, 0.85, ..., 0.39]   (very close to the above)
"Quarterly revenue grew 12%" → [-0.61, 0.77, -0.05, ..., 0.02] (far away from both)
```

The key property: **texts with similar meaning produce vectors that are close together** in this high-dimensional space, even if they don't share any words. This is what lets you search by *meaning* rather than by exact keyword match.

🧑‍💼 **PM view:** Embeddings are the foundation of "search that understands what the user means, not just the words they typed." This is the difference between a search box that only finds documents containing the literal word "cheap" and one that also finds documents about "affordable" or "low-cost."

🧑‍💻 **Engineer view:** In practice, you call an embedding model with a string and get back a fixed-length array of floats (the **dimensionality** — e.g., 384, 768, 1536, 3072 depending on the model). You then store that vector alongside a reference to the original text (and any metadata) so you can retrieve the text later.

🧭 **Tech lead view:** The choice of embedding model is a long-lived architectural decision. Every vector in your index must come from the *same* model (and the same model version/config) as the queries you'll run against it — see the failure modes table below. Changing embedding models means re-embedding your entire corpus.

---

## 2. How similarity search works

Once text is represented as vectors, "find documents related to this query" becomes a geometry problem: **find the vectors closest to the query's vector**.

### Cosine similarity

The most common similarity metric for text embeddings is **cosine similarity** — it measures the angle between two vectors, ignoring their magnitude:

```
cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)
```

- A value of `1.0` means the vectors point in exactly the same direction (maximally similar).
- A value of `0.0` means they're orthogonal (unrelated).
- A value of `-1.0` means they point in opposite directions (maximally dissimilar).

Other common metrics include **dot product** (similar to cosine for normalized vectors) and **Euclidean (L2) distance** (straight-line distance — smaller is more similar).

### Nearest neighbor search

Given a query vector, "similarity search" means: **rank all stored vectors by similarity to the query, and return the top K**. This is called **k-nearest neighbors (k-NN)**.

```
query: "How do I reset my password?"
       ↓ embed
query_vector: [0.22, -0.51, ...]

Compare against every document vector in the index →
rank by cosine similarity →
return top 3 most similar documents
```

### Approximate nearest neighbor (ANN) indexes

Computing exact similarity against *every* vector (a "brute-force" or "flat" search) is fine for thousands of vectors, but becomes slow at millions or billions. **ANN indexes** trade a small amount of accuracy for large speed gains by organizing vectors so that only a subset needs to be checked.

The most widely used ANN approach is **HNSW (Hierarchical Navigable Small World graphs)**. Conceptually:

- Vectors are organized into a multi-layer graph, like a network of "highways" (sparse, long-range connections at the top) and "local roads" (dense, short-range connections at the bottom).
- A search starts at the top layer, quickly narrows to the right neighborhood, then descends through layers to find precise nearest neighbors in that area — without ever comparing against most of the dataset.
- This gives **sub-linear search time** at the cost of (a) approximate, not guaranteed-exact, results, and (b) extra memory to store the graph structure.

🧑‍💼 **PM view:** "Approximate" sounds risky, but in practice HNSW-based search typically returns 95–99%+ of the same top results as exact search, at a fraction of the latency and cost. For almost all product use cases (search, RAG retrieval, recommendations), this tradeoff is the right one.

🧑‍💻 **Engineer view:** Most vector libraries/databases expose tunable parameters (e.g., HNSW's `M` and `ef_search`) that trade recall for speed/memory. Start with library defaults; tune only if you've measured a recall or latency problem.

🧭 **Tech lead view:** At small scale (tens of thousands of vectors), the index *type* barely matters — a flat/brute-force search in numpy can be fast enough and is simpler to reason about. ANN indexes start to matter once you're in the millions of vectors, or have tight latency budgets (e.g., <50ms p99).

---

## 3. Vector database options and tradeoffs

"Vector database" covers a spectrum from "an array in memory" to "a fully managed distributed service." None of these is universally "best" — the right choice depends on data scale, operational appetite, and existing infrastructure.

| Option | Hosting model | Scalability | Metadata filtering | Operational overhead |
|---|---|---|---|---|
| **numpy / plain arrays** | In-process, in-memory | Up to ~10⁵–10⁶ vectors (limited by RAM) | Manual (filter in Python) | None — just a library |
| **FAISS** | In-process library (Meta) | Millions–billions with the right index type | Limited / manual | Low — no server, but you manage persistence yourself |
| **Chroma** | Embedded or self-hosted server | Good for small–medium projects | Built-in | Low–medium — easy to start, simple to self-host |
| **Qdrant** | Self-hosted or managed (Qdrant Cloud) | Scales to large collections, horizontal scaling | Strong, built-in | Medium — run/maintain a service (or use managed) |
| **pgvector** | Extension for PostgreSQL (self-hosted or managed Postgres) | Good for small–medium; scales with Postgres tuning | Full SQL — joins, `WHERE` clauses, etc. | Low if you already run Postgres |
| **Pinecone** | Fully managed (cloud SaaS) | Designed for very large scale, serverless scaling | Strong, built-in | Very low — no infrastructure to run, but ongoing cost and vendor dependency |
| **Weaviate** | Self-hosted or managed (Weaviate Cloud) | Scales horizontally, large collections | Strong, built-in | Medium (self-hosted) or low (managed) |

🧑‍💼 **PM view:** Vector store cost is usually a *small* fraction of overall LLM infrastructure cost — but it adds a new *operational dependency* (a service that must be deployed, monitored, backed up, and upgraded), which has timeline and staffing implications even when the dollar cost is low.

🧑‍💻 **Engineer view:** For prototypes and small datasets (a few thousand to ~100K documents), an in-memory numpy/FAISS index or embedded Chroma is often *plenty* — don't reach for a managed service before you need one. See [`examples/02_similarity_search.py`](examples/02_similarity_search.py) for a from-scratch numpy approach.

🧭 **Tech lead view:** Key questions when choosing:
- **Do we already run Postgres?** If so, pgvector avoids adding a new system entirely.
- **Do we need rich metadata filtering** (e.g., "similar documents, but only from this tenant, created after this date")? Most managed/self-hosted options support this; raw numpy/FAISS do not, out of the box.
- **What's our scale trajectory?** If you'll plausibly need >10M vectors or multi-region deployment, start with something built for that (Pinecone, Weaviate, Qdrant) rather than migrating later under pressure.
- **Vendor lock-in vs. operational burden** is the core tradeoff between managed (Pinecone, Weaviate Cloud) and self-hosted (Qdrant, pgvector, Chroma) options.

---

## 4. Indexing strategies: exact vs. approximate

| Strategy | How it works | Recall | Speed | When to use |
|---|---|---|---|---|
| **Exact / "flat" / brute-force** | Compare query vector against every stored vector | 100% (ground truth) | Slow at scale — linear in dataset size | Small datasets (≲100K vectors), or as a correctness baseline |
| **Approximate (e.g., HNSW, IVF)** | Pre-built graph or clustering structure narrows the search space | ~95–99%+ typical | Sub-linear — fast even at millions of vectors | Production systems with large or growing datasets |

The **recall/speed tradeoff** is the central design knob:
- Higher recall settings (more graph connections, more candidates checked) → slower, more memory, closer to exact results.
- Lower recall settings → faster, less memory, occasional misses of the "true" top result.

🧑‍💼 **PM view:** A small drop in recall (e.g., 99% → 96%) is usually imperceptible to end users in a search or RAG context — the difference between the 1st and 3rd most-relevant document rarely changes the final answer quality. Don't over-invest engineering time chasing 100% recall.

🧭 **Tech lead view:** Re-indexing cost matters as much as query cost. Some ANN index structures are expensive to build or update incrementally — know whether your chosen store supports adding/removing vectors cheaply, or whether updates require a full rebuild (which affects how you handle frequently-changing data).

---

## 5. Embeddings, RAG, and semantic search

Embeddings are the mechanism that makes [Module 02 (RAG Systems)](../02-rag-systems/README.md) and semantic search possible:

```
Ingestion (offline):
  documents → chunk → embed each chunk → store (vector, text, metadata) in vector store

Query time:
  user query → embed query → similarity search against stored vectors
             → return top-K matching chunks → pass to LLM as context (RAG)
             → or return directly to user (semantic search)
```

- **RAG** uses the retrieved chunks as *context* for an LLM to generate a grounded answer.
- **Semantic search** can stop at retrieval — returning the matching documents/snippets directly to the user, without an LLM generation step at all.

Both depend entirely on embedding quality and index freshness: if the embeddings don't capture the right meaning, or the index doesn't reflect current data, retrieval — and therefore everything downstream — suffers.

🧑‍💼 **PM view:** When a RAG-based feature "gives wrong answers," the root cause is very often *retrieval* (embeddings/index), not the LLM. Debug retrieval first: what documents were actually retrieved for this query?

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Retrieval returns irrelevant or nonsensical results | Index was built with a **different embedding model** (or model version) than the one used for queries | Always embed queries and documents with the exact same model/version; track which model an index was built with |
| "Dimension mismatch" error when inserting/querying | Embedding model's output dimensionality doesn't match the vector store's configured dimension | Configure the index dimension to match the embedding model's output size *before* inserting data; re-create the index if the model changes |
| Search quality degrades over time | **Stale index** — underlying documents changed/were added but the index wasn't updated | Set up a re-indexing pipeline (scheduled or event-driven) so the index reflects current data |
| Good results in testing, poor results in production | Test queries/documents are too similar in style to each other; real user queries are phrased very differently | Test with realistic, varied real-world queries; consider hybrid search (keyword + vector) for exact-match terms (IDs, names) |
| Slow queries at scale | Using exact/flat search on a large dataset | Switch to an ANN index (HNSW, IVF) once the dataset grows beyond ~100K vectors |
| High memory usage / OOM | Storing high-dimensional vectors for very large corpora in memory (numpy/FAISS in-process) | Use a disk-backed or managed vector store, or reduce dimensionality (smaller embedding model) |
| Irrelevant results for filtered queries (e.g., "only my org's docs") | Vector store doesn't support metadata filtering, or filters applied *after* retrieval | Choose a store with native metadata filtering (Qdrant, Pinecone, Weaviate, pgvector) and filter *during* the search, not after |

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — generate embeddings, build a numpy-based similarity search, and compare vector store options
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions
