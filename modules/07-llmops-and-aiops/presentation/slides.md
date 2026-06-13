---
marp: true
title: LLMOps & AIOps
paginate: true
---

# LLMOps & AIOps
### Module 07

Running LLM features reliably, observably, and cost-effectively

---

## Agenda

1. Deploying LLM applications
2. Observability: logging, tracing, cost tracking
3. Caching strategies
4. Handling model deprecations & updates
5. Monitoring for quality drift
6. Common failure modes & mitigations

---

## 1. Deploying LLM Applications

```
request -> gateway (auth/rate limit) -> your service
              -> Anthropic API (retries + fallback model)
              -> response (+ logging, cost tracking)
```

- The model API is an external dependency — treat it like one
- **Retries with backoff** for `429`/`5xx`/timeouts
- **Model fallback chain** (e.g., Sonnet -> Haiku) beats failing outright

**PM takeaway:** "the LLM API is down" should not mean "our feature is down"

---

## 2. Observability

Log on every call:

- Prompt + response (with PII-aware retention)
- `usage.input_tokens` / `usage.output_tokens`
- `cache_creation_input_tokens` / `cache_read_input_tokens`
- Model + prompt version
- Latency
- Estimated cost (tokens x pricing)

> Cost-per-user/feature should be a query, not a guess

---

## 3. Caching Strategies

**Prompt caching** (`cache_control: {"type": "ephemeral"}`)

```python
system=[{
    "type": "text",
    "text": LONG_SYSTEM_PROMPT,
    "cache_control": {"type": "ephemeral"},
}]
```

- First call: pays to write cache (`cache_creation_input_tokens`)
- Later calls: discounted `cache_read_input_tokens`
- Put stable content first, variable content after

**Response caching:** hash repeat requests, skip the API call entirely

---

## 4. Model Deprecations & Updates

```
Old: hardcode "claude-sonnet-4-6" everywhere
     -> deprecation notice -> frantic find-and-replace

Better: MODEL = config["model_id"]  (one place)
        -> deprecation notice -> update config, run eval suite, roll out
```

- New model versions can change behavior even at the same tier
- Re-run the Module 06 eval suite before switching production traffic

---

## 5. Monitoring for Quality Drift

Drift happens even with **no code changes**:

- Provider updates the underlying model
- Real-world input distribution shifts
- Upstream data (retrieved docs, tool outputs) changes

**Mitigation:**
- Run the eval suite on a schedule (not just on PRs)
- Sample production traffic for LLM-as-judge scoring
- Track score trend + leading indicators (length, refusals, latency)

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Outage = feature down | Retries + fallback model chain |
| Cost spikes | Per-request/user cost logging + alerts |
| "It used to work" | Scheduled eval runs + drift monitoring |
| Caching not saving cost | Keep cached prefix identical between calls |
| Breaks after deprecation | Centralize model ID in config |
| Retry storms | Backoff + jitter + max attempts, only on retryable errors |

---

## Hands-on

- `examples/01_prompt_caching.py`
- `examples/02_request_logging_and_cost_tracking.py`
- `examples/03_fallback_and_retry.py`
- `exercises/` — practice problems + solutions

---

# Questions?

Next module: **Fine-Tuning** ->
