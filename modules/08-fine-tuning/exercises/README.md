# Module 08 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

> **Not coding this module?** [`pm_track.md`](pm_track.md) covers the same
> decisions (when fine-tuning is justified, data readiness, and before/after
> evaluation) as a written exercise — no code required.

## Exercise 1: Validate and format a training dataset

**File:** [`exercise_01_format_dataset.py`](exercise_01_format_dataset.py)

You're given a list of raw input/output examples for a "release notes
summarizer" — a model that should turn raw changelog entries into a single
customer-facing sentence, in a consistent style.

1. Extend the validation from `examples/01_prepare_training_data.py` to also
   check:
   - No duplicate `input` values (duplicates can over-weight an example)
   - `output` is no longer than 200 characters (this dataset's style
     constraint — outputs should be one short sentence)
2. Run validation against the provided `RAW_EXAMPLES` and report which
   examples are valid vs. which fail, and why.
3. Write the valid examples to JSONL in the `messages` format, using a
   system prompt you write that describes the desired style.

**Think about:** If 4 out of 10 examples fail validation, is the dataset
"80% ready," or does that reveal a bigger problem with how the data was
collected?

---

## Exercise 2: Apply the decision framework

**File:** [`exercise_02_decision_framework.py`](exercise_02_decision_framework.py)

For each of the 4 scenarios in the starter file, decide whether the right
tool is **prompting**, **RAG**, **tool use / structured output**, or
**fine-tuning** — and write 2-3 sentences justifying your choice using the
framework from Section 1 of the module README.

1. Fill in `recommendation` and `justification` for each scenario.
2. For any scenario where you chose "fine-tuning," explain what you'd want
   to try *first* before committing to it, and what evidence would tell you
   prompting/RAG wasn't enough.

**Think about:** Is there a scenario where your honest answer is "I'd need
to see eval results before I could say"? That's often the *correct* answer
— write it down as such rather than guessing.

---

## Exercise 3: Design a before/after evaluation plan

**File:** [`exercise_03_eval_plan.py`](exercise_03_eval_plan.py)

A team wants to fine-tune a model to always respond to customer emails in a
specific brand voice, and has asked you (acting as tech lead) to define how
they'll know if it worked.

1. Using the pattern in `examples/02_evaluate_finetuned_vs_base.py` and
   Module 06's evaluation harness, sketch (as Python data structures — no
   API calls needed) an eval set of at least 4 cases that would catch:
   - Whether the new model matches the target brand voice
   - Whether the new model *regressed* on something the base model used to
     do well (e.g., answering an off-topic question safely)
2. Write the `criteria` for each case, the way Module 06's `EVAL_DATASET`
   does.
3. Describe (in a comment) what score difference between base and
   fine-tuned would be enough to justify shipping the fine-tuned model, and
   what result would make you NOT ship it even if the target-voice score
   improved.
