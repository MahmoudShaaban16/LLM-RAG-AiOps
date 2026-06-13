---
marp: true
title: Self-Hosted Inference with vLLM
paginate: true
---

# Self-Hosted Inference with vLLM
### Module 11

When (and how) teams run open-weight models on their own GPUs

---

## Agenda

1. What is vLLM?
2. Why self-host at all? API vs. self-hosted
3. How vLLM makes self-hosting practical
4. Deploying vLLM: the OpenAI-compatible server
5. A decision framework: API, self-hosted, or both?
6. Common failure modes

---

## 1. What is vLLM?

- An open-source **inference/serving engine** for open-weight LLMs (Llama, Mistral, Qwen, ...)
- Not a model — the runtime that serves a model efficiently and exposes an API

```
Model weights  ≈  the application code
vLLM           ≈  the web server / runtime that runs it efficiently
```

> Quality ceiling = whatever open-weight model you choose, generally below frontier hosted models

---

## 2. API vs. Self-Hosted

| | Managed API | Self-hosted (vLLM) |
|---|---|---|
| Infra | Provider runs it | You run it |
| Cost shape | Variable, $/token | Fixed, GPU-hours |
| Quality ceiling | Frontier models | Best open-weight model |
| Data residency | Sent to provider | Stays in your infra |
| Ops burden | None | Capacity, upgrades, failures, scaling |
| Time to first request | Minutes | Hours-days |

**PM takeaway:** not "cheaper" in the abstract — depends on volume, compliance, and ops capacity.

---

## 3. How vLLM Makes Self-Hosting Practical

**PagedAttention**
- Manages the KV cache like OS virtual memory — fixed-size pages, allocated on demand
- Drastically reduces memory waste → more concurrent requests per GPU

**Continuous batching**
- Adds/removes requests from the running batch on the fly
- Keeps the GPU busy under real, bursty traffic

**Also:** quantization (AWQ/GPTQ/FP8), tensor parallelism, LoRA adapter serving (Module 08)

---

## 4. Deploying vLLM

```bash
pip install vllm
vllm serve mistralai/Mistral-7B-Instruct-v0.2
```

OpenAI-compatible API on `localhost:8000`:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
response = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    messages=[{"role": "user", "content": "Summarize this in one sentence: ..."}],
)
```

**Same shape as Ollama, LM Studio, TGI** — pattern generalizes

---

## 5. Decision Framework: API, Self-Hosted, or Both?

| Question | "Yes" favors self-hosting |
|---|---|
| High & steady volume? | Fixed GPU cost amortizes better |
| Data residency requires it? | May be a hard requirement |
| Open-weight model good enough (per Module 06 evals)? | Quality tradeoff acceptable |
| Have ML infra expertise? | Someone owns GPUs + incidents |
| Latency-insensitive / has fallback? | Easier to absorb learning curve |

**Hybrid is common:** self-host for high-volume narrow tasks, API for frontier reasoning/tool use.

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| OOM under load | Tune GPU memory/batch settings, consider quantization |
| Self-hosted costs more than API | Right-size GPUs to sustained load, or fall back to API for overflow |
| Quality regression after switching | Re-run Module 06 eval suite before shipping |
| Tool use/structured output breaks | Verify support for your model + server version |
| No cost/failure visibility | Apply Module 07 observability to your own server |
| GPU node failure = outage | Fallback chain to a managed API |

---

## Hands-on

- `examples/02_openai_compatible_client.py` — query an OpenAI-compatible endpoint
- `examples/03_cost_comparison.py` — self-hosted GPU vs. API cost crossover
- `exercises/` — decision framework + cost-modeling practice

---

# Questions?

Next: revisit any module, or return to the [curriculum overview](../../../README.md)
