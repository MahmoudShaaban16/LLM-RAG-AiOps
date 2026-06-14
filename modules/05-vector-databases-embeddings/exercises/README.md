# Module 05 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

These exercises use [`sentence-transformers`](https://www.sbert.net/) (the
`all-MiniLM-L6-v2` model) and `numpy`, the same as `examples/`. No API key
is required.

> **Not coding this module?** [`pm_track.md`](pm_track.md) covers the same
> decisions (embedding model choice, exact vs. approximate search, and vector
> store tradeoffs) as a written exercise — no code required.

```bash
pip install -r ../examples/requirements.txt
```

## Exercise 1: Implement cosine similarity from scratch

**File:** [`exercise_01_cosine_similarity.py`](exercise_01_cosine_similarity.py)

The module README defines cosine similarity as:

```
cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)
```

1. Implement `cosine_similarity(a, b)` using only `numpy` — no
   `sklearn.metrics.pairwise` shortcuts.
2. Verify your implementation against the provided test vectors (including
   identical vectors, orthogonal vectors, and opposite vectors).
3. Use your function to compute the similarity between embeddings of a few
   sample sentences and confirm the results match what you'd expect
   (similar-meaning sentences score higher).

**Think about:** Why does normalizing vectors first (dividing by their norm)
let you replace cosine similarity with a plain dot product?

---

## Exercise 2: Build a top-k search function

**File:** [`exercise_02_topk_search.py`](exercise_02_topk_search.py)

Building on `examples/02_similarity_search.py`:

1. Write a function `top_k(query_vector, index, k)` that returns the
   indices and scores of the `k` most similar vectors in `index` to
   `query_vector`, sorted from most to least similar — without using any
   vector database library (numpy only).
2. Apply it to the provided set of documents and queries, and print the
   ranked results.
3. **Bonus:** Add an optional `min_score` threshold so that results below a
   similarity cutoff are excluded — and discuss what happens to a query that
   doesn't match anything well (e.g., a totally unrelated question).

**Think about:** What would change in your implementation if the index held
1 million vectors instead of 8? At what point would you reach for an ANN
index or a dedicated vector database instead?

---

## Exercise 3: Choose a vector store for a scenario

**File:** [`exercise_03_choose_vector_store.py`](exercise_03_choose_vector_store.py)

This is a written/reasoning exercise — there's no embedding model involved.

The starter file contains three scenarios (A, B, C) describing different
teams, data scales, and constraints. For each scenario:

1. Recommend a vector store option from the module README (numpy/FAISS,
   Chroma, Qdrant, pgvector, Pinecone, or Weaviate).
2. Justify your choice using at least two of: hosting model, scalability,
   metadata filtering, and operational overhead.
3. Identify one failure mode from the README's failure-modes table that this
   team should specifically watch for, given their setup.

Fill in your answers as comments or strings in the starter file, then check
them against the discussion in `solutions/`.
