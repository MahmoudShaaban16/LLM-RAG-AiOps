# Module 06 — Examples

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
| [`01_eval_dataset.py`](01_eval_dataset.py) | Defining a small eval dataset (inputs + expected criteria) and running each input through the model |
| [`02_llm_as_judge.py`](02_llm_as_judge.py) | Using a second Claude call as a judge, with structured output (1-5 score + reasoning), to score outputs from `01_eval_dataset.py` |
| [`03_prompt_regression_test.py`](03_prompt_regression_test.py) | Running an old vs. new system prompt against the eval dataset, scoring both with the judge, and printing a regression-test-style comparison table |

Run any script directly:

```bash
python 01_eval_dataset.py
python 02_llm_as_judge.py
python 03_prompt_regression_test.py
```

Note: `02_llm_as_judge.py` and `03_prompt_regression_test.py` import from
`01_eval_dataset.py` (and `02_llm_as_judge.py`) using `importlib` — run them
from inside this `examples/` directory so the import resolves.

Each script makes multiple API calls (one per eval case, plus one judge call
per case) — expect `03_prompt_regression_test.py` to make roughly
`2 x len(EVAL_DATASET) x 2` calls (generation + judging, for both prompt
variants).
