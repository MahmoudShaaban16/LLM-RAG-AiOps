---
marp: true
title: Fine-Tuning — A Decision Framework
paginate: true
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

## Hands-on

- `examples/01_prepare_training_data.py`
- `examples/02_evaluate_finetuned_vs_base.py`
- `exercises/` — decision framework + dataset prep practice

---

# Questions?

Next module: **Security & Responsible AI** →
