# Module 11 — Exercises

These exercises extend [`examples/03_cost_comparison.py`](../examples/03_cost_comparison.py)
and the decision framework from the module README. None require a GPU or an
API key.

> **Not coding this module?** [`pm_track.md`](pm_track.md) covers the same
> decisions (API vs. self-hosted, breakeven volume, and the decision
> framework) as a written exercise — no code required.

## Exercise 1: Model the breakeven for your own workload

**File:** [`exercise_01_breakeven.py`](exercise_01_breakeven.py)

`examples/03_cost_comparison.py` hardcodes a request shape (500 input / 200
output tokens) and a single GPU price ($2.00/hr).

1. Parameterize `breakeven_requests_per_month` as a function of
   `avg_input_tokens`, `avg_output_tokens`, `gpu_cost_per_hour`, and the API
   pricing.
2. Compute the breakeven for three scenarios: a small classification task
   (50 input / 10 output tokens), a RAG-based support assistant (1500 input
   / 300 output tokens, like Module 10's capstone), and a long-document
   summarizer (8000 input / 500 output tokens).
3. Print all three breakeven volumes.

**Think about:** Which of these scenarios is most likely to exceed the
breakeven volume in practice? Does that match your intuition about which
workloads get self-hosted in the real world?

---

## Exercise 2: Apply the decision framework

**File:** [`exercise_02_decision_framework.py`](exercise_02_decision_framework.py)

Using the decision framework table from the module README:

1. For each of the 4 scenarios below, answer each of the 5 framework
   questions (yes/no) and print a recommendation ("favor self-hosting",
   "favor managed API", or "hybrid - investigate further"):
   - A startup prototyping a new AI feature, uncertain of demand
   - A healthcare company that cannot send patient data to third-party APIs
   - A high-volume content-moderation classifier running on every user post
   - A coding assistant that needs the strongest available reasoning model
2. Print your reasoning for each.

**Think about:** Is there a scenario where the "right" answer might change
significantly as the product matures (e.g., prototype -> high volume)? How
would you revisit this decision later without it being a rewrite?

---

## Exercise 3: Eval-gate a self-hosting migration

**File:** [`exercise_03_eval_gate.py`](exercise_03_eval_gate.py)

A team wants to move a high-volume ticket-categorization task (similar to
Module 10's `submit_triage` `category` field) from the Anthropic API to a
self-hosted open-weight model via vLLM, because the breakeven analysis from
Exercise 1 favors it.

1. Using the LLM-as-judge / regression-testing pattern from Module 06,
   sketch (in comments or pseudocode - no API key needed to run this) the
   eval gate this migration should pass *before* shipping: what would you
   compare, and what would count as a regression?
2. Write a small `should_migrate(old_scores: list[float], new_scores: list[float], threshold: float) -> bool`
   function that returns `True` only if the new (self-hosted) model's scores
   are not meaningfully worse than the old model's, using `threshold` as the
   maximum acceptable average score drop.
3. Test it with a few example score lists.

**Bonus:** The module README notes that self-hosting adds an operational
failure mode (GPU node down = outage) that the API didn't have. Even if the
eval gate passes, what else would you want in place before cutting over
production traffic?
