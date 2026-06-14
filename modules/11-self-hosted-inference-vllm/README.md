# Module 11 — Self-Hosted Inference with vLLM

> **Goal:** Understand when and why teams self-host open-weight models instead of (or alongside) calling a managed API like the Anthropic API, how an inference server like [vLLM](https://github.com/vllm-project/vllm) makes that practical, and how to reason about the cost/ops tradeoffs.

## Contents

- [1. What is vLLM?](#1-what-is-vllm)
- [2. Why self-host at all? API vs. self-hosted](#2-why-self-host-at-all-api-vs-self-hosted)
- [3. How vLLM makes self-hosting practical](#3-how-vllm-makes-self-hosting-practical)
- [4. Deploying vLLM: the OpenAI-compatible server](#4-deploying-vllm-the-openai-compatible-server)
- [5. A decision framework: API, self-hosted, or both?](#5-a-decision-framework-api-self-hosted-or-both)
- [6. Common failure modes](#6-common-failure-modes)
- [Tools & Resources](#tools--resources)
- [Hands-on](#hands-on)

---

## 1. What is vLLM?

[vLLM](https://github.com/vllm-project/vllm) is an open-source **inference and serving engine** for large language models. It takes an open-weight model (Llama, Mistral, Qwen, and many others on Hugging Face) and serves it efficiently — handling batching, memory management, and exposing an API — so you can run that model on your own GPUs instead of (or in addition to) calling a hosted model API.

It is **not** a model — it's the serving layer underneath one. The analogy:

```
Model weights  ≈  the application code
vLLM           ≈  the web server / runtime that runs it efficiently and exposes an API
```

🧑‍💼 **PM view:** vLLM doesn't give you a *better* model — it gives you a way to run an *open-weight* model yourself, with throughput and latency characteristics close to what specialized inference providers offer. The model quality ceiling is whatever open-weight model you choose, which today is generally below frontier hosted models like Claude for hard reasoning tasks.

🧑‍💻 **Engineer view:** If you've called `client.messages.create()` against the Anthropic API throughout this curriculum, vLLM's default server exposes an **OpenAI-compatible** `/v1/chat/completions` endpoint — so the request/response shape is familiar, even though the model, infrastructure, and operational responsibilities are completely different.

---

## 2. Why self-host at all? API vs. self-hosted

| | Managed API (e.g., Anthropic API) | Self-hosted (vLLM + open-weight model) |
|---|---|---|
| **Who runs the infrastructure** | The provider | You |
| **Scaling** | Automatic, pay-per-token | You provision GPUs for peak load |
| **Cost shape** | Variable, scales with usage ($/token) | Largely fixed (GPU-hours), regardless of usage |
| **Model quality ceiling** | Frontier models (Opus/Sonnet/Haiku tier) | Best available open-weight model |
| **Data residency / control** | Data sent to provider per their policies | Data never leaves your infrastructure |
| **Operational burden** | None (it's an API call) | You: capacity planning, upgrades, GPU failures, scaling, monitoring |
| **Time to first request** | Minutes (get an API key) | Hours–days (provision GPUs, deploy, tune) |

🧑‍💼 **PM view:** Self-hosting trades a *variable, usage-based* cost for a *fixed, capacity-based* cost plus a new ongoing operational responsibility. It's rarely about "self-hosting is cheaper" in the abstract — it's about whether your **volume is high and steady enough** that fixed GPU cost beats per-token API cost, or whether **data residency / compliance** requirements rule out sending data to a third-party API at all.

🧭 **Tech lead view:** This is the same "build vs. buy" tradeoff as any infrastructure decision, with one twist: the *model itself* is also part of what you're "building" — you're not just hosting your own code, you're taking on responsibility for a piece of someone else's (the model provider's) weights, including its quality ceiling and any biases/limitations baked into it.

---

## 3. How vLLM makes self-hosting practical

Running a large model efficiently on a GPU is hard — naive implementations waste enormous amounts of GPU memory and leave most of the GPU idle most of the time. vLLM's core contributions:

### PagedAttention

During generation, each request needs a growing **KV cache** (the model's "memory" of the tokens generated so far). Naively, frameworks reserve a large contiguous memory block per request sized for the *worst case* (max sequence length) — even if most requests are much shorter, wasting GPU memory.

**PagedAttention** manages the KV cache like an OS manages virtual memory: in fixed-size blocks ("pages") that are allocated on demand and can be shared/reused. This dramatically reduces memory waste, which means **more requests fit in GPU memory at once**.

### Continuous batching

Instead of waiting to collect a fixed batch of requests before running them together (and having the whole batch wait for the slowest one), vLLM continuously adds new requests into the running batch and removes finished ones — keeping the GPU busy and improving throughput under real, bursty traffic.

### Other relevant features

- **Quantization** (AWQ, GPTQ, FP8, etc.) — running models at lower numerical precision to fit in less GPU memory / run faster, at some quality cost.
- **Tensor parallelism** — splitting a model too large for one GPU across multiple GPUs.
- **LoRA adapter serving** — serving multiple fine-tuned variants (Module 08) of a base model efficiently, by swapping small adapter weights rather than loading a full separate model per variant.

🧑‍💻 **Engineer view:** None of this changes how you *call* the model — it changes how many concurrent requests a given amount of GPU hardware can serve, and at what latency. The practical effect is: vLLM is usually the difference between "self-hosting is a research project" and "self-hosting can serve real production traffic."

---

## 4. Deploying vLLM: the OpenAI-compatible server

The most common way to use vLLM in an application is its built-in **OpenAI-compatible API server**:

```bash
# Install (requires a CUDA-capable GPU)
pip install vllm

# Serve a model, exposing an OpenAI-compatible API on localhost:8000
vllm serve mistralai/Mistral-7B-Instruct-v0.2
```

Because the server speaks the OpenAI Chat Completions API shape, existing OpenAI-client code mostly works by pointing `base_url` at your vLLM server:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    messages=[{"role": "user", "content": "Summarize this in one sentence: ..."}],
)
print(response.choices[0].message.content)
```

See [`examples/02_openai_compatible_client.py`](examples/02_openai_compatible_client.py) for a runnable version (against any OpenAI-compatible endpoint, including a local vLLM server).

🧑‍💻 **Engineer view:** This OpenAI-compatible shape is *also* how many other self-hosted/local serving tools (Ollama, LM Studio, TGI) expose models — so the patterns here generalize beyond vLLM specifically. The key difference from the Anthropic SDK examples elsewhere in this repo: there is no managed `tool_use`/structured-output guarantee unless the specific model + server version supports it — verify what your chosen model and server version actually support before relying on it.

🧭 **Tech lead view:** "Drop-in OpenAI-API-compatible" is true for the *basic* request/response shape, but production concerns (auth, rate limiting, retries, observability — Module 07) are now **entirely your responsibility**, including in front of your *own* server. You haven't eliminated the "treat the model endpoint as an external dependency" mindset from Module 07 — you've just moved the endpoint onto infrastructure you operate.

---

## 5. A decision framework: API, self-hosted, or both?

Extending the "heaviest, slowest tool last" framing from Module 08:

| Question | If "yes," self-hosting becomes more attractive |
|---|---|
| Is request volume **high and steady** (not bursty)? | Fixed GPU cost amortizes better over consistent load |
| Does data residency / compliance **prohibit** sending data to a third-party API? | Self-hosting may be a hard requirement, not just a cost question |
| Is an **open-weight model good enough** for the task (measured via Module 06 evals)? | The quality ceiling tradeoff is acceptable |
| Do you have (or can justify hiring) **ML infrastructure expertise**? | Someone needs to own GPU capacity, upgrades, and incidents |
| Is the workload **latency-insensitive or can tolerate a fallback**? | Easier to absorb the operational learning curve |

If most answers are "no," a managed API (as used throughout Modules 01-10) remains the right default — it's simply a much smaller operational surface area.

**Hybrid is common in practice:** e.g., self-host an open-weight model for high-volume, well-defined tasks (classification, extraction) where evals show it's sufficient, while using a managed API like the Anthropic API for tasks needing frontier-model reasoning quality, complex tool use, or the lowest operational burden.

🧑‍💼 **PM view:** "Should we self-host?" is rarely a yes/no for an entire product — it's a per-feature question, answered with the same eval discipline (Module 06) used for any model choice: does the cheaper option meet the quality bar for *this* task?

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Out-of-memory errors under load | KV cache / batch size misconfigured for available GPU memory | Tune `--gpu-memory-utilization`, `--max-model-len`, and batch settings; consider quantization |
| Self-hosted cost ends up *higher* than the API | Low/bursty utilization on always-on GPUs | Right-size GPU count to actual sustained load; consider autoscaling or a managed API for overflow |
| Quality regression vs. the model used during prototyping | Switched from a frontier hosted model to a smaller open-weight model without re-evaluating | Re-run the Module 06 eval suite against the self-hosted model before switching production traffic |
| "OpenAI-compatible" client code breaks on tool use / structured output | Feature not supported (or differently implemented) by the specific model + vLLM version | Verify supported features for your exact model/server version before depending on them |
| No visibility into cost or failures | Self-hosted server has none of the observability the managed API gave you "for free" | Apply Module 07's logging/cost-tracking practices to your own server too |
| GPU node failure takes down the feature | No fallback when the self-hosted server is unreachable | Fallback chain to a managed API (Module 07), same as a model-tier fallback |

---

## Tools & Resources

🧑‍💻 **Engineer view — SDKs & libraries**

| Tool / Library | What it's for |
|---|---|
| [vLLM](https://github.com/vllm-project/vllm) / [vLLM docs](https://docs.vllm.ai/) | The inference/serving engine covered in this module — installation, server flags, supported models |
| [Hugging Face Hub](https://huggingface.co/models) | Where the open-weight models vLLM serves (Llama, Mistral, Qwen, etc.) are hosted and versioned |
| [Anthropic API docs](https://docs.anthropic.com/) | Reference for the managed-API side of the comparison in Section 2 |

📚 **Further reading**

- [vLLM documentation](https://docs.vllm.ai/) — server configuration, quantization, and deployment guides
- [Anthropic — Pricing](https://www.anthropic.com/pricing) — usage-based cost figures for the API side of the breakeven analysis

🧑‍💼 **PM view:** If coding the examples isn't practical for your role, see [`exercises/pm_track.md`](exercises/pm_track.md) for a no-code exercise covering the same decisions (API vs. self-hosted, cost/ops tradeoffs, and when a hybrid approach makes sense) using a worked scenario.

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — starting a vLLM server, querying it via an OpenAI-compatible client, and a self-hosted vs. API cost comparison
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions (including a non-coding [PM track](exercises/pm_track.md))

> **Note:** Running vLLM itself requires a CUDA-capable GPU and is out of scope to run inside this repo's examples. The examples focus on the *client-side* patterns and the *cost/decision* reasoning, which don't require a GPU.
