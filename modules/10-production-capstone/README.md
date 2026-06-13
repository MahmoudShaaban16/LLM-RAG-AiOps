# Module 10 — Production Capstone

> **Goal:** Combine everything from Modules 01–09 into a single, small-but-complete application: a support-ticket assistant that retrieves relevant docs (RAG), uses tools (agent), is guarded against prompt injection, and is evaluated and observed like a production service.

## Contents

- [1. What we're building](#1-what-were-building)
- [2. Architecture](#2-architecture)
- [3. How each module shows up here](#3-how-each-module-shows-up-here)
- [4. Running the capstone](#4-running-the-capstone)
- [5. Where to go next](#5-where-to-go-next)

---

## 1. What we're building

A **support ticket triage assistant**. Given an incoming support ticket, it:

1. Retrieves relevant help-center articles (RAG — Module 02) using a small in-memory vector index (Module 05)
2. Decides whether it can answer directly or needs to call a tool (Module 03) — e.g., `check_order_status`
3. Produces a structured triage result: category, urgency, suggested response, and whether a human needs to review it
4. Runs through a guardrail layer that treats retrieved/tool content as untrusted (Module 09)
5. Logs cost/latency for observability (Module 07)

🧑‍💼 **PM view:** This is the shape of a realistic v1 feature — small enough to ship, but it touches retrieval, tool use, structured output, guardrails, and observability. Most "AI features" in production are variations on this pattern.

🧭 **Tech lead view:** Notice what's *not* here: no fine-tuning (Module 08), no multi-agent orchestration (Module 04). Both were deliberately left out because the base task doesn't need them — a good architecture review asks "what can we leave out" as much as "what do we need." [`main_extended.py`](examples/capstone_app/main_extended.py) shows what adding them back looks like, *if* a measured need arises (see section 3a below).

---

## 2. Architecture

```
                    ┌─────────────────────┐
incoming ticket --> │  Guardrail layer     │  (Module 09: wrap untrusted text in
                    │  (input wrapping)    │   delimited tags before it reaches the model)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Retrieval (RAG)     │  (Module 02 + 05: TF-IDF / embedding
                    │  over help articles  │   search over a small KB)
                    └──────────┬──────────┘
                               │ relevant articles
                    ┌──────────▼──────────┐
                    │  Claude + tools      │  (Module 03: tool_choice may call
                    │  (triage agent)      │   check_order_status)
                    └──────────┬──────────┘
                               │ structured tool_use result
                    ┌──────────▼──────────┐
                    │  Guardrail layer     │  (Module 09: validate tool calls,
                    │  (output validation) │   flag if human review required)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Cost/latency log    │  (Module 07: observability)
                    └──────────────────────┘
```

---

## 3. How each module shows up here

| Module | Where it appears in the capstone |
|---|---|
| 01 — Fundamentals & Prompting | The system prompt, structured-output tool schema, and model choice (`claude-sonnet-4-6`) |
| 02 — RAG Systems | `retrieve_relevant_articles()` — TF-IDF retrieval over a small help-center knowledge base |
| 03 — AI Agents | The triage call exposes a `check_order_status` tool; the model decides whether to call it |
| 05 — Vector DBs & Embeddings | The retrieval index is the same "in-memory similarity search" pattern from Module 05 |
| 06 — Evaluation | `exercises/` asks you to build an eval set for the triage assistant |
| 07 — LLMOps & AIOps | `log_request()` records tokens, latency, and estimated cost for every call |
| 09 — Security & Responsible AI | Retrieved articles and ticket text are wrapped in `<untrusted_input>` tags with explicit handling instructions |

---

## 3a. The extended version: adding back Modules 04 and 08

[`main_extended.py`](examples/capstone_app/main_extended.py) builds on
`main.py` and adds the two modules left out of the base capstone:

- **Module 04 (Multi-Agent Systems):** the triage agent acts as a
  **supervisor**. When it flags a billing ticket for human review, it hands
  off to a **billing specialist worker agent** (`escalate_to_billing_specialist()`)
  with its own narrow system prompt, the refund policy, and a
  `submit_billing_review` tool. The worker's decision (refund recommended?
  revised response?) is attached to the triage result.
- **Module 08 (Fine-Tuning):** after a batch of tickets is processed,
  `fine_tuning_recommendation()` runs the category distribution through the
  Module 08 decision framework — if one category dominates at volume, it
  flags that as worth evaluating for fine-tuning (after confirming
  prompting + RAG hasn't closed the gap); otherwise it recommends staying
  with prompting + RAG.

🧭 **Tech lead view:** This is the point of the exercise — `main.py` is the
right architecture for the *stated* scope, and `main_extended.py` is what you
add **only when a specific, measured need appears** (a recurring billing
dispute volume that needs specialist handling, or a category large enough to
justify fine-tuning). Shipping the extended version from day one would be
premature complexity.

---

## 4. Running the capstone

```bash
cd modules/10-production-capstone/examples/capstone_app
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python main.py
```

This runs a few sample tickets through the full pipeline and prints, for each: the retrieved articles, the model's structured triage decision, any tool calls made, and the logged cost/latency.

🧑‍💻 **Engineer view:** Read [`examples/capstone_app/main.py`](examples/capstone_app/main.py) top to bottom — it's intentionally a single file (~150 lines) so you can see the whole pipeline without jumping between modules. In a real codebase you'd split retrieval, guardrails, and logging into separate modules.

---

## 5. Where to go next

- 📊 [Presentation slides](presentation/slides.md) — walk through the architecture with your team
- 💻 [`examples/capstone_app/`](examples/capstone_app/) — the full application
- ✏️ [Exercises](exercises/) — extend the capstone (add a new tool, build an eval set, add a new guardrail)

If you've worked through Modules 01–09, this module should feel like a synthesis, not new material. If any part feels unfamiliar, that's a signal to revisit the corresponding module.
