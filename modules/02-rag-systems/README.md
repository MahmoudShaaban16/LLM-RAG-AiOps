# Module 02 — RAG Systems

> Status: 🚧 Planned — structure below shows what this module will contain.

## What you'll learn

- What Retrieval-Augmented Generation (RAG) is and why it exists (grounding LLM answers in your own data)
- The RAG pipeline: ingestion → chunking → embedding → indexing → retrieval → generation
- Chunking strategies and their tradeoffs (fixed-size, semantic, document-aware)
- How retrieval quality affects answer quality ("garbage in, garbage out")
- Basic vs. advanced RAG patterns (re-ranking, hybrid search, query rewriting)

🧑‍💼 **PM view:** RAG is usually the first step from "chatbot" to "chatbot that knows about our stuff." It shifts the cost/quality conversation from the model to the *data pipeline* — most RAG quality issues are retrieval issues, not model issues.

🧭 **Tech lead view:** RAG introduces new infrastructure (vector store, embedding pipeline, document ingestion) and new failure modes (stale indexes, poor chunking, irrelevant retrieval) — plan for this as a system, not a prompt tweak.

## Planned contents

```
modules/02-rag-systems/
├── README.md
├── presentation/slides.md
├── examples/
│   ├── 01_basic_rag_pipeline.py     # Minimal end-to-end RAG with LangChain
│   ├── 02_chunking_strategies.py    # Compare chunking approaches
│   └── 03_hybrid_search.py          # Combine keyword + vector search
└── exercises/
```

See [Module 01](../01-llm-fundamentals-and-prompting/README.md) for the prerequisite concepts (tokens, context windows, prompting).
