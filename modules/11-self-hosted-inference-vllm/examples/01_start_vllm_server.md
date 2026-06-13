# Starting a vLLM server

This is a reference, not a runnable script — starting vLLM requires a
CUDA-capable GPU, which this repo's examples don't assume you have.

## Install

```bash
pip install vllm
```

## Serve a model

```bash
vllm serve mistralai/Mistral-7B-Instruct-v0.2
```

This starts an OpenAI-compatible API server on `http://localhost:8000` by
default. Useful flags:

```bash
vllm serve mistralai/Mistral-7B-Instruct-v0.2 \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 8192 \
    --tensor-parallel-size 1
```

- `--gpu-memory-utilization` — fraction of GPU memory vLLM is allowed to use
  for model weights + KV cache. Too low wastes capacity (fewer concurrent
  requests); too high risks out-of-memory errors under load.
- `--max-model-len` — caps the context length vLLM will serve. Lower values
  free up memory for more concurrent requests (Section 3 of the module
  README — PagedAttention/continuous batching).
- `--tensor-parallel-size` — number of GPUs to split a single model across,
  for models too large for one GPU.

## Verify it's up

```bash
curl http://localhost:8000/v1/models
```

Once the server responds, [`02_openai_compatible_client.py`](02_openai_compatible_client.py)
shows how to call it from Python.
