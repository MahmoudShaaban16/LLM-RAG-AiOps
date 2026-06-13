# Module 07 — Examples

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
| [`01_prompt_caching.py`](01_prompt_caching.py) | Anthropic prompt caching with `cache_control: {"type": "ephemeral"}`, and the `cache_creation_input_tokens` / `cache_read_input_tokens` usage fields |
| [`02_request_logging_and_cost_tracking.py`](02_request_logging_and_cost_tracking.py) | A wrapper around `client.messages.create` that logs request metadata (tokens, latency, estimated cost) and prints a cost summary per feature/user |
| [`03_fallback_and_retry.py`](03_fallback_and_retry.py) | Retry with exponential backoff for transient errors, plus a model fallback chain (Sonnet -> Haiku) |

Run any script directly:

```bash
python 01_prompt_caching.py
python 02_request_logging_and_cost_tracking.py
python 03_fallback_and_retry.py
```

Note on `01_prompt_caching.py`: prompt caching benefits are most visible
with larger cached blocks (real system prompts are often thousands of
tokens) and across many requests in quick succession. The numbers you see
locally with a single run may differ from production-scale behavior — always
check `response.usage` to confirm caching is behaving as expected.
