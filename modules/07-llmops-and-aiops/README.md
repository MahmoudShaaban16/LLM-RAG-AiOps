# Module 07 — LLMOps & AIOps

> **Goal:** Take an LLM-powered feature that works in development and run it reliably, observably, and cost-effectively in production — and keep it working as models, prompts, and traffic change over time.

## Contents

- [1. Deploying LLM applications](#1-deploying-llm-applications)
- [2. Observability: logging, tracing, and cost tracking](#2-observability-logging-tracing-and-cost-tracking)
- [3. Caching strategies](#3-caching-strategies)
- [4. Handling model deprecations and updates](#4-handling-model-deprecations-and-updates)
- [5. Monitoring for quality drift](#5-monitoring-for-quality-drift)
- [6. Common failure modes](#6-common-failure-modes)
- [Tools & Resources](#tools--resources)
- [Hands-on](#hands-on)

---

## 1. Deploying LLM applications

An LLM API call is an **external network dependency** with its own latency, rate limits, and failure modes — your deployment architecture needs to treat it that way, the same as any third-party API.

```
client request
     │
     ▼
your API gateway ──▶ rate limiting / auth / request validation
     │
     ▼
your service ──▶ Anthropic API (with retries + fallback model)
     │
     ▼
response (+ logging, cost tracking)
```

Key building blocks:

- **API gateway** — your own entry point that handles auth, request validation, and rate limiting *before* a request reaches the model call. This protects both your budget and the upstream API's rate limits.
- **Rate limiting** — both directions matter: limit how fast *your users* can call your feature (cost control, abuse prevention), and respect the *provider's* rate limits (requests/minute, tokens/minute) to avoid `429` errors under load.
- **Retries with backoff** — transient errors (`429` rate limits, `5xx` server errors, timeouts) are common and often resolve on retry. A retry should use exponential backoff with jitter, and a sane retry limit — see [`examples/03_fallback_and_retry.py`](examples/03_fallback_and_retry.py).
- **Model fallback chains** — if your primary model is unavailable or overloaded, fall back to a different model tier (e.g., Sonnet → Haiku) rather than failing the request outright. The fallback response may be lower quality, but "degraded" usually beats "down."

🧑‍💼 **PM view:** "The LLM API is down" should not mean "our feature is down." Even a basic fallback (a cached response, a simpler model, or a friendly "try again shortly" message) is a product decision worth making *before* an outage, not during one.

🧑‍💻 **Engineer view:** Wrap every model call in a single function/module so retry logic, fallback chains, logging, and cost tracking live in one place — not duplicated at every call site. See [`examples/03_fallback_and_retry.py`](examples/03_fallback_and_retry.py) for a minimal retry + fallback wrapper using only the standard library.

🧭 **Tech lead view:** Decide upfront which failures are *retryable* (rate limits, timeouts, 5xx) vs. which should fail fast (4xx validation errors, content policy rejections — retrying these wastes time and money without changing the outcome).

---

## 2. Observability: logging, tracing, and cost tracking

Traditional application observability (logs, metrics, traces) still applies — but LLM calls add dimensions that are easy to miss if you only log HTTP status codes and latency:

- **Prompts and responses** — what was actually sent to the model (system prompt, user message, any retrieved context) and what came back. This is essential for debugging "why did it say that" after the fact.
- **Token usage** — `usage.input_tokens`, `usage.output_tokens`, and (with prompt caching) `cache_creation_input_tokens` / `cache_read_input_tokens` from every response.
- **Model and prompt version** — which model ID and which version of your prompt produced this response. Without this, you can't correlate a quality change with its cause.
- **Cost** — derived from token usage × the pricing table for the model used. Track this per request, and aggregate per user/feature/team to turn "AI spend" from a single opaque number into something actionable.
- **Latency** — wall-clock time for the model call, separate from your application's total request time, so you can tell "the model is slow" apart from "our code is slow."

```python
# Minimal shape of what to log per LLM call
{
    "timestamp": "...",
    "model": "claude-sonnet-4-6",
    "feature": "support_assistant",
    "user_id": "...",
    "input_tokens": 512,
    "output_tokens": 128,
    "cache_read_input_tokens": 400,
    "latency_ms": 842,
    "estimated_cost_usd": 0.0034,
}
```

🧑‍💼 **PM view:** "How much does our AI feature cost per active user, per month?" should be a query against logs, not a guess. Set this up *before* the feature has heavy traffic — retrofitting cost attribution after the fact is much harder.

🧑‍💻 **Engineer view:** A simple wrapper around `client.messages.create` that logs metadata on every call gets you most of the value with minimal effort. See [`examples/02_request_logging_and_cost_tracking.py`](examples/02_request_logging_and_cost_tracking.py). For multi-step agents (Module 03/04), this becomes **tracing** — each step in a chain of calls needs a shared identifier (a trace/run ID) so you can reconstruct the whole sequence.

🧭 **Tech lead view:** Be deliberate about logging *prompts and responses* — they may contain user PII or sensitive business data. Decide on retention, redaction, and access-control policy for this log data with the same rigor as any other data store containing user content.

---

## 3. Caching strategies

Two distinct kinds of caching apply to LLM applications, and they solve different problems:

### Prompt caching (Anthropic's `cache_control`)

When a large, *unchanging* block of content (a long system prompt, a big document, a tool definition set) is reused across many requests, you can mark it with `cache_control: {"type": "ephemeral"}` so the API can reuse its processed representation on subsequent calls — reducing latency and cost for the cached portion.

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,          # e.g., a large policy doc
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": user_question}],
)

print(response.usage.cache_creation_input_tokens)  # tokens written to cache (first call)
print(response.usage.cache_read_input_tokens)       # tokens read from cache (later calls)
```

- The **first** request that includes a given cached block pays a small premium to *write* the cache (`cache_creation_input_tokens`).
- **Subsequent** requests within the cache's lifetime that reuse the identical prefix get a large discount on those tokens, reported as `cache_read_input_tokens`.
- Caches are short-lived ("ephemeral") — they exist to speed up bursts of related requests (e.g., many users asking questions against the same large document), not as permanent storage.

*(The exact cache lifetime, discount percentage, and minimum cacheable size are subject to change — always check the current [Anthropic API docs](https://docs.anthropic.com/) for up-to-date numbers. The shapes shown here — a content block with `"type": "text"` and a `"cache_control"` key, and the two `usage` fields — reflect the documented API pattern.)*

### Response caching

A simpler, application-level cache: if the *same* request (same prompt, same inputs) is likely to recur — e.g., an FAQ-style feature, or a batch job reprocessing similar inputs — store the model's response keyed by a hash of the input, and skip the API call entirely on a cache hit.

- Works best for **deterministic-enough, repeatable** queries (low temperature, stable prompts).
- Needs an explicit invalidation strategy: if the prompt or underlying data changes, cached responses become stale.

🧑‍💼 **PM view:** Prompt caching is close to "free" latency/cost wins for features with a large shared context (e.g., "answer questions about this 50-page document") — it's worth checking whether your system prompts/context are structured to take advantage of it. Response caching is a bigger design decision: it trades freshness for cost, which may or may not be acceptable depending on the feature.

🧑‍💻 **Engineer view:** To benefit from prompt caching, structure your system prompt so the **large, stable** content comes first (and is marked with `cache_control`), with request-specific content after it — cache hits require the cached prefix to match exactly. See [`examples/01_prompt_caching.py`](examples/01_prompt_caching.py).

🧭 **Tech lead view:** Prompt caching is most valuable for high-volume features that repeatedly send the same large context (RAG system prompts, long tool definitions, codebase context for coding agents). Measure `cache_read_input_tokens` in production to confirm you're actually getting cache hits — a subtle change to the cached prefix (even whitespace) can silently break caching.

---

## 4. Handling model deprecations and updates

Model providers periodically deprecate older model versions and release new ones. Because your application likely references a **model ID string** (e.g., `"claude-sonnet-4-6"`), this is a dependency that *will* change over time, on a timeline you don't control.

What this means in practice:

- **Deprecation notices** give a window (often months) before an old model ID stops working — track these the same way you'd track a deprecated library version.
- **New model versions can change behavior** even at the same "tier" — a prompt tuned against one model version may need re-tuning after an upgrade. This is exactly what your eval suite (Module 06) is for: run it against the new model before switching production traffic.
- **Pin model versions explicitly** in config (not "latest") so upgrades are a deliberate, tested change — not something that happens silently when a provider rolls out a default.

```
Old flow: hardcode "claude-sonnet-4-6" everywhere
          → deprecation notice → frantic find-and-replace

Better:   MODEL = config["model_id"]  (one place)
          → deprecation notice → update config, run eval suite, roll out
```

🧑‍💼 **PM view:** Budget time for periodic "model migration" work as a normal maintenance cost of an LLM feature — similar to dependency upgrades in traditional software, but with a quality-regression risk that needs eval coverage, not just "does it still compile."

🧭 **Tech lead view:** Treat the model ID as a versioned, configuration-managed dependency. Before switching, run the Module 06 eval/regression suite against the new model with your existing prompts — a "drop-in" model swap is rarely *quality*-neutral even when it's *API*-compatible.

---

## 5. Monitoring for quality drift

Even with no changes on your side, LLM feature quality can **drift**:

- The provider updates the underlying model (even a "minor" update can shift behavior on edge cases).
- The distribution of real user inputs shifts (new product features, new user segments, seasonal patterns).
- Upstream data your prompts depend on (retrieved documents, tool outputs) changes.

Detecting drift requires monitoring *outputs*, not just *uptime*:

- **Run your eval suite on a schedule** (e.g., nightly/weekly), not just on PRs — this catches drift from provider-side model updates that your code didn't trigger.
- **Sample production traffic for judge-based scoring** — periodically run LLM-as-judge (Module 06) on a random sample of real production interactions, and track the score trend over time.
- **Track leading indicators** alongside quality scores: response length distribution, refusal rate, latency, and user-facing signals (thumbs down, follow-up "that's not right" messages, escalation rate).

🧑‍💼 **PM view:** "It used to work fine" is the most common way LLM quality issues are first reported — and the hardest to debug without historical data. Quality monitoring turns "it feels worse lately" into "the judge score dropped 8% starting on this date, correlating with this model update."

🧭 **Tech lead view:** Quality drift detection is the production analog of the regression testing in Module 06 — same scoring mechanism (eval dataset + LLM-as-judge), but run continuously against live data rather than only on prompt changes.

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Feature goes down when the model API has an outage | No retry/fallback logic | Add retries with backoff + a model fallback chain (Section 1) |
| Costs spike unexpectedly | No per-request/per-user cost tracking | Log token usage and cost on every call; set budget alerts |
| "It used to work" with no clear cause | No quality monitoring over time | Run eval suite on a schedule; sample production traffic for judge scoring (Section 5) |
| Prompt caching isn't reducing cost | Cached prefix isn't identical between requests (e.g., includes a timestamp) | Keep the cached block static; put variable content after it |
| App breaks after a model deprecation | Model ID hardcoded everywhere, no deprecation tracking | Centralize model ID in config; track provider deprecation notices |
| Debugging a bad response is guesswork | Prompts/responses not logged | Log full prompt + response (with PII-aware retention policy) per request |
| Retries make a bad situation worse (retry storms) | Retrying non-retryable errors, or no backoff | Only retry `429`/`5xx`/timeouts, with exponential backoff + jitter and a max attempt count |

---

## Tools & Resources

🧑‍💻 **Engineer view — SDKs & libraries**

| Tool / Library | What it's for |
|---|---|
| [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) | `client.messages.create` — exposes `usage`, prompt caching (`cache_control`), and the fields needed for cost/latency tracking |
| [LangSmith](https://docs.smith.langchain.com/) | Tracing, logging, and cost/latency dashboards for multi-step LLM applications |
| [Helicone](https://docs.helicone.ai/) | Drop-in observability proxy for logging prompts, responses, token usage, and cost |
| [OpenTelemetry](https://opentelemetry.io/docs/) | Vendor-neutral tracing standard — useful for correlating LLM call traces with the rest of your application's observability stack |

📚 **Further reading**

- [Anthropic — Prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — official reference for `cache_control`, cache lifetimes, and the `usage` fields shown in Section 3
- [Anthropic — Pricing](https://www.anthropic.com/pricing) — current model pricing for cost-tracking calculations
- [Anthropic — Model deprecations](https://docs.anthropic.com/en/docs/about-claude/model-deprecations) — official deprecation timeline and policy referenced in Section 4

🧑‍💼 **PM view:** If coding the examples isn't practical for your role, see [`exercises/pm_track.md`](exercises/pm_track.md) for a no-code exercise covering the same decisions (fallback strategy, what to log for cost attribution, and how to respond to quality drift) using a worked scenario.

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — runnable scripts demonstrating prompt caching, logging/cost tracking, and retry/fallback
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions (including a non-coding [PM track](exercises/pm_track.md))
