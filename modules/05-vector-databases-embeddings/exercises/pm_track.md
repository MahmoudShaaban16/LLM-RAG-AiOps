# Module 05 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises —
similarity search basics, exact vs. approximate indexing, and choosing a
vector store — using a written scenario instead of Python. Useful if you
want to apply the module's concepts without running any code.

## Scenario

Your company sells project-management software. Support has accumulated
**40,000 help-center articles, release notes, and resolved ticket threads**.
The product team wants to build a "smart search" feature: a user types a
question in plain English (e.g., "why can't I export my project as a PDF?")
and gets back the most relevant articles — and eventually, an AI-generated
answer grounded in those articles (RAG).

The team is choosing:
- which embedding model to use,
- whether exact or approximate search is appropriate at this scale,
- and which vector store to build on, given the company already runs
  PostgreSQL for its main application database.

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Why embeddings, not keyword search?** A user searches "why can't I
   export my project as a PDF?" but the relevant article is titled
   "Troubleshooting: Download/print issues with project reports." Explain in
   plain language why an embedding-based search is more likely to surface
   this article than a keyword search for "export PDF," and what risk this
   introduces (hint: think about what happens with an unrelated query that
   happens to be *worded* similarly).

2. **Exact vs. approximate search.** At 40,000 articles, would you start
   with exact ("flat") similarity search or an approximate (ANN/HNSW) index?
   Justify your answer using the module's recall/speed tradeoff discussion.
   At what point (roughly) would you expect to need to revisit this choice?

3. **Vector store choice.** The company already runs PostgreSQL. Using the
   module's comparison table (numpy/FAISS, Chroma, Qdrant, pgvector,
   Pinecone, Weaviate), recommend a vector store for this feature. Justify
   your choice using at least two of: hosting model, scalability, metadata
   filtering, and operational overhead. What would change your recommendation
   if the company expected to grow to 10 million articles within a year?

4. **Debugging a quality complaint.** Three months after launch, a support
   lead reports: "smart search used to find the right article for 'refund
   policy' questions, but now it often returns irrelevant results." Using the
   module's failure-modes table, list at least two plausible root causes and,
   for each, what you'd check first to confirm or rule it out.

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. Embeddings capture *meaning*, not just words — "export as a PDF" and
   "download/print issues with project reports" share almost no words but
   describe related concepts (getting a document out of the tool in a
   printable form), so their embeddings land close together in vector space.
   A keyword search for "export PDF" would miss this article entirely. The
   risk: embeddings can also surface results that are *topically* similar but
   not actually what the user wants (e.g., a query about "exporting team
   member lists" might also score high on "export," even though it's a
   different feature) — embedding similarity is about meaning-proximity, not
   guaranteed relevance, so some irrelevant-but-related results should be
   expected and handled (e.g., by showing multiple results, not just the top
   one).

2. At 40,000 articles, **exact/flat search is perfectly viable** — this is
   well within the "tens of thousands" range the module calls out as fine for
   brute-force search in numpy, and it gives 100% recall with simple,
   predictable behavior (easier to debug "why didn't this article show up").
   The team should revisit this choice if the corpus grows toward the
   **hundreds of thousands to low millions** of chunks, or if query latency
   starts becoming noticeable — at that point an ANN index (HNSW) becomes
   worth the small recall tradeoff for the speed gain.

3. Since the company **already runs PostgreSQL**, **pgvector** is a strong
   starting recommendation: it avoids adding a new system/service entirely
   (low operational overhead — the team already knows how to operate, back
   up, and monitor Postgres), and it gives full SQL access for metadata
   filtering (e.g., "only articles tagged for the Enterprise plan," "only
   articles updated in the last year," joined with existing tables). At 40K
   articles, pgvector's scale characteristics are more than sufficient. If
   the company expected to grow to **10 million articles within a year**,
   the recommendation would shift toward a store built for that scale and
   trajectory from the start — Pinecone (managed, serverless scaling, low
   ops) or Qdrant/Weaviate (strong built-in filtering, horizontal scaling) —
   to avoid a painful mid-flight migration.

4. Two plausible root causes from the failure-modes table: (a) **the index
   went stale** — new refund-policy articles or policy updates were added/
   edited but the re-indexing pipeline didn't run, so the index still
   reflects old content (check: when was the index last rebuilt vs. when was
   the refund policy article last edited?); (b) **embedding model/version
   mismatch** — if the embedding model used for queries was updated (e.g., a
   new model version or provider) without re-embedding the existing index,
   query vectors and document vectors are no longer comparable (check: does
   the model/version used to embed the index match the model/version
   currently used to embed queries?). A third possibility worth checking:
   whether "refund policy" queries are now competing with newly added,
   superficially similar articles (e.g., a new "subscription cancellation"
   article) that are pulling rank — in which case the fix may be better
   metadata filtering or chunking, not a re-index.

</details>
