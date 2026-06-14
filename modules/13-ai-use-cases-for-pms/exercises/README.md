# Module 13 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

> **New to this module / not coding at all?** [`pm_track.md`](pm_track.md)
> walks through the whole scope-a-project workflow (spotting the use case,
> scoring it, writing the one-pager, and setting a launch gate) as a single
> written exercise — no code required. Exercises 1-3 below cover the same
> ground with runnable scripts and a one-pager template.

## Exercise 1: Score and prioritize a use-case backlog

**File:** [`exercise_01_score_use_cases.py`](exercise_01_score_use_cases.py)

1. Implement `priority_score` and `tier` following the README's Section 3
   framework.
2. Run the script over the provided backlog and review the ranked output.

**Think about:** Pick the two highest-ranked items - are they actually the
two you'd pick if this were your real backlog? If not, what's the scoring
framework missing for your context?

---

## Exercise 2: Write a one-pager

**File:** [`exercise_02_one_pager.md`](exercise_02_one_pager.md)

A no-code exercise: given a lead-routing scenario, fill in all six sections
of the [one-pager template](../examples/templates/one_pager_template.md),
then compare against the sample solution.

**Think about:** Which section was hardest to fill in with real numbers?
That's usually the section that needs more discovery before this goes to
engineering.

---

## Exercise 3: Launch readiness check

**File:** [`exercise_03_launch_readiness.py`](exercise_03_launch_readiness.py)

1. Implement `check_readiness` and `overall_decision` to turn a one-pager's
   success-metric targets into a go/no-go gate.
2. Run the script against both provided shadow-mode result sets.

**Think about:** Results B passes 2 of 3 metrics but is still "NO-GO" -
why is an all-or-nothing gate the right call here, and when (if ever) would
you make an exception?
