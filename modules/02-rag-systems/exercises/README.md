# Module 02 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

## Exercise 1: Tune chunk size and `k`

**File:** [`exercise_01_chunk_tuning.py`](exercise_01_chunk_tuning.py)

The starter code builds a small TF-IDF-based retriever (like
[`examples/01_basic_rag_pipeline.py`](../examples/01_basic_rag_pipeline.py))
over a multi-section policy document.

1. Implement `chunk_text` with a configurable `chunk_size`.
2. Run retrieval for the provided query at three different chunk sizes
   (e.g., 50, 150, 400 characters) and print the retrieved chunk(s) for each.
3. Try `k=1` vs `k=3` at your best chunk size and compare the retrieved
   context.

**Think about:** Is there a chunk size where the retrieved chunk contains
the answer *and* not much irrelevant text? What happens to retrieval when
chunks are too small (lose context) vs. too large (dilute the match with
unrelated content)?

---

## Exercise 2: Add a "no relevant context" guard

**File:** [`exercise_02_grounded_answers.py`](exercise_02_grounded_answers.py)

The starter code retrieves chunks and sends them to Claude for every query
— even when nothing in the knowledge base is actually relevant to the
question, which can lead to the model answering from general knowledge
instead of saying "I don't know."

1. Add a similarity-score threshold: if the best retrieved chunk's score is
   below the threshold, skip the LLM call entirely and return a fixed
   "I don't have information about that" message.
2. Test with a query that *is* covered by the knowledge base and one that
   is *not*, and confirm the behavior differs correctly.
3. **Bonus:** Instead of hardcoding the threshold, print the similarity
   scores for a few in-domain and out-of-domain queries and pick a
   threshold based on the gap between them.

---

## Exercise 3: Build a hybrid retriever

**File:** [`exercise_03_hybrid_retriever.py`](exercise_03_hybrid_retriever.py)

Using the hybrid search pattern from
[`examples/03_hybrid_search.py`](../examples/03_hybrid_search.py):

1. Complete `HybridRetriever.search` so it combines a keyword score and a
   semantic score into a single ranked list, using a configurable weight
   `alpha`.
2. Run the provided query (which contains both an exact product code and a
   paraphrased description) at `alpha=0.0` (pure semantic), `alpha=1.0`
   (pure keyword), and `alpha=0.5` (hybrid), and print the top result for
   each.
3. **Bonus:** Which `alpha` would you pick for a support bot where users
   often type exact error codes? Which would you pick for a bot answering
   conceptual "how does X work" questions? Does one `alpha` work for both?
