---
marp: true
title: LLM Fundamentals & Prompting
paginate: true
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

## Hands-on

- `examples/01_first_api_call.py`
- `examples/02_token_counting.py`
- `examples/03_prompting_techniques.py`
- `examples/04_structured_output.py`
- `exercises/` — practice problems + solutions

---

# Questions?

Next module: **RAG Systems** →
