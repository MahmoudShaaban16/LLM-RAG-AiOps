---
marp: true
title: Production Capstone
paginate: true
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

## Hands-on

- `examples/capstone_app/main.py` — single-file, ~150 lines, full pipeline
- `exercises/` — add a tool, build an eval set, add a guardrail

---

# Questions?

This is the end of the core curriculum — revisit any module as needed.
