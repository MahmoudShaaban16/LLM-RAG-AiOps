# Exercise 2: Write a one-pager

**No coding required.**

## Scenario

Your company's sales team currently spends ~15 minutes per inbound lead
manually reading the lead's website/LinkedIn and the inquiry form to decide
which of three sales reps (Enterprise, SMB, or Partnerships) should follow
up. There are about 2,000 inbound leads per month. Misrouted leads usually
get caught and reassigned within a day, but cost the original rep wasted
time and slow down the response to the prospect.

## Your task

1. Copy [`../examples/templates/one_pager_template.md`](../examples/templates/one_pager_template.md)
   to a new file (e.g., `my_one_pager.md`) - or just write your answers
   inline in a doc/notes app.
2. Fill in all six sections for this lead-routing use case:
   - **Problem** — quantify today's cost (15 min × 2,000 leads/month at a
     reasonable loaded hourly rate)
   - **Proposed approach** — which row of the [use-case catalog](../README.md#2-use-case-catalog-patterns-and-where-they-fit-in-this-curriculum)
     fits best?
   - **Success metrics** — at least one business metric and one
     model/quality metric, each with a target
   - **Risks & mitigations** — what happens on a misroute? Does this need an
     approval step, or can it run fully automated from day one?
   - **Estimated cost** — use [`02_roi_estimator.py`](../examples/02_roi_estimator.py)-style
     reasoning (you can plug your numbers into that script if you want)
   - **Rollout plan** — which of the four phases would you start at, and why?
3. Compare your one-pager against the sample in
   [`solutions/exercise_02_solution.md`](solutions/exercise_02_solution.md) —
   not to match it exactly, but to check you didn't skip a section.

**Think about:** Which section was hardest to fill in with real numbers?
That's usually the section that needs more discovery before this goes to
engineering.
