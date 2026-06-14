# Module 06 — LLM Evaluation & Testing

> **Goal:** Move from "it worked when I tried it" to a repeatable, measurable way to know whether an LLM-powered feature works — and whether a prompt or model change made it better or worse.

## Contents

- [1. Why traditional unit tests don't fully cover LLM behavior](#1-why-traditional-unit-tests-dont-fully-cover-llm-behavior)
- [2. Building an evaluation dataset](#2-building-an-evaluation-dataset)
- [3. LLM-as-judge](#3-llm-as-judge)
- [4. Regression testing for prompts](#4-regression-testing-for-prompts)
- [5. Metrics that matter](#5-metrics-that-matter)
- [6. Common failure modes](#6-common-failure-modes)
- [Tools & Resources](#tools--resources)
- [Hands-on](#hands-on)

---

## 1. Why traditional unit tests don't fully cover LLM behavior

A normal unit test asserts an exact value: `assert add(2, 3) == 5`. LLM outputs don't work that way — the same prompt can produce different (but equally valid) wording on every call, and "correct" is often a matter of degree rather than an exact match.

```
assert response == "The capital of France is Paris."   # too brittle — fails on
                                                          # "Paris is the capital of France."
```

Two properties make LLM behavior fundamentally different from typical code under test:

- **Non-determinism** — even at low temperature, outputs vary in phrasing, length, and structure between runs.
- **Open-ended correctness** — there's often no single "right" output, only a set of *properties* a good output should have (e.g., "mentions the refund policy," "is under 100 words," "doesn't promise a specific delivery date").

This doesn't mean LLM features are untestable — it means the *kind* of test changes: from exact-match assertions to **evaluations** that check whether outputs satisfy expected properties, scored across a representative set of inputs.

🧑‍💼 **PM view:** "It worked when I tried it three times" is not a quality bar — it's anecdote. An evaluation set is what lets you say "94% of our test cases pass the quality bar" and track that number over time, the same way you'd track a bug count or test-pass rate for traditional software.

🧑‍💻 **Engineer view:** You still write traditional unit tests for the deterministic parts of your system (parsing, retries, schema validation, business logic around the LLM call). The LLM call itself needs a different kind of test: an **eval** — a dataset of inputs plus a way to score whether each output meets expectations.

🧭 **Tech lead view:** Without an eval suite, every prompt change or model swap is a leap of faith reviewed by "does it look okay in a quick manual check." With one, the same change becomes a before/after comparison with a number attached — which is what lets you approve changes with confidence (and roll them back with evidence).

---

## 2. Building an evaluation dataset

An evaluation dataset is a list of **representative inputs**, each paired with **expected properties** of a good response — not necessarily an exact expected output.

```python
EVAL_DATASET = [
    {
        "id": "refund_policy_basic",
        "input": "Can I get a refund if I bought the annual plan 2 months ago?",
        "criteria": [
            "States whether a refund is possible under the stated policy",
            "Mentions the relevant time window (e.g., 30-day policy)",
            "Does not invent a policy detail not in the source material",
        ],
    },
    ...
]
```

What makes a good eval dataset:

- **Representative** — covers the realistic range of inputs your feature will see: typical cases, edge cases, adversarial/ambiguous cases, and known-hard cases from production (real complaints, real bug reports).
- **Small enough to run often, large enough to be meaningful** — 20-50 well-chosen cases catch far more regressions than 500 near-duplicates. Start small and grow it as you find new failure cases.
- **Living, versioned data** — store it in your repo alongside the prompts it tests. When a bug is found in production, add the input that triggered it as a new eval case so it can never silently regress again.

🧑‍💼 **PM view:** Building the eval dataset *is* writing down acceptance criteria — the same exercise as writing a spec, just in a form a program can check. This is a great activity to do collaboratively with whoever owns the product requirements.

🧭 **Tech lead view:** Treat the eval dataset like test fixtures — version-controlled, reviewed in PRs, and grown incrementally. Every production incident caused by an LLM output is a candidate new eval case.

---

## 3. LLM-as-judge

For open-ended outputs, a second LLM call can act as a **judge**: given the input, the criteria, and the model's output, the judge scores how well the output meets the criteria.

```
[input] + [output to evaluate] + [criteria]
        │
        ▼
   judge model (often the same or a stronger model)
        │
        ▼
  { "score": 4, "reasoning": "..." }
```

Key practices:

- **Use structured output for the judge's verdict** — force a JSON response (via tool calling, as in [`examples/02_llm_as_judge.py`](examples/02_llm_as_judge.py)) so scores are easy to aggregate. This mirrors the structured-output pattern from [Module 01](../01-llm-fundamentals-and-prompting/examples/04_structured_output.py).
- **Give the judge a rubric, not just "is this good?"** — a numeric scale (e.g., 1-5) with a description of what each score means produces far more consistent results than an open-ended judgment.
- **Have the judge explain its score** — a short `reasoning` field makes it possible to spot-check disagreements and catch a judge that's systematically too lenient or too harsh.
- **The judge is not infallible** — periodically spot-check judge scores against human judgment, especially after changing the judge's prompt or model.

🧑‍💼 **PM view:** LLM-as-judge turns "read 50 transcripts and eyeball them" into an automated score that runs on every change — but it's a *proxy* for quality, not a replacement for occasional human review, especially for high-stakes outputs.

🧑‍💻 **Engineer view:** A judge call is just another `client.messages.create` call with `tools` + `tool_choice` forcing a schema like `{"score": int, "reasoning": str}`. Run it once per (input, output, criteria) triple in your eval set.

🧭 **Tech lead view:** Using a *stronger* model as judge than the one being evaluated (e.g., Opus judging Sonnet output) generally gives more reliable scores — but at higher per-eval-run cost. For CI runs on every PR, a same-tier judge with a tight rubric is often a reasonable tradeoff.

---

## 4. Regression testing for prompts

A **prompt regression test** runs the *same eval dataset* against two prompt (or model) variants — the current one and a proposed change — and compares the scores.

```
                  ┌──────────────┐
 EVAL_DATASET ───▶│ PROMPT (old) │──▶ outputs ──▶ judge ──▶ scores_old
                  └──────────────┘
                  ┌──────────────┐
 EVAL_DATASET ───▶│ PROMPT (new) │──▶ outputs ──▶ judge ──▶ scores_new
                  └──────────────┘
                          │
                          ▼
              compare scores_old vs scores_new
```

This is the same idea as a regression test suite in traditional software: it doesn't prove the new version is bug-free, but it catches *known* failure modes from recurring, and it gives you a number to look at before merging a prompt change.

What to do with the result:

- **Net improvement, no per-case regressions** — safe to ship.
- **Net improvement, but some individual cases got worse** — investigate those cases specifically; an average can hide a regression on an important case.
- **No significant change** — the prompt change may be neutral; consider other criteria (cost, latency, length) to decide.
- **Net regression** — don't ship as-is; the eval just did its job.

🧑‍💼 **PM view:** This is the artifact you want before approving "let's switch to Haiku to cut costs" or "let's rewrite the system prompt for tone." It turns a subjective debate into a side-by-side comparison.

🧭 **Tech lead view:** Wire this into CI as a check on PRs that touch prompts or model configuration — even a lightweight version (5-10 eval cases, cheap judge model) catches obvious regressions before they reach production. See [`examples/03_prompt_regression_test.py`](examples/03_prompt_regression_test.py).

---

## 5. Metrics that matter

No single number captures "is this LLM feature good." Track several together:

| Metric | What it tells you | How to measure |
|---|---|---|
| **Quality / accuracy** | Are outputs correct and meeting criteria? | LLM-as-judge scores against the eval dataset; for classification-style tasks, exact-match against labeled data |
| **Latency** | How long users wait | Wall-clock time per `messages.create` call (p50/p95, not just average) |
| **Cost** | $ per request / per user / per feature | `usage.input_tokens` + `usage.output_tokens` × pricing (Module 07 covers tracking this in production) |
| **Consistency** | How much output varies across repeated runs of the same input | Run each eval input N times; measure variance in judge scores or output structure |

🧑‍💼 **PM view:** Quality, latency, and cost usually trade off against each other (a bigger model is often higher-quality but slower and more expensive). Decide upfront which axis is the hard constraint (e.g., "must respond in under 2 seconds") vs. which is being optimized (quality, within that constraint).

🧭 **Tech lead view:** Track these metrics over time, not just at one point in time — a model provider update or an upstream data change can cause **quality drift** even with no code changes on your side (Module 07).

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Eval scores look great but production complaints persist | Eval dataset doesn't cover real user inputs | Mine production logs/incidents for new eval cases; keep the dataset living |
| Judge scores are inconsistent across runs | Vague rubric, no structured output, judge temperature too high | Give the judge a concrete 1-5 rubric, force JSON via tool_choice, use temperature 0 |
| A prompt change "improves" the average score but breaks one important case | Aggregating to a single average hides per-case regressions | Always inspect per-case deltas, not just the mean, before shipping |
| Eval suite takes too long / costs too much to run on every PR | Dataset too large, or using an expensive model for every eval+judge call | Maintain a small "fast" subset for CI and a larger "full" suite for periodic/release runs |
| Judge consistently rates everything highly (or low) | Judge model has a bias, or rubric is too lenient/strict | Spot-check judge output against human ratings; tune the rubric description per score level |
| "Regression test" passes, but the new prompt is more verbose/costly | Only quality was measured, not cost/latency | Include token usage and latency in the comparison table, not just the judge score |

---

## Tools & Resources

🧑‍💻 **Engineer view — SDKs & libraries**

| Tool / Library | What it's for |
|---|---|
| [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) | `client.messages.create(..., tools=[...])` — used to build the LLM-as-judge pattern in this module's examples |
| [promptfoo](https://www.promptfoo.dev/) | Open-source CLI/framework for building eval datasets and running prompt regression tests |
| [LangSmith](https://docs.smith.langchain.com/) | Tracing and evaluation platform for tracking eval runs and comparing prompt/model versions over time |

📚 **Further reading**

- [Anthropic — Develop test cases for evaluation](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests) — guidance on building eval datasets and grading approaches
- [Anthropic — Tool use (function calling)](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — reference for forcing structured judge output via `tool_choice`

🧑‍💼 **PM view:** If coding the examples isn't practical for your role, see [`exercises/pm_track.md`](exercises/pm_track.md) for a no-code exercise covering the same decisions (what makes a good eval set, how to read LLM-as-judge scores, and when a prompt change is safe to ship) using a worked scenario.

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — runnable scripts demonstrating an eval dataset, LLM-as-judge, and a prompt regression test
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions (including a non-coding [PM track](exercises/pm_track.md))
