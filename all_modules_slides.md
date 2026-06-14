---
marp: true
title: LLM & AI Engineering Hub
paginate: true
---

# LLM & AI Engineering Hub
### A Practical Curriculum for PMs, Engineers, and Tech Leads

Modules 01–10: from prompting fundamentals to a production capstone

---

## Curriculum Overview

| # | Module |
|---|---|
| 01 | LLM Fundamentals & Prompting |
| 02 | RAG Systems |
| 03 | AI Agents |
| 04 | Multi-Agent Systems |
| 05 | Vector Databases & Embeddings |
| 06 | LLM Evaluation & Testing |
| 07 | LLMOps & AIOps |
| 08 | Fine-Tuning |
| 09 | Security & Responsible AI |
| 10 | Production Capstone |
| 11 | Self-Hosted Inference with vLLM |
| 12 | Model Context Protocol (MCP) |
| 13 | AI Use Cases & Project Management for PMs |

---

# LLM Fundamentals & Prompting
### Module 01

A practical introduction for PMs, engineers, and tech leads

---

## Agenda

1. What is an LLM, really?
2. Tokens: the unit LLMs think in
3. Context windows
4. Choosing a model
5. Prompt engineering basics
6. Common failure modes & mitigations

---

## 1. What is an LLM?

- Trained to predict the **next token** given everything before it
- Generates text one token at a time, feeding output back as input
- Not a database — it generates plausible text, it doesn't "look things up"

> This is *why* hallucinations happen, and *why* RAG exists (Module 02)

---

## 2. Tokens

- The basic unit of input/output — roughly ¾ of a word on average
- Pricing is **per token** (input and output priced separately)
- Code, non-English text, and rare words often use more tokens per "unit of meaning"

**PM takeaway:** Estimate cost in tokens, not "messages" or "documents."

---

## 3. Context Windows

| Model | Context Window | Max Output |
|---|---|---|
| Claude Opus 4.8 | 1M tokens | 128K |
| Claude Sonnet 4.6 | 1M tokens | 64K |
| Claude Haiku 4.5 | 200K tokens | 64K |

- The model's "working memory" for one request
- Bigger window ≠ free — cost scales with what you send

---

## 4. Choosing a Model

| Model | Best for | Input $/1M | Output $/1M |
|---|---|---|---|
| Opus 4.8 | Hardest reasoning, agentic tasks | $5.00 | $25.00 |
| Sonnet 4.6 | Best balance for production | $3.00 | $15.00 |
| Haiku 4.5 | High volume, low latency | $1.00 | $5.00 |

**Strategy:** start cheap, upgrade only where quality demands it. Mix tiers.

---

## 5. Prompt Engineering Basics

- Be explicit: task, format, constraints
- Use the **system prompt** for role/tone/ground rules
- Show examples (few-shot) for consistent formatting
- Ask for **structured output** (JSON / tool calls) when parsing results
- Let the model reason step-by-step for hard problems
- Treat prompts like code: version, test, iterate

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Inconsistent format | Add schema / examples |
| Hallucinated facts | Ground with RAG |
| Cut-off responses | Raise `max_tokens` |
| Slow / expensive | Use a smaller model |
| Ignored instructions | Put key instructions in system prompt |

---

## Module 01 Hands-on

- `examples/01_first_api_call.py`
- `examples/02_token_counting.py`
- `examples/03_prompting_techniques.py`
- `examples/04_structured_output.py`
- `exercises/` — practice problems + solutions

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

## Module 02 Hands-on

- `examples/01_basic_rag_pipeline.py`
- `examples/02_chunking_strategies.py`
- `examples/03_hybrid_search.py`
- `exercises/` — practice problems + solutions

---

# AI Agents
### Module 03

Tool use, the agentic loop, and when to use one

---

## Agenda

1. From a single call to an agent
2. The agentic loop
3. Designing tools
4. Planning patterns: ReAct vs. plan-and-execute
5. Should I build an agent?
6. Common failure modes

---

## 1. From a Single Call to an Agent

- Module 01: prompt → model → response (done)
- Agent: model can call **tools**, see results, and **loop**
- Same API (`client.messages.create`) — your code runs the loop

> Nothing magic — it's a `while` loop around the Messages API

---

## 2. The Agentic Loop

```
prompt → model → tool call → your code runs the tool
   ↑                              │
   └──────── result fed back ─────┘
... repeats until stop_reason != "tool_use" ...
```

- `stop_reason == "tool_use"` → execute tool(s), append `tool_result`, loop
- `stop_reason == "end_turn"` → final answer, done

**Cost/latency:** N steps = N API calls, each re-sending growing history

---

## 3. Designing Tools

```python
{
    "name": "get_weather",
    "description": "Get current weather for a city...",
    "input_schema": { "type": "object", "properties": {...}, "required": [...] }
}
```

- Name like a function (verb + object)
- Describe **when** to use it, not just what it does
- Tight schemas: enums, required fields
- Return actionable errors, not crashes

**Tool design > prompt tweaks** for agent reliability

---

## 4. Planning Patterns

**ReAct (Reason + Act)**
- Interleave reasoning and tool calls, one step at a time
- Adaptive, but can wander

**Plan-and-execute**
- Model lists steps up front, then executes (re-planning if needed)
- Predictable, auditable, parallelizable

---

## 5. Should I Build an Agent?

| Criterion | Favors an agent when... |
|---|---|
| **Complexity** | Steps depend on intermediate results |
| **Value** | High enough to justify variable cost/latency |
| **Viability** | Reliable, well-scoped tools exist |
| **Cost of error** | Errors are cheap/reversible, or human-checked |

Start with a **bounded agent**: few tools, low `max_iterations`, narrow task

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Infinite loop | Clear termination condition + `max_iterations` |
| Wrong tool called | Sharper, mutually exclusive descriptions |
| Invalid tool arguments | Tighter schema + validation |
| One failure derails task | Structured error results |
| Cost spikes | Cap iterations, monitor `usage` |

---

## Module 03 Hands-on

- `examples/01_simple_tool_use.py` — one tool, one round trip
- `examples/02_agentic_loop.py` — manual multi-step loop, 2+ tools
- `exercises/` — practice problems + solutions

---

# Multi-Agent Systems
### Module 04

Coordinating multiple LLM calls toward one task

---

## Agenda

1. When a single agent isn't enough
2. Orchestration patterns
3. Agent-to-agent communication & shared state
4. Cost and latency implications
5. Debugging multi-agent systems
6. Common failure modes

---

## 1. When a Single Agent Isn't Enough

- Task needs different "expertise" per step (research vs. write vs. review)
- Tool/instruction set too large for one agent
- Independent subtasks could run in **parallel**
- Want separation of concerns for review / human checkpoints

> Still just `client.messages.create` — more calls, more specialized prompts

---

## 2. Orchestration Patterns

**Supervisor / Worker**
- Supervisor delegates subtasks to specialized workers, synthesizes results
- Workers can run in parallel or sequentially

**Pipeline**
- Fixed sequence: research → write → review
- Simple, inspectable, but rigid

**Peer-to-peer**
- Agents talk directly, often in a loop (e.g., drafter ↔ critic)
- Most flexible, hardest to bound

---

## 2. Orchestration Patterns (diagram)

```
                ┌──────────────┐
 task ────────► │  Supervisor  │
                └──────┬───────┘
         ┌─────────────┼─────────────┐
         ▼              ▼             ▼
    Worker A        Worker B      Worker C
         │              │             │
         └──────────────┼─────────────┘
                         ▼
                  Supervisor (synthesize) ──► final answer
```

---

## 3. Agent-to-Agent Communication

- Agents are stateless — "communication" = your code passing outputs as inputs
- "Shared state" = a dict/DB row/file your orchestrator manages
- Define explicit handoff payloads (use structured outputs / tool schemas)

```python
research = call_research_agent(topic)
draft    = call_writer_agent(research)
final    = call_reviewer_agent(draft)
```

---

## 4. Cost & Latency Implications

| Pattern | API calls | Latency shape |
|---|---|---|
| Pipeline, K stages | K | Sum of K calls |
| Supervisor + M workers (parallel) | M + 2 | ≈ max(workers) + 2 |
| Supervisor + M workers (sequential) | M + 2 | Sum of all M + 2 |

**Headline:** "one request" to a user can be 3-10+ billed API calls.

---

## 5. Debugging Multi-Agent Systems

- **Error attribution**: which stage caused the bad output?
- **Compounding non-determinism**: each stage independently varies
- **Partial failures**: what if one worker fails?

**Mitigations:**
- Log full input/output per stage
- Each agent = independently testable function
- Explicit fallback behavior for missing results

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Output ignores earlier stages | Explicit structured handoffs |
| Costs higher than expected | Pass only what's needed, not full context |
| One slow worker blocks everything | Per-call timeouts + fallback synthesis |
| Hard to trace bad output | Per-stage logging |
| Peer-to-peer loop never ends | Cap turns, require explicit "done" signal |

---

## Module 04 Hands-on

- `examples/01_supervisor_worker.py` — supervisor delegates to 2 workers
- `examples/02_pipeline_of_agents.py` — research → write → review pipeline
- `exercises/` — practice problems + solutions

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

## Module 05 Hands-on

- `examples/01_generate_embeddings.py`
- `examples/02_similarity_search.py`
- `examples/03_vector_store_comparison.py`
- `exercises/` — practice problems + solutions

---

# LLM Evaluation & Testing
### Module 06

From "it worked when I tried it" to measurable, repeatable evaluation

---

## Agenda

1. Why unit tests don't fully cover LLM behavior
2. Building an evaluation dataset
3. LLM-as-judge
4. Regression testing for prompts
5. Metrics that matter
6. Common failure modes & mitigations

---

## 1. Why Traditional Unit Tests Fall Short

- LLM output is **non-deterministic** — phrasing varies between identical calls
- Correctness is often a matter of **properties**, not exact match
- `assert response == "..."` is too brittle for open-ended text

> The fix isn't "don't test" — it's a different *kind* of test: an **eval**

---

## 2. Building an Evaluation Dataset

A list of representative inputs + expected **properties** (not exact outputs):

```python
{
    "id": "refund_policy_basic",
    "input": "Can I get a refund after 2 months on the annual plan?",
    "criteria": [
        "States whether a refund is possible",
        "Mentions the relevant time window",
        "Does not invent policy details",
    ],
}
```

**Good eval data is:** representative, small-but-meaningful, versioned & living

---

## 3. LLM-as-Judge

- A second model call scores the first model's output against criteria
- Use **structured output** (tool_choice) for `{"score": 1-5, "reasoning": "..."}`
- Give the judge a concrete rubric — not just "is this good?"
- Spot-check the judge against human judgment periodically

---

## 4. Regression Testing for Prompts

```
EVAL_DATASET ──▶ PROMPT (old) ──▶ outputs ──▶ judge ──▶ scores_old
EVAL_DATASET ──▶ PROMPT (new) ──▶ outputs ──▶ judge ──▶ scores_new

                  compare scores_old vs scores_new
```

- Same idea as a regression suite — catches known failure modes from recurring
- Always check **per-case deltas**, not just the average
- Wire into CI for any PR touching prompts/model config

---

## 5. Metrics That Matter

| Metric | Measures |
|---|---|
| Quality / accuracy | Judge scores, exact-match for classification |
| Latency | Wall-clock per request (p50/p95) |
| Cost | tokens × pricing |
| Consistency | Variance across repeated runs |

**No single number tells the whole story — track all four.**

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Great eval scores, real complaints persist | Eval doesn't cover real inputs — mine production |
| Judge scores inconsistent | Concrete rubric + structured output + temp 0 |
| Average improves, one case regresses | Check per-case deltas |
| Eval suite too slow/costly for CI | Small fast subset + larger periodic suite |

---

## Module 06 Hands-on

- `examples/01_eval_dataset.py`
- `examples/02_llm_as_judge.py`
- `examples/03_prompt_regression_test.py`
- `exercises/` — practice problems + solutions

---

# LLMOps & AIOps
### Module 07

Running LLM features reliably, observably, and cost-effectively

---

## Agenda

1. Deploying LLM applications
2. Observability: logging, tracing, cost tracking
3. Caching strategies
4. Handling model deprecations & updates
5. Monitoring for quality drift
6. Common failure modes & mitigations

---

## 1. Deploying LLM Applications

```
request -> gateway (auth/rate limit) -> your service
              -> Anthropic API (retries + fallback model)
              -> response (+ logging, cost tracking)
```

- The model API is an external dependency — treat it like one
- **Retries with backoff** for `429`/`5xx`/timeouts
- **Model fallback chain** (e.g., Sonnet -> Haiku) beats failing outright

**PM takeaway:** "the LLM API is down" should not mean "our feature is down"

---

## 2. Observability

Log on every call:

- Prompt + response (with PII-aware retention)
- `usage.input_tokens` / `usage.output_tokens`
- `cache_creation_input_tokens` / `cache_read_input_tokens`
- Model + prompt version
- Latency
- Estimated cost (tokens x pricing)

> Cost-per-user/feature should be a query, not a guess

---

## 3. Caching Strategies

**Prompt caching** (`cache_control: {"type": "ephemeral"}`)

```python
system=[{
    "type": "text",
    "text": LONG_SYSTEM_PROMPT,
    "cache_control": {"type": "ephemeral"},
}]
```

- First call: pays to write cache (`cache_creation_input_tokens`)
- Later calls: discounted `cache_read_input_tokens`
- Put stable content first, variable content after

**Response caching:** hash repeat requests, skip the API call entirely

---

## 4. Model Deprecations & Updates

```
Old: hardcode "claude-sonnet-4-6" everywhere
     -> deprecation notice -> frantic find-and-replace

Better: MODEL = config["model_id"]  (one place)
        -> deprecation notice -> update config, run eval suite, roll out
```

- New model versions can change behavior even at the same tier
- Re-run the Module 06 eval suite before switching production traffic

---

## 5. Monitoring for Quality Drift

Drift happens even with **no code changes**:

- Provider updates the underlying model
- Real-world input distribution shifts
- Upstream data (retrieved docs, tool outputs) changes

**Mitigation:**
- Run the eval suite on a schedule (not just on PRs)
- Sample production traffic for LLM-as-judge scoring
- Track score trend + leading indicators (length, refusals, latency)

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Outage = feature down | Retries + fallback model chain |
| Cost spikes | Per-request/user cost logging + alerts |
| "It used to work" | Scheduled eval runs + drift monitoring |
| Caching not saving cost | Keep cached prefix identical between calls |
| Breaks after deprecation | Centralize model ID in config |
| Retry storms | Backoff + jitter + max attempts, only on retryable errors |

---

## Module 07 Hands-on

- `examples/01_prompt_caching.py`
- `examples/02_request_logging_and_cost_tracking.py`
- `examples/03_fallback_and_retry.py`
- `exercises/` — practice problems + solutions

---

# Fine-Tuning
### Module 08

A decision framework for PMs, engineers, and tech leads

---

## Agenda

1. Fine-tuning vs. prompting vs. RAG
2. What fine-tuning can and can't fix
3. Data preparation
4. Evaluating fine-tuned vs. base
5. Cost & maintenance
6. Common failure modes

---

## 1. Fine-tuning vs. Prompting vs. RAG

| Tool | Changes | Iteration speed |
|---|---|---|
| Prompting | Instructions per request | Minutes |
| RAG | What info the model can see | Hours |
| Tool use | What actions/schema the model uses | Minutes–hours |
| Fine-tuning | The model's weights | Days–weeks |

> Fine-tuning is the **heaviest, slowest** tool — and usually the **last** one to reach for.

---

## When Fine-Tuning Might Apply

- You've already tried prompting + RAG + tools
- A specific, *measured* gap remains (format/style/classification at scale)
- The behavior is demonstrable via examples but too costly to prompt every call

**Anthropic's fine-tuning offerings are limited/enterprise-focused** — for most teams, prompting + RAG covers the need.

---

## 2. What Fine-Tuning CAN Fix

- Style/tone/persona consistency
- Output format consistency at scale
- Narrow domain classification/extraction
- Shorter prompts via "baked-in" behavior

---

## What Fine-Tuning CAN'T Fix

- ❌ New knowledge / facts → use **RAG**
- ❌ Frequently changing information
- ❌ A model that fundamentally lacks the capability

> Mental model: fine-tuning changes **how** it responds, not **what it knows**

---

## 3. Data Preparation

- Format: **JSONL**, one example per line
- Each example: consistent schema (e.g., `messages` or `input`/`output`)
- Needs: consistency, coverage, volume (hundreds–thousands), quality > quantity
- No PII unless your data agreement covers training retention

**Validate before training:** valid JSON, required fields, consistent schema
→ `examples/01_prepare_training_data.py`

---

## 4. Evaluating Fine-Tuned vs. Base

Same discipline as Module 06:

1. Same eval set for both models
2. Run base (best prompt) vs. fine-tuned
3. Compare quality, format compliance, latency, cost
4. Check for **regressions outside the target task**

> "It feels better" is not a launch criterion.

---

## 5. Cost & Maintenance

A fine-tuned model is an artifact you **own**:

- Training cost
- Inference cost (often different pricing)
- Versioning + re-evaluation on every update
- Retraining when the base model is deprecated
- Ongoing data pipeline maintenance

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Stale "knowledge" baked in | Use RAG for facts |
| Good on target task, worse elsewhere | Broaden training data, eval outside target task |
| Inconsistent training data → inconsistent model | Validate schema before training |
| No before/after comparison | Use Module 06 eval harness |
| Jumping straight to fine-tuning | Apply the decision framework first |

---

## Module 08 Hands-on

- `examples/01_prepare_training_data.py`
- `examples/02_evaluate_finetuned_vs_base.py`
- `exercises/` — decision framework + dataset prep practice

---

# Security & Responsible AI
### Module 09

A practical introduction for PMs, engineers, and tech leads

---

## Agenda

1. Prompt injection
2. Data privacy
3. Guardrails
4. Responsible AI considerations
5. Governance
6. Common failure modes

---

## 1. Prompt Injection

- Untrusted content (documents, tool results, web pages) can contain text the model treats as **instructions**
- Everything in the context window is just text — the model has no built-in "this part is data" signal
- **RAG and agents are especially exposed**: retrieved docs and tool results are attacker-reachable surfaces

> The "SQL injection" of LLM apps

---

## Prompt Injection — Mitigations

| Mitigation | What it does |
|---|---|
| Delimit untrusted content | XML tags + "treat as data, not instructions" |
| Privilege separation | Don't grant tools the task doesn't need |
| Treat tool results as untrusted | Same delimiting for fetched/tool content |
| Least-privilege tool design | Narrow, structured tools — not `run_sql` |
| Human-in-the-loop | Approval gate for risky actions |

**No prompting trick fully solves this** — the real boundary is *what the model is allowed to do*.

---

## 2. Data Privacy

- Every API call sends the **full context** — system prompt, history, retrieved docs, tool I/O — to the provider
- Check your provider's **retention policy** (training use, abuse monitoring, zero-data-retention agreements)
- **PII handling**: redact before it enters the prompt; re-insert real values client-side if needed
- Logging is part of your data footprint too

**PM takeaway:** "Can we send this data to the model?" is a legal/compliance question — answer it before designing the feature.

---

## 3. Guardrails

- **Input filtering** — sanitize before the model sees it
- **Output filtering** — check before the user/system sees it
- **Tool-access allow-lists** — validate every `tool_use` call before executing
- **Human-in-the-loop** — required approval for destructive/high-impact actions (delete, send, refund)

> The model's response is a **proposal**. Your code decides what actually runs.

---

## 4. Responsible AI

- **Bias** — evaluate outputs across groups/inputs for consequential decisions
- **Transparency** — disclose AI involvement in decisions that affect people
- **Appropriate use** — define out-of-scope topics explicitly; LLM supports, doesn't replace, authoritative sources for deterministic tasks

**Tech lead takeaway:** Out-of-scope behavior is testable — add it to your Module 06 eval set.

---

## 5. Governance

- **Prompt/model approval** — system prompts are config that affects security & behavior; review like code
- **Model version pinning** — upgrades are changes requiring re-evaluation
- **Audit trails** — what did the model see, output, do, and who approved it
- **Incident response** — detect, roll back, assess impact

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Model reveals system prompt | Delimit untrusted content + explicit instructions |
| Agent takes a destructive action | Tool allow-list + human approval gate |
| PII in logs / sent to provider | Redaction pipeline + logging review |
| Confident out-of-scope answers | Explicit scope boundaries + eval coverage |
| Can't reconstruct an incident | Structured audit trail from day one |
| Prompt change ships without review | Treat prompts as reviewed artifacts |

---

## Module 09 Hands-on

- `examples/01_prompt_injection_demo.py`
- `examples/02_tool_access_guardrails.py`
- `exercises/` — guardrail design + injection-risk review

---

# Production Capstone
### Module 10

Putting it all together: a support ticket triage assistant

---

## What we're building

A support ticket triage assistant that:

1. Retrieves relevant help-center articles (RAG)
2. Decides whether to call a tool (e.g., check order status)
3. Returns a structured triage result (category, urgency, response, needs human review)
4. Treats retrieved/tool content as untrusted (guardrails)
5. Logs cost & latency for every call (observability)

---

## Architecture

```
ticket --> [guardrail: wrap untrusted text]
       --> [retrieval: TF-IDF over help articles]
       --> [Claude + tools: triage agent]
       --> [guardrail: validate tool calls]
       --> [log: cost & latency]
```

---

## Module mapping

| Module | Role in the capstone |
|---|---|
| 01 | System prompt, structured output, model choice |
| 02 | RAG retrieval over help articles |
| 03 | Tool use (check_order_status) |
| 05 | In-memory similarity search |
| 06 | Exercise: build an eval set |
| 07 | Cost/latency logging |
| 09 | Untrusted-input wrapping |

---

## What's deliberately left out

- No fine-tuning (Module 08) — prompting + RAG is sufficient
- No multi-agent orchestration (Module 04) — a single agent with tools is enough

**Tech lead takeaway:** good architecture reviews ask "what can we leave out," not just "what do we need."

---

## Module 10 Hands-on

- `examples/capstone_app/main.py` — single-file, ~250 lines, full pipeline
- `exercises/` — add a tool, build an eval set, add a guardrail

---

# Self-Hosted Inference with vLLM
### Module 11

When (and how) teams run open-weight models on their own GPUs

---

## Agenda

1. What is vLLM?
2. Why self-host at all? API vs. self-hosted
3. How vLLM makes self-hosting practical
4. Deploying vLLM: the OpenAI-compatible server
5. A decision framework: API, self-hosted, or both?
6. Common failure modes

---

## 1. What is vLLM?

- An open-source **inference/serving engine** for open-weight LLMs (Llama, Mistral, Qwen, ...)
- Not a model — the runtime that serves a model efficiently and exposes an API

```
Model weights  ≈  the application code
vLLM           ≈  the web server / runtime that runs it efficiently
```

> Quality ceiling = whatever open-weight model you choose, generally below frontier hosted models

---

## 2. API vs. Self-Hosted

| | Managed API | Self-hosted (vLLM) |
|---|---|---|
| Infra | Provider runs it | You run it |
| Cost shape | Variable, $/token | Fixed, GPU-hours |
| Quality ceiling | Frontier models | Best open-weight model |
| Data residency | Sent to provider | Stays in your infra |
| Ops burden | None | Capacity, upgrades, failures, scaling |
| Time to first request | Minutes | Hours-days |

**PM takeaway:** not "cheaper" in the abstract — depends on volume, compliance, and ops capacity.

---

## 3. How vLLM Makes Self-Hosting Practical

**PagedAttention**
- Manages the KV cache like OS virtual memory — fixed-size pages, allocated on demand
- Drastically reduces memory waste → more concurrent requests per GPU

**Continuous batching**
- Adds/removes requests from the running batch on the fly
- Keeps the GPU busy under real, bursty traffic

**Also:** quantization (AWQ/GPTQ/FP8), tensor parallelism, LoRA adapter serving (Module 08)

---

## 4. Deploying vLLM

```bash
pip install vllm
vllm serve mistralai/Mistral-7B-Instruct-v0.2
```

OpenAI-compatible API on `localhost:8000`:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
response = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    messages=[{"role": "user", "content": "Summarize this in one sentence: ..."}],
)
```

**Same shape as Ollama, LM Studio, TGI** — pattern generalizes

---

## 5. Decision Framework: API, Self-Hosted, or Both?

| Question | "Yes" favors self-hosting |
|---|---|
| High & steady volume? | Fixed GPU cost amortizes better |
| Data residency requires it? | May be a hard requirement |
| Open-weight model good enough (per Module 06 evals)? | Quality tradeoff acceptable |
| Have ML infra expertise? | Someone owns GPUs + incidents |
| Latency-insensitive / has fallback? | Easier to absorb learning curve |

**Hybrid is common:** self-host for high-volume narrow tasks, API for frontier reasoning/tool use.

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| OOM under load | Tune GPU memory/batch settings, consider quantization |
| Self-hosted costs more than API | Right-size GPUs to sustained load, or fall back to API for overflow |
| Quality regression after switching | Re-run Module 06 eval suite before shipping |
| Tool use/structured output breaks | Verify support for your model + server version |
| No cost/failure visibility | Apply Module 07 observability to your own server |
| GPU node failure = outage | Fallback chain to a managed API |

---

## Module 11 Hands-on

- `examples/02_openai_compatible_client.py` — query an OpenAI-compatible endpoint
- `examples/03_cost_comparison.py` — self-hosted GPU vs. API cost crossover
- `exercises/` — decision framework + cost-modeling practice

---

# Model Context Protocol (MCP)
### Module 12

A standard protocol for tools, resources, and prompts

---

## Agenda

1. What is MCP, and why does it exist?
2. MCP architecture: hosts, clients, servers
3. MCP tools vs. inline tool definitions (Module 03)
4. Building an MCP server
5. Connecting Claude to an MCP server
6. Security considerations
7. Common failure modes

---

## 1. What is MCP, and Why Does it Exist?

Module 03: tools defined **inline** — JSON schema + Python function, in your app

Gets awkward when:
- Same tools need to be used by **multiple** apps/agents
- You want tools built by **someone else** without copying their code
- Tools need to be added/updated **independently** of the app

**MCP** = standardized way for a "host" to discover and call tools/resources/prompts exposed by a separate **MCP server**

---

## MCP in One Picture

```
Without MCP:  your agent code  --(hardcoded tool functions)-->  each integration

With MCP:     your agent code  --(MCP protocol)-->  MCP server  --> the actual integration
                    (host/client)                    (anyone can build/run this)
```

> Like USB-C for device connectors, or LSP for editor/language integrations

🧑‍💼 **PM view:** MCP matters when tools need to be **shared, reused, or operated independently**. For a single agent with a handful of owned tools, inline tools (Module 03) remain simpler.

---

## 2. MCP Architecture

| Role | What it is | Example |
|---|---|---|
| **Host** | The application the user interacts with | Your agent app, Claude Desktop/Code |
| **Client** | The part of the host that speaks MCP | `ClientSession` (embedded in host) |
| **Server** | A process exposing tools/resources/prompts | "GitHub" MCP server, "company DB" server |

A host can connect to **multiple** servers, aggregating all their tools.

**Transports:**
- **stdio** — client launches server as a subprocess (local, simple)
- **HTTP/SSE** — server runs as a network service (shared/hosted)

---

## 3. MCP Tools vs. Inline Tools

Both produce the same thing the Anthropic API needs:
`{"name", "description", "input_schema"}` + a way to execute a named tool

| | Inline tools (Module 03) | MCP server tools |
|---|---|---|
| Where defined | Your application code | Separate MCP server process |
| Who can reuse | Only this codebase | Any MCP-compatible host |
| Update cycle | Redeploy your app | Update/restart server independently |
| New tool | Edit your code | Add to server — clients see it automatically |
| Operational surface | One service | Two services (host + server) |

🧭 **Tech lead view:** Not "MCP vs. tool use" — MCP **is** tool use, behind a protocol boundary.

---

## 4. Building an MCP Server

`FastMCP` makes a minimal server straightforward:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

@mcp.tool()
def get_order_status(order_id: str) -> str:
    """Look up the current status of a customer order by order ID."""
    mock_orders = {"ORD-1234": "shipped", "ORD-5678": "processing"}
    return mock_orders.get(order_id, "not_found")

if __name__ == "__main__":
    mcp.run()
```

`@mcp.tool()` derives the schema from the signature/type hints, description from the docstring

---

## 5. Connecting Claude to an MCP Server

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(command="python", args=["01_simple_mcp_server.py"])

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # 1. Discover tools from the MCP server
        mcp_tools = await session.list_tools()
        anthropic_tools = [
            {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
            for t in mcp_tools.tools
        ]

        # 2. Same agentic loop as Module 03, but tool execution
        #    goes via session.call_tool(block.name, block.input)
```

🧭 Everything from Module 03 (`stop_reason`, `tool_result`, `MAX_ITERATIONS`) is unchanged

---

## 6. Security Considerations

MCP servers are **tool providers your agent grants capabilities to** — Module 09's trust questions apply, plus:

- **Tool-access allow-lists** apply to MCP tools too — validate `tool_use.name` before calling `session.call_tool`
- **Tool descriptions are untrusted input** if the server isn't yours — a malicious server could write descriptions designed to manipulate the model
- **Resource/data exposure** — prefer servers configured with the **minimum** tool set the task needs

🧭 "We added an MCP server" = adding a third-party dependency that can act on your behalf

---

## 7. Common Failure Modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Client can't connect | Wrong command/args, server crashed | Run server standalone first |
| Tool call fails silently | Name/schema mismatch, server exception | Log results/errors explicitly |
| New tool not available | Tool list fetched once at startup | Re-fetch `list_tools()` per session |
| Agent calls a tool it shouldn't | No allow-list on MCP tools | Apply Module 09's guardrail |
| Broke in prod | stdio → HTTP/SSE without network handling | Apply Module 07's retry/fallback thinking |

---

## Module 12 Hands-on

- `examples/01_simple_mcp_server.py` — minimal MCP server with two tools
- `examples/02_mcp_client_with_claude.py` — Claude client connecting via stdio
- `exercises/` — practice problems + solutions

---

# AI Use Cases & Project Management for PMs
### Module 13

Spotting, scoring, scoping, and shipping AI features

---

## Agenda

1. A framework for spotting AI use cases
2. Use-case catalog: patterns and where they fit
3. Scoring and prioritizing
4. Writing the one-pager / business case
5. Working with engineering: scoping
6. Defining success metrics and evals
7. Rollout, risk, and governance
8. Common PM pitfalls

---

## 1. Spotting AI Use Cases

**Good signals**
- Language in, language out (reading, drafting, classifying, extracting)
- High volume, repetitive
- Existing examples/data (past tickets, transcripts, documents)
- Tolerant of an error rate, with a human/system safety net

**Red flags**
- Needs near-100% accuracy with no review step
- Needs information the model can't access or retrieve
- It's really a data/process problem, not a language problem

> Before scoping: what happens when the model is wrong, and who reviews it?

---

## 2. Use-Case Catalog

| Use case | Pattern | Modules |
|---|---|---|
| Drafting, summarizing, classifying | Single prompt, structured output | 01 |
| Internal knowledge search | RAG | 02, 05 |
| Support assistant with actions | Agent with tools | 03, 09 |
| Multi-step workflows | Multi-agent | 04 |
| Manuals/diagrams/charts | Multimodal RAG | 02 (Ex. 4) |
| Shared tool integrations | MCP server | 12 |
| Customer-facing / financial | + guardrails, approvals | 09 |
| High-volume, narrow-domain | Fine-tune / self-host | 08, 11 |
| Anything in production | + eval, monitoring, cost | 06, 07 |

🧭 This table is also a **complexity ladder** — bottom rows are multi-quarter programs

---

## 3. Scoring and Prioritizing

Score 1-5 on three axes:
- **Impact** — value if it works
- **Feasibility** — how close to a known pattern?
- **Risk** — *inverse*: 5 = low risk (reversible, internal), 1 = high risk

`priority_score = (Impact + Feasibility + Risk) / 3`

| Tier | Profile | Action |
|---|---|---|
| Quick win | High/High/Low-risk-score-high | Scope now |
| Strategic bet | High impact, lower feasibility/risk | Phased plan + sponsorship |
| Fill-in | Moderate impact, easy, low risk | Build momentum, not urgent |
| Reconsider | Low impact, or hard+risky | Revisit later |

`examples/01_use_case_scoring.py` implements this scoring

---

## 4. The One-Pager

1. **Problem** — current process & cost
2. **Proposed approach** — which catalog pattern?
3. **Success metrics** — business + quality/safety
4. **Risks & mitigations** — what happens when it's wrong?
5. **Estimated cost** — API cost × volume + eng effort
6. **Rollout plan** — phased (see Section 7)

`examples/templates/one_pager_template.md` — fill-in-the-blanks version

---

## 5. Scoping with Engineering

Before a sprint starts, can you answer:

- **Inputs:** single prompt, RAG, or live tools?
- **Outputs:** free text or structured?
- **Tools/actions:** owner + allow/approve/block (Module 09) + inline vs. MCP (Module 12)?
- **Eval plan:** how do we know "good enough" before launch? (Module 06)
- **Ops plan:** who watches cost/latency/quality after launch? (Module 07)

🧭 Can't answer all five? That's a **spike**, not a sprint.

---

## 6. Success Metrics & Evals

| Type | Examples |
|---|---|
| Business | Deflection rate, time-to-resolution, CSAT |
| Model/quality | Eval-set accuracy, hallucination rate, override rate |
| Cost & ops | Cost/request, p95 latency, fallback rate |

Pick **one number per row** and a target — *before* launch.

---

## 7. Rollout, Risk, Governance

1. **Shadow mode** — log only, compare against metrics
2. **Human-in-the-loop** — model drafts, human sends
3. **Auto for low-risk, approval for high-risk** (Module 09)
4. **Full automation** — only for proven, low-cost-of-error actions

Each phase needs an **exit metric** that decides advance / hold / rollback

---

## 8. Common PM Pitfalls

| Symptom | Mitigation |
|---|---|
| "Is this working?" unanswerable | Pick metrics + targets before launch |
| Endless "one more accuracy fix" | Build an eval set early, agree a threshold |
| Cost spike at launch | Estimate cost upfront, monitor after |
| Bad output → major incident | Phase rollout, classify actions first |
| Scope keeps growing | Ship "quick win" tier first |
| Eng/PM disagree on "done" | Answer Section 5's five questions before the sprint |

---

## Module 13 Hands-on

- `examples/01_use_case_scoring.py` — score and tier a backlog
- `examples/02_roi_estimator.py` — savings & payback estimate
- `examples/templates/one_pager_template.md` — business-case template
- `exercises/` — score a backlog, write a one-pager, set a launch gate

---

# Questions?

This is the end of the curriculum — revisit any module as needed.

