# Module 07 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

> **Not coding this module?** [`pm_track.md`](pm_track.md) covers the same
> decisions (fallback strategy, what to log for cost attribution, and how to
> respond to quality drift) as a written exercise — no code required.

## Exercise 1: Add a cost budget alert

**File:** [`exercise_01_cost_alert.py`](exercise_01_cost_alert.py)

Building on [`examples/02_request_logging_and_cost_tracking.py`](../examples/02_request_logging_and_cost_tracking.py):

1. Add a `BUDGET_USD_PER_USER` constant (e.g., `0.01`).
2. After logging each request, check the *running total cost* for that
   `user_id`. If it exceeds the budget, print a warning (e.g.,
   `"BUDGET ALERT: user_3 has exceeded $0.01"`).
3. Run a simulated batch of requests (at least 5, across 2-3 users) so that
   at least one user crosses the budget.

**Think about:** In a real system, what should happen when a user crosses
a budget threshold — block further requests? Downgrade to a cheaper model?
Just alert a human? Does the answer differ for an internal tool vs. a
customer-facing feature?

---

## Exercise 2: Make the cached prefix actually stable

**File:** [`exercise_02_cache_stability.py`](exercise_02_cache_stability.py)

The module README notes that prompt caching requires the cached prefix to
match *exactly* between requests — even a small change (like an embedded
timestamp) breaks the cache.

1. Write a version of the system prompt from
   [`examples/01_prompt_caching.py`](../examples/01_prompt_caching.py) that
   has a **bug**: it includes `datetime.now()` directly in the cached text
   block.
2. Make two calls with this buggy version and inspect
   `cache_creation_input_tokens` / `cache_read_input_tokens` on both —
   confirm the cache is never reused (every call looks like a fresh write).
3. Fix the bug by moving the dynamic content (the timestamp) *outside* the
   cached block — e.g., into a separate, non-cached system block or into the
   user message — and re-run to confirm caching now works across calls.

---

## Exercise 3: Extend the fallback chain with a circuit breaker

**File:** [`exercise_03_circuit_breaker.py`](exercise_03_circuit_breaker.py)

[`examples/03_fallback_and_retry.py`](../examples/03_fallback_and_retry.py)
retries each model independently on every call. In a real outage, this means
every request pays the full retry cost (and delay) for the primary model
before falling back — for the entire duration of the outage.

1. Add a simple in-memory "circuit breaker": track consecutive failures for
   the primary model (`claude-sonnet-4-6`).
2. If the primary model has failed `N` times in a row (e.g., `N = 3`), skip
   straight to the fallback model for subsequent calls — don't retry the
   primary — for a cooldown period (e.g., the next 5 calls), then try the
   primary again.
3. Simulate this with a function that can be made to "fail" on demand (you
   don't need to actually trigger real API errors — a flag that raises an
   exception is fine), and print which model serves each of ~10 simulated
   requests.

**Think about:** Why does skipping retries during a known outage matter for
both latency (user experience) and cost (you're still being billed for
failed attempts in some failure modes)?
