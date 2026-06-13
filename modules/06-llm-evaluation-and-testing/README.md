# Module 06 — LLM Evaluation & Testing

> Status: 🚧 Planned — structure below shows what this module will contain.

## What you'll learn

- Why traditional unit tests don't fully cover LLM behavior (non-determinism, open-ended output)
- Building an evaluation set: representative inputs + expected properties of outputs
- LLM-as-judge: using a model to evaluate another model's output
- Regression testing for prompts — catching quality drops when you change a prompt or model
- Metrics that matter: accuracy/quality, latency, cost, and consistency

🧑‍💼 **PM view:** "It worked when I tried it" is not a quality bar. An evaluation set turns prompt/model changes into measurable before/after comparisons — essential for sign-off on changes.

🧭 **Tech lead view:** Build the evaluation harness early — it pays for itself the first time someone proposes "let's just switch to a cheaper model" or "let's tweak the system prompt."

## Planned contents

```
modules/06-llm-evaluation-and-testing/
├── README.md
├── presentation/slides.md
├── examples/
│   ├── 01_eval_dataset.py
│   ├── 02_llm_as_judge.py
│   └── 03_prompt_regression_test.py
└── exercises/
```
