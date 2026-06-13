---
marp: true
title: LLM Evaluation & Testing
paginate: true
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

## Hands-on

- `examples/01_eval_dataset.py`
- `examples/02_llm_as_judge.py`
- `examples/03_prompt_regression_test.py`
- `exercises/` — practice problems + solutions

---

# Questions?

Next module: **LLMOps & AIOps** →
