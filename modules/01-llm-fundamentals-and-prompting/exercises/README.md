# Module 01 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

> **Not coding this module?** [`pm_track.md`](pm_track.md) covers the same
> decisions (token/cost estimation, model selection, and prompt design) as a
> written exercise — no code required.

## Exercise 1: Estimate and verify token usage

**File:** [`exercise_01_token_budget.py`](exercise_01_token_budget.py)

You're building a feature that sends a system prompt plus a user-provided
paragraph to Claude on every request, expecting a short reply.

1. Write code that counts the tokens in the system prompt + a sample user
   paragraph *before* sending the request, using `count_tokens`.
2. Make the actual API call and print the real `usage.input_tokens` and
   `usage.output_tokens`.
3. Given the pricing table in the module README, calculate the estimated
   cost in USD for this single request using `claude-sonnet-4-6`.

**Think about:** If this feature gets 10,000 requests/day, what's the
monthly cost? Would a different model tier change your answer significantly?

---

## Exercise 2: Fix a vague prompt

**File:** [`exercise_02_fix_prompt.py`](exercise_02_fix_prompt.py)

The starter code sends this prompt:

```python
"Tell me about our product."
```

and gets back an inconsistent, rambling response of varying length and tone.

1. Rewrite the prompt (and/or add a system prompt) so the model consistently
   returns a response that:
   - Is exactly 3 bullet points
   - Is written for a prospective enterprise customer (formal tone)
   - Does not make up product details — if it doesn't know something, it
     should say so explicitly

2. Run your version 3 times and confirm the output format is consistent
   each time.

---

## Exercise 3: Build a structured classifier

**File:** [`exercise_03_classifier.py`](exercise_03_classifier.py)

Using the tool-based structured output pattern from
[`examples/04_structured_output.py`](../examples/04_structured_output.py):

1. Define a tool schema that classifies a piece of user feedback into:
   - `sentiment`: `"positive" | "neutral" | "negative"`
   - `topics`: an array of strings from a fixed set (e.g., `"pricing"`,
     `"performance"`, `"ui"`, `"support"`, `"reliability"`)
   - `requires_followup`: boolean

2. Test it against the 3 sample feedback strings provided in the starter
   file and print the structured result for each.

3. **Bonus:** What happens if you remove `tool_choice` (letting the model
   decide whether to use the tool)? Try it and explain the difference.
