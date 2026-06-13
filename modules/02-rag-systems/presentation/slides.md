---
marp: true
title: RAG Systems
paginate: true
---

# RAG Systems
### Module 02

Grounding LLM answers in your own data

---

## Agenda

1. What is RAG, and why does it exist?
2. The RAG pipeline
3. Chunking strategies & tradeoffs
4. Retrieval quality vs. answer quality
5. Basic vs. advanced RAG
6. Common failure modes & mitigations

---

## 1. What is RAG?

- Retrieve relevant material from **your own data** before asking the LLM
- The model answers using retrieved context, not just training data
- Cheaper and faster than fine-tuning, and easy to keep up to date

> "Search, then prompt."

---

## 2. The RAG Pipeline

**Ingestion (offline):**
Documents → Chunking → Embedding → Indexing (vector store)

**Query time (online):**
User query → Embedding → Retrieval → Generation

- Ingestion is batchy, tolerant of latency
- Retrieval + generation is on the user-facing critical path

---

## 3. Chunking Strategies

| Strategy | Pros | Cons |
|---|---|---|
| Fixed-size | Simple, predictable cost | Can split mid-sentence/idea |
| Sentence-aware | Coherent chunks | Variable sizes |
| Document-aware | Matches human structure | Needs format-specific parsing |

- Overlap helps preserve context across chunk boundaries
- Re-chunking usually means re-embedding everything — prototype first

---

## 4. Retrieval Quality vs. Answer Quality

```
Bad retrieval  → bad context  → bad answer (even with a great model)
Good retrieval → good context → good answer (even with a smaller model)
```

- Most "bad AI answer" bugs are **retrieval bugs**
- Log retrieved chunks alongside answers
- Build a (query → expected source) eval set to measure retrieval alone

---

## 5. Basic vs. Advanced RAG

**Basic RAG:** embed query → single similarity search → top-k into prompt → generate

**Advanced patterns:**

| Pattern | Fixes |
|---|---|
| Hybrid search | Exact terms/acronyms embeddings miss |
| Re-ranking | "Close but not quite right" vector results |
| Query rewriting | Vague or conversational queries |

Add these in response to a *measured* problem, not speculatively.

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Confidently wrong despite RAG | Inspect retrieved chunks, fix chunking/`k` |
| Ignores provided context | Instruct model to answer only from context |
| Misses obvious matches | Add hybrid search / query rewriting |
| Stale answers | Re-index on document change |
| Costs growing | Reduce `k` / chunk size, add re-ranking |

---

## Hands-on

- `examples/01_basic_rag_pipeline.py`
- `examples/02_chunking_strategies.py`
- `examples/03_hybrid_search.py`
- `exercises/` — practice problems + solutions

---

# Questions?

Next module: **AI Agents** →
