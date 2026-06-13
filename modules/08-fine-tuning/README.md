# Module 08 — Fine-Tuning

> Status: 🚧 Planned — structure below shows what this module will contain.

## What you'll learn

- Fine-tuning vs. prompting vs. RAG — when each is the right tool
- What fine-tuning can and can't fix (style/format vs. knowledge)
- Data preparation: collecting and formatting training examples
- Evaluating a fine-tuned model against the base model
- Cost and maintenance implications of owning a fine-tuned model

🧑‍💼 **PM view:** Fine-tuning is usually the *last* resort, not the first — prompting and RAG are cheaper, faster to iterate, and easier to keep up to date. Fine-tuning makes sense when you need a consistent style/format at scale that prompting can't reliably achieve.

🧭 **Tech lead view:** A fine-tuned model is a new artifact you own — it needs versioning, evaluation, and a plan for what happens when the underlying base model is updated.

## Planned contents

```
modules/08-fine-tuning/
├── README.md
├── presentation/slides.md
├── examples/
│   ├── 01_prepare_training_data.py
│   └── 02_evaluate_finetuned_vs_base.py
└── exercises/
```
