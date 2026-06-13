# Module 01 — Examples

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
| [`01_first_api_call.py`](01_first_api_call.py) | A minimal, config-driven call to the Messages API |
| [`02_token_counting.py`](02_token_counting.py) | Counting tokens before sending a request, and reading usage from a response |
| [`03_prompting_techniques.py`](03_prompting_techniques.py) | System prompts, few-shot examples, and step-by-step reasoning |
| [`04_structured_output.py`](04_structured_output.py) | Getting reliable JSON output via structured outputs |

Run any script directly:

```bash
python 01_first_api_call.py
```
