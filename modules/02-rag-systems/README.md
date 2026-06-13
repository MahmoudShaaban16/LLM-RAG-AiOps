# Module 02 — RAG Systems

> **Goal:** Understand what Retrieval-Augmented Generation (RAG) is, how the pipeline fits together end to end, what makes retrieval good or bad, and how basic RAG differs from more advanced production patterns.

## Contents

- [1. What is RAG, and why does it exist?](#1-what-is-rag-and-why-does-it-exist)
- [2. The RAG pipeline](#2-the-rag-pipeline)
- [3. Chunking strategies and tradeoffs](#3-chunking-strategies-and-tradeoffs)
- [4. Retrieval quality vs. answer quality](#4-retrieval-quality-vs-answer-quality)
- [5. Basic vs. advanced RAG](#5-basic-vs-advanced-rag)
- [6. Common failure modes](#6-common-failure-modes)
- [Hands-on](#hands-on)

---

## 1. What is RAG, and why does it exist?

**Retrieval-Augmented Generation (RAG)** is a pattern where, before asking an LLM to answer a question, you first **retrieve relevant material from your own data** and include it in the prompt as context. The model then answers using that retrieved material rather than (only) its training data.

```
User question
   → Retrieve relevant documents/chunks from your data
   → Stuff them into the prompt as context
   → Ask the LLM to answer using that context
```

Module 01 established that an LLM is not a database — it generates plausible text based on patterns learned during training, and its knowledge is frozen at training time and limited to what it learned (it doesn't know your internal docs, your latest product changes, or anything proprietary). RAG exists to close that gap **without retraining the model**.

🧑‍💼 **PM view:** RAG is usually the first step from "a chatbot" to "a chatbot that knows about *our* stuff" — internal docs, support tickets, product specs, policies. It's much cheaper and faster than fine-tuning (Module 08), and the knowledge base can be updated continuously just by re-indexing documents.

🧑‍💻 **Engineer view:** At its simplest, RAG is "search, then prompt." You need a way to find the most relevant pieces of text for a given query (retrieval), and a way to pass those pieces to the model alongside the question (augmentation + generation). Everything else — chunking, embeddings, vector stores, re-ranking — exists to make that search step better.

🧭 **Tech lead view:** RAG turns a prompting problem into a **systems problem**. You're now responsible for an ingestion pipeline, an index that can become stale, and a retrieval step whose quality directly bounds answer quality — no amount of prompt engineering fixes a retrieval step that returns the wrong documents.

---

## 2. The RAG pipeline

A RAG system has two halves: an **offline/ingestion** pipeline that prepares your data, and an **online/query-time** pipeline that answers questions.

```
INGESTION (offline, run when data changes)
  Documents → Chunking → Embedding → Indexing (vector store)

QUERY TIME (online, per user question)
  User query → Embedding → Retrieval (similarity search) → Generation (LLM call with retrieved context)
```

| Stage | What happens | Key decisions |
|---|---|---|
| **Ingestion** | Load raw documents (PDFs, wikis, tickets, code) | What counts as a "document"? How often does it change? |
| **Chunking** | Split documents into smaller pieces | Chunk size, overlap, boundary strategy (Section 3) |
| **Embedding** | Convert each chunk into a vector (a list of numbers capturing meaning) | Which embedding model? Dimensionality? Cost per chunk |
| **Indexing** | Store chunk vectors (and original text) in a vector store for fast similarity search | Vector DB choice, metadata filters, update strategy |
| **Retrieval** | Embed the user's query, find the most similar chunks in the index | How many chunks (`k`)? Similarity metric? Filters? |
| **Generation** | Send the query + retrieved chunks to the LLM, ask it to answer using only that context | Prompt structure, citation requirements, fallback if nothing relevant is found |

🧑‍💼 **PM view:** Each stage is a place where things can go wrong, and a place where cost is incurred. Embedding and indexing happen once per document (or whenever it changes); retrieval and generation happen on *every* user query. Budget and monitor accordingly.

🧑‍💻 **Engineer view:** "Embedding" just means calling an embedding model (a separate model from the LLM you use for generation) that turns text into a fixed-length vector. Similar meanings → vectors that are close together (measured via cosine similarity or dot product). [`examples/01_basic_rag_pipeline.py`](examples/01_basic_rag_pipeline.py) shows this end to end using TF-IDF vectors (no extra embedding API needed) plus the Claude Messages API for generation.

🧭 **Tech lead view:** The ingestion and query-time pipelines have very different operational characteristics — ingestion is batchy and can tolerate latency; retrieval+generation is on the user-facing critical path and needs to be fast. Design them as separate services/jobs from day one, even if they share a codebase initially.

---

## 3. Chunking strategies and tradeoffs

You can't embed an entire 50-page document as one vector and expect useful retrieval — you need to split documents into **chunks** small enough to be specific, but large enough to retain meaning.

### Fixed-size chunking
Split text every *N* characters or tokens, often with some overlap between consecutive chunks.

- ✅ Simple, fast, predictable chunk sizes (predictable token cost)
- ❌ Can split mid-sentence or mid-idea, producing chunks that are confusing out of context

### Sentence- / paragraph-aware chunking
Split on natural boundaries (sentences, paragraphs, headings), optionally grouping several sentences up to a target size.

- ✅ Chunks are more coherent — each one is a complete thought
- ❌ Chunk sizes vary, which can complicate cost estimation and embedding batch sizing

### Document-aware / structural chunking
Use the document's own structure (Markdown headings, code function boundaries, table rows) as chunk boundaries.

- ✅ Chunks align with how a human would naturally reference the content ("the Refunds section")
- ❌ Requires format-specific parsing logic; structure isn't always present or reliable

### Overlap
Adding overlap (e.g., the last 1-2 sentences of one chunk repeated at the start of the next) helps avoid losing context that straddles a chunk boundary — at the cost of redundant storage and slightly more retrieved tokens.

🧑‍💼 **PM view:** Chunking decisions are easy to defer and easy to underestimate. A chunking strategy that worked fine for a FAQ page may fail badly on a 200-page policy manual with deeply nested sections — test chunking against your *actual* documents, not toy examples.

🧑‍💻 **Engineer view:** [`examples/02_chunking_strategies.py`](examples/02_chunking_strategies.py) compares fixed-size vs. sentence-aware chunking on the same document and shows how a query that should match one clean idea can retrieve a mangled, mid-sentence chunk under naive fixed-size splitting.

🧭 **Tech lead view:** Chunk size is a tuning parameter, not a constant — it interacts with your embedding model's effective range, your `k` (number of chunks retrieved), and your LLM's context window. Re-chunking an existing index usually means re-embedding everything, so prototype chunking strategies on a representative sample *before* indexing your full corpus.

---

## 4. Retrieval quality vs. answer quality

The single most important idea in RAG: **the LLM can only answer as well as the context it's given.** If retrieval returns the wrong chunks, irrelevant chunks, or no chunks at all, no amount of prompting will produce a correct, grounded answer.

```
Bad retrieval → bad context → bad answer, even with a great model
Good retrieval → good context → even a smaller/cheaper model can answer well
```

This means most "the AI gave a wrong/weird answer" bug reports in a RAG system are actually **retrieval bugs**, not model bugs. Common root causes:

- The user's phrasing doesn't closely match the wording in the source documents (vocabulary mismatch)
- The chunk that contains the answer was split awkwardly and lost critical context
- The right chunk exists but ranks just below the `k` cutoff
- The index is stale — the document was updated but not re-ingested

🧑‍💼 **PM view:** When triaging a "bad answer," ask first: *"was the right information even retrieved?"* Log retrieved chunks alongside answers — this single piece of observability resolves most RAG quality debugging.

🧑‍💻 **Engineer view:** Build an offline "retrieval eval set" — a list of (query, expected source document) pairs — and measure whether the right document is retrieved in the top-k, independent of what the LLM does with it. This isolates retrieval quality from generation quality.

🧭 **Tech lead view:** Treat retrieval quality and generation quality as two separate metrics with two separate improvement levers. Improving the LLM (bigger model, better prompt) cannot fix a retrieval problem, and improving retrieval (better chunking, hybrid search, re-ranking) cannot fix a model that ignores its context.

---

## 5. Basic vs. advanced RAG

**Basic RAG** ("naive RAG"): embed the query, do a single similarity search against the vector index, stuff the top-k chunks into the prompt, generate. This is what [`examples/01_basic_rag_pipeline.py`](examples/01_basic_rag_pipeline.py) demonstrates, and it's a reasonable starting point for small, fairly uniform document sets.

As systems scale and queries get harder, several advanced patterns address basic RAG's weaknesses:

### Hybrid search
Combine **keyword/lexical search** (e.g., BM25 or TF-IDF, which match exact terms — great for acronyms, product names, error codes) with **embedding/semantic search** (which matches meaning even with different wording). Results from both are merged/re-ranked. See [`examples/03_hybrid_search.py`](examples/03_hybrid_search.py).

### Re-ranking
Retrieve a larger candidate set cheaply (e.g., top 20-50 via vector search), then use a more expensive, more accurate model (a cross-encoder or an LLM call) to re-score and re-order just those candidates down to the top-k that actually go into the prompt. This trades extra latency/cost for noticeably better precision.

### Query rewriting
Use an LLM call to rewrite or expand the user's query before retrieval — e.g., turning a vague follow-up question ("what about for enterprise?") into a self-contained query that includes context from the conversation, or generating multiple phrasings to search with and merging the results.

| Pattern | What it fixes | Extra cost |
|---|---|---|
| Hybrid search | Exact-term/acronym matches that pure embeddings miss | One extra (cheap) lexical search |
| Re-ranking | Vector search returning "close but not quite right" results | One extra model call over candidates |
| Query rewriting | Vague, conversational, or multi-part queries | One extra LLM call before retrieval |

🧑‍💼 **PM view:** Each advanced pattern adds latency and cost to *every query*. Don't add them speculatively — add them in response to a measured retrieval-quality problem (Section 4), and measure the improvement.

🧭 **Tech lead view:** These patterns compose: a production pipeline might rewrite the query, run hybrid search to get 30 candidates, then re-rank down to 5. Each stage is independently swappable and testable — build the basic pipeline first so you have a baseline to compare against.

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Answers are confidently wrong despite RAG | Retrieved chunks don't actually contain the answer | Log and inspect retrieved chunks; fix chunking or `k` |
| Model answers from "general knowledge" instead of the provided docs | Prompt doesn't instruct the model to rely only on context | Add explicit system instructions: "answer only using the provided context; say so if it's insufficient" |
| Retrieval misses documents that obviously match | Vocabulary mismatch between query and document wording | Add hybrid (keyword) search, or query rewriting |
| Right document retrieved, but answer ignores key details | Chunk boundary split the relevant detail away from its context | Use sentence/structure-aware chunking, add overlap |
| Index returns outdated information | Documents updated but not re-ingested/re-embedded | Set up re-indexing on document change (event-driven or scheduled) |
| Costs grow faster than expected | Sending too many/too-large chunks as context on every query | Reduce `k`, shrink chunk size, or add re-ranking to be more selective |

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — a basic RAG pipeline, chunking strategy comparison, and hybrid search
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions
