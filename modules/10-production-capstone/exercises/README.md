# Module 10 — Exercises

These exercises extend [`examples/capstone_app/main.py`](../examples/capstone_app/main.py).
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

> **Not coding this module?** [`pm_track.md`](pm_track.md) covers the same
> decisions (what belongs in a v1 capstone, what to defer, and how to review
> an end-to-end AI feature) as a written exercise — no code required.

## Exercise 1: Add a new tool

**File:** [`exercise_01_add_tool.py`](exercise_01_add_tool.py)

Add a `check_account_status` tool that returns whether an account is
"active", "suspended", or "pending_verification" for a given email address
(mock the data, like `check_order_status` does for orders).

1. Define the tool schema.
2. Implement the mock function.
3. Add it to the `tools=[...]` list and to the tool-dispatch logic in
   `triage_ticket`.
4. Update the system prompt so the model knows when to use it.
5. Add a sample ticket that should trigger this tool (e.g., "I can't log in,
   is my account suspended? My email is jane@example.com").

**Think about:** How would you prevent the model from calling this tool with
an email address it found in an *untrusted* part of the input (e.g., an
attacker-controlled ticket claiming to be a different user)?

---

## Exercise 2: Build an eval set for the triage assistant

**File:** [`exercise_02_eval_set.py`](exercise_02_eval_set.py)

Using the LLM-as-judge pattern from
[Module 06](../../06-llm-evaluation-and-testing/examples/02_llm_as_judge.py):

1. Write 5 sample tickets covering different categories (account, billing,
   order, technical, other) with an *expected* category and urgency for each.
2. Run each through `triage_ticket`.
3. Check whether the model's `category` and `urgency` match your expectations,
   and print a pass/fail summary.

**Think about:** What should happen when the model's `needs_human_review` is
`true` but your expected urgency is `low`? Is that a failure, or expected
caution?

---

## Exercise 3: Add a guardrail for the suggested response

**File:** [`exercise_03_response_guardrail.py`](exercise_03_response_guardrail.py)

Add a guardrail function `validate_suggested_response(triage_result: dict) -> dict`
that runs *after* `triage_ticket` returns and:

1. Checks the `suggested_response` text doesn't contain anything that looks
   like a system prompt leak (e.g., contains the literal words "system
   prompt" or "<untrusted_input>").
2. If it does, set `needs_human_review = True` and append a note explaining
   why.
3. Run this guardrail on the result for the third sample ticket (the one
   with the prompt injection attempt) and confirm it flags correctly.

**Bonus:** What's the difference between this *output* guardrail and the
*input* guardrail (the `<untrusted_input>` wrapping)? Why might you want both?
