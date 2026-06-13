# Module 08 — Examples

Runnable scripts demonstrating the concepts from the module README.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Scripts

| Script | Demonstrates |
|---|---|
| [`01_prepare_training_data.py`](01_prepare_training_data.py) | Formatting input/output examples into JSONL training data, with schema validation — pure data prep, no fine-tuning API call |
| [`02_evaluate_finetuned_vs_base.py`](02_evaluate_finetuned_vs_base.py) | A conceptual base-vs-"fine-tuned" comparison using two system prompts and the Module 06 LLM-as-judge pattern |

Run any script directly:

```bash
python 01_prepare_training_data.py
python 02_evaluate_finetuned_vs_base.py
```

Note: `01_prepare_training_data.py` does not require `ANTHROPIC_API_KEY` — it's
local data processing only. `02_evaluate_finetuned_vs_base.py` makes several
API calls (one generation + one judge call per model per eval case).
