# Module 08 — Fine-Tuning

> **Goal:** Understand what fine-tuning actually changes about a model, when it's the right tool versus prompting or RAG, what it takes to prepare training data, and how to decide — and evaluate — whether a fine-tuned model is worth owning.

## Contents

- [1. Fine-tuning vs. prompting vs. RAG](#1-fine-tuning-vs-prompting-vs-rag)
- [2. What fine-tuning can and can't fix](#2-what-fine-tuning-can-and-cant-fix)
- [3. Data preparation](#3-data-preparation)
- [4. Evaluating a fine-tuned model vs. the base model](#4-evaluating-a-fine-tuned-model-vs-the-base-model)
- [5. Cost and maintenance implications](#5-cost-and-maintenance-implications)
- [6. Common failure modes](#6-common-failure-modes)
- [Hands-on](#hands-on)

---

## 1. Fine-tuning vs. prompting vs. RAG

Fine-tuning means taking a pre-trained model and continuing its training on your own examples, producing a new model artifact with adjusted weights. It is the heaviest-weight tool in the toolbox — and, for most teams, the *least* likely to be the right first move.

Before reaching for fine-tuning, ask whether the problem can be solved with:

- **A better prompt** (Module 01) — explicit instructions, examples, output format constraints. Cheapest, fastest to iterate, no new artifact to manage.
- **RAG** (Module 02) — if the model is missing *information*, retrieval almost always beats fine-tuning, because the knowledge stays current without retraining.
- **Tool use / structured output** (Module 01, 03) — if the issue is "the model can't do X reliably," sometimes the fix is giving it a tool or a schema, not new weights.

Fine-tuning becomes worth considering only when:

- You've already tried prompting and RAG, and they fall short on a *specific, measurable* dimension (e.g., output format consistency at scale, a narrow style/voice, classification accuracy on a domain-specific taxonomy).
- The behavior you need is something that can be demonstrated through examples but is too complex or too verbose to encode reliably in a prompt every single call.
- You're operating at a scale where shaving tokens off every request (by removing a long few-shot prompt) produces meaningful savings.

| Tool | Changes | Best for | Iteration speed |
|---|---|---|---|
| Prompting | Instructions sent with each request | Most behavior changes, format, tone, reasoning style | Minutes |
| RAG | What information the model has access to | Knowledge gaps, freshness, grounding in your data | Hours (re-index) |
| Tool use | What actions the model can take / what schema it returns | Structured output, taking actions, integrations | Minutes–hours |
| Fine-tuning | The model's weights themselves | Deeply ingrained style/format/behavior at scale, when prompting can't reliably get there | Days–weeks (data prep, training, eval, redeploy) |

🧑‍💼 **PM view:** Treat fine-tuning as a *last resort*, not a starting point. If someone proposes "let's fine-tune a model" as the first solution to a quality problem, the right response is "what did we try in the prompt, and what did the eval results show?" Fine-tuning adds a new artifact to your roadmap — versioning, retraining cadence, evaluation — that prompting and RAG don't.

🧑‍💻 **Engineer view:** In practice, the order of operations is almost always: (1) improve the prompt and add examples, (2) add retrieval if the model is missing facts, (3) add tools/structured output if the model needs to take actions or return parseable data, and only then (4) consider fine-tuning if a specific, measured gap remains after 1–3.

🧭 **Tech lead view:** Anthropic's fine-tuning offerings are more limited and enterprise-focused than some other providers (e.g., OpenAI's general-purpose fine-tuning API). For most teams building on Claude, the practical path to "make the model behave consistently in our domain" is a strong system prompt + few-shot examples + RAG + tool use — and that combination covers the vast majority of real-world needs. This module is intentionally a **decision framework**, not a hands-on fine-tuning walkthrough, because for most readers the right outcome is recognizing *when fine-tuning would apply in principle* and confirming, case by case, whether your model provider currently offers it for your use case.

---

## 2. What fine-tuning can and can't fix

A useful mental model: fine-tuning changes **how** the model responds, not **what it knows**.

### What fine-tuning is good at

- **Style and tone consistency** — e.g., always responding in a specific brand voice, register, or persona, without needing to repeat lengthy style instructions every call.
- **Format consistency at scale** — e.g., always producing a specific structured format for a narrow task, especially when few-shot examples in the prompt aren't sticking or are too expensive to include every time.
- **Domain-specific classification or extraction** — when you have thousands of labeled examples of a narrow task and need high accuracy without a long prompt.
- **Reducing prompt length / latency** — if a task currently requires a long system prompt with many examples, a fine-tuned model can sometimes achieve similar behavior with a much shorter prompt.

### What fine-tuning is bad at (or can't do at all)

- **Adding new knowledge or facts.** Fine-tuning on a set of Q&A pairs about your product does *not* reliably give the model broad, queryable knowledge of your product — it teaches the model to produce *similar-looking responses*, which can actually increase hallucination risk if the model pattern-matches to a fine-tuned style on topics it doesn't actually know about. For knowledge, use RAG.
- **Keeping up with frequently changing information.** Every update to "the facts" requires new training data and a new training run. A RAG index can be updated by re-embedding a document in minutes.
- **Fixing a model that's fundamentally not capable enough.** If the base model can't reason through a task even with a great prompt and examples, fine-tuning on the same task rarely produces a qualitatively different capability — it produces a model that's better at *mimicking the training examples*, which may or may not generalize.

🧑‍💼 **PM view:** If the underlying problem is "the model doesn't know about our latest product/policy/pricing," fine-tuning is the wrong fix even if it appears to work in a demo — it will go stale the moment the underlying facts change again, and you'll be back here next quarter. RAG (Module 02) is the durable fix for knowledge freshness.

🧑‍💻 **Engineer view:** A good gut-check before fine-tuning: can you describe the desired behavior change as "do X *style/format* of thing" rather than "know about Y"? If it's the latter, fine-tuning is not the tool.

---

## 3. Data preparation

If you do move forward with fine-tuning (with a provider that supports it for your use case), the core artifact is a **training dataset** of input/output examples that demonstrate the behavior you want.

### Format

Most fine-tuning APIs (and a common convention across providers) use **JSONL** (one JSON object per line), where each line is a training example. A common shape is a list of messages, mirroring the Messages API:

```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

Or, for simpler input/output pair tasks:

```json
{"input": "Summarize this ticket: ...", "output": "Customer reports duplicate billing charge; needs refund."}
```

### What makes a good training set

- **Consistency** — every example should follow the *exact* format, tone, and structure you want the model to learn. Inconsistent examples teach inconsistent behavior.
- **Coverage** — examples should span the range of inputs the model will see in production, including edge cases, not just the "happy path."
- **Volume** — fine-tuning typically needs hundreds to thousands of high-quality examples; a handful of examples is better served by few-shot prompting.
- **Quality over quantity** — a smaller set of carefully curated, correct examples beats a large set with inconsistent or low-quality outputs. Bad examples teach bad patterns.
- **No PII / sensitive data** unless your data handling agreement with the provider explicitly covers it — training data may be retained differently than inference-time data (see Module 09 on data privacy).

### Where examples come from

- Curated "gold" examples written or reviewed by domain experts.
- Real production interactions that were rated highly (e.g., by users or by an LLM-as-judge eval, Module 06) — but review before including, since "what users accepted" isn't always "what you want the model to learn."
- Synthetic examples generated by a stronger model and then human-reviewed — useful for bootstrapping coverage, but watch for the model learning the *generating* model's quirks.

🧑‍💼 **PM view:** Data preparation is usually the most time-consuming part of a fine-tuning project — often more effort than the training itself. Budget for a human review pass over the training data; "garbage in, garbage out" applies directly to model weights.

🧑‍💻 **Engineer view:** Validate your dataset programmatically before submitting it anywhere: check that every line is valid JSON, that required fields are present, that the schema is consistent across all examples, and that there's no obviously sensitive data. See [`examples/01_prepare_training_data.py`](examples/01_prepare_training_data.py).

---

## 4. Evaluating a fine-tuned model vs. the base model

A fine-tuned model is a new model artifact — and like any other model or prompt change, it needs to go through the same evaluation discipline covered in **Module 06 (LLM Evaluation & Testing)**:

1. **Use the same evaluation set** you'd use to test a prompt change — representative inputs with expected properties of the output.
2. **Run both the base model (with your best prompt) and the fine-tuned model** against that same evaluation set.
3. **Compare using the same metrics** — accuracy/quality (often via LLM-as-judge), format compliance, latency, and cost.
4. **Look for regressions, not just improvements on the target task.** Fine-tuning can improve the narrow behavior you trained on while making the model worse at *other* things it used to do well (a form of overfitting / catastrophic forgetting). Your eval set should include "things outside the fine-tuning focus that still need to work."

This is exactly the "before vs. after" comparison pattern from Module 06 — the only difference is that "before" and "after" are two different models (or a base model with a prompt vs. a fine-tuned model with a shorter prompt) instead of two prompt versions.

🧑‍💼 **PM view:** "The fine-tuned model feels better in my testing" is not a launch criterion. Require a side-by-side eval report against the same eval set used for the current production prompt, with explicit numbers, before considering a fine-tuned model for production.

🧭 **Tech lead view:** Treat the fine-tuned model as you would a new model version in your config (Module 01's model-selection pattern) — gate it behind the same eval harness, and keep the prompt-based baseline as a fallback you can roll back to.

---

## 5. Cost and maintenance implications

Owning a fine-tuned model is not a one-time cost — it's an ongoing commitment:

- **Training cost** — running the fine-tuning job itself (data volume and number of epochs drive cost).
- **Hosting/inference cost** — fine-tuned models are sometimes priced differently (often higher per-token) than base models, and may have different availability/throughput characteristics.
- **Versioning** — every time you improve your training data or fix a problem, you need a new fine-tuned model version, with its own evaluation pass before replacing the one in production.
- **Base model lifecycle** — when the underlying base model is deprecated or a new version is released, your fine-tuned model may need to be retrained against the new base — you don't get newer-base-model improvements for free.
- **Data pipeline maintenance** — the training dataset itself needs to be kept up to date as your product, policies, or domain change, or the fine-tuned model will reinforce stale patterns.

🧑‍💼 **PM view:** Ask "who owns retraining this model when X changes?" before greenlighting a fine-tuning project. If the answer is "nobody, we'll deal with it later," that's a sign the team isn't ready to own this artifact.

🧭 **Tech lead view:** Compare the *total cost of ownership* of fine-tuning (data curation, training runs, evaluation, retraining cadence, hosting) against the *recurring* cost of a longer prompt / RAG retrieval per request. For many workloads, the recurring per-token cost of a longer prompt is cheaper than the engineering cost of maintaining a fine-tuned model — especially once you account for eng time.

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Fine-tuned model "knows" outdated facts | Fine-tuning was used to inject knowledge instead of RAG | Move factual content to a retrieval index; reserve fine-tuning for style/format |
| Model performs well on the fine-tuning task but worse on everything else | Overfitting / catastrophic forgetting from narrow or low-diversity training data | Broaden training data coverage; include eval cases outside the target task; consider a smaller fine-tuning effort or better prompting instead |
| Inconsistent training examples produce inconsistent model behavior | Training data wasn't validated for schema/format consistency before submission | Run a validation pass (schema, required fields) before training — see `examples/01_prepare_training_data.py` |
| "It works in my demo" but no measurable improvement in production | No structured before/after evaluation against a shared eval set | Use the Module 06 evaluation harness to compare base vs. fine-tuned on the same eval set, with explicit metrics |
| Fine-tuned model becomes stale after a few months | No retraining plan, base model deprecated upstream | Treat the fine-tuned model as a versioned artifact with an owner and a retraining cadence |
| Team jumps straight to fine-tuning for a knowledge or formatting problem | No decision framework / fine-tuning treated as default | Apply the decision framework in Section 1 — prompting and RAG first |

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — data preparation and a conceptual base-vs-specialized evaluation harness
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions
