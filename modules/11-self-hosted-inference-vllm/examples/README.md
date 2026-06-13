# Module 11 — Examples

## [`01_start_vllm_server.md`](01_start_vllm_server.md)

Reference (not runnable here) for installing vLLM and starting its
OpenAI-compatible API server. Requires a CUDA-capable GPU.

## [`02_openai_compatible_client.py`](02_openai_compatible_client.py)

Queries an OpenAI-compatible endpoint (a running vLLM server, or any other
local server with the same API shape, e.g. Ollama) using the `openai` Python
client.

```bash
pip install -r requirements.txt
export VLLM_BASE_URL=http://localhost:8000/v1   # default shown
export VLLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
python 02_openai_compatible_client.py
```

Requires a running OpenAI-compatible server - it will fail to connect
otherwise.

## [`03_cost_comparison.py`](03_cost_comparison.py)

No server or API key needed. A back-of-envelope calculator for the request
volume at which a self-hosted GPU's fixed cost crosses over a managed API's
per-token cost.

```bash
python 03_cost_comparison.py
```
