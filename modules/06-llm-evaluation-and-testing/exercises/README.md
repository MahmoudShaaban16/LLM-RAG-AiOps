# Module 06 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

## Exercise 1: Extend the evaluation dataset

**File:** [`exercise_01_extend_dataset.py`](exercise_01_extend_dataset.py)

The eval dataset in [`examples/01_eval_dataset.py`](../examples/01_eval_dataset.py)
covers refund-policy questions for "Acme Cloud" support.

1. Add **3 new eval cases** to `EVAL_DATASET`, including at least one of each:
   - A typical case (similar to existing ones, but a different scenario)
   - An edge case (e.g., a question right at the boundary of the refund window)
   - An adversarial/off-policy case (e.g., asking the assistant to ignore its
     instructions, or to make a refund exception "just this once")
2. For each new case, write 2-4 criteria describing what a good response
   looks like.
3. Run all cases through the model and print the outputs.

**Think about:** Why might the adversarial case be the most valuable one to
add? What would happen in production if this case wasn't covered?

---

## Exercise 2: Build a judge for a different task

**File:** [`exercise_02_judge_for_summaries.py`](exercise_02_judge_for_summaries.py)

The judge in [`examples/02_llm_as_judge.py`](../examples/02_llm_as_judge.py)
scores support responses against criteria. This exercise asks you to build a
judge for a **summarization** task instead.

1. Define a small eval dataset (2-3 cases) where each input is a short
   paragraph and the criteria describe what a good summary should do
   (e.g., "captures the main point in one sentence", "does not exceed 25
   words", "does not include opinions not present in the source").
2. Generate a summary for each input using `client.messages.create`.
3. Reuse (or adapt) the `JUDGE_SCHEMA` and `judge_response` function from
   `02_llm_as_judge.py` to score each summary against its criteria.
4. Print the score and reasoning for each case.

**Think about:** Does the same 1-5 rubric description make sense for
summarization as it did for support responses? Would you change the rubric's
wording for this task?

---

## Exercise 3: Run a regression test with a real prompt change

**File:** [`exercise_03_your_regression_test.py`](exercise_03_your_regression_test.py)

Using [`examples/03_prompt_regression_test.py`](../examples/03_prompt_regression_test.py)
as a template:

1. Write a `PROMPT_OLD` and a `PROMPT_NEW` where `PROMPT_NEW` makes a
   **deliberate tradeoff** — e.g., a much shorter system prompt that should
   reduce output tokens (and therefore cost) but might reduce quality.
2. Run both against the eval dataset, score with the judge, and print the
   comparison table (score delta + token delta per case).
3. Write 2-3 sentences: based on the table, would you ship `PROMPT_NEW`?
   What additional eval cases (if any) would make you more confident?

**Bonus:** Run the same regression test twice for `PROMPT_OLD` only (no
changes). Are the judge scores identical both times? What does this tell you
about how many eval cases you'd need before trusting a small score
difference as a real signal vs. noise?
