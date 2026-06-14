# Module 13 — PM Track Exercise (No Coding Required)

This exercise walks through the whole module in one pass — spotting a use
case, scoring it, sketching a one-pager, and setting a launch gate — using a
single scenario. It's a good "dry run" before doing this for a real project.

## Scenario

Your finance team manually reviews every expense report before
reimbursement. A reviewer reads the receipt images, checks the amount
against the submitted category and the company's spending policy, and either
approves, asks for more info, or flags it for a manager. About 1,500 reports
come in per month, each taking ~8 minutes to review. Roughly 5% get flagged
for policy violations (e.g., over a per-diem limit, missing a required
approval) — the rest are approved as submitted.

Someone on the leadership team has asked: "Can AI help with this?"

## Your task

1. **Spot the use case (Section 1).** Using the good-signal / red-flag list,
   is this a reasonable candidate for an LLM-based assistant? Identify which
   good signals apply, and name at least one red flag the team should plan
   for.

2. **Match it to the catalog (Section 2).** Which pattern(s) from the
   use-case catalog fit this scenario? (Hint: receipt *images* are involved —
   which earlier module's exercise covered something similar?)

3. **Score it (Section 3).** Give this use case Impact / Feasibility / Risk
   scores (1-5 each, remembering Risk is on an *inverse* scale — 5 = low
   risk). Compute the priority score and assign a tier. Justify your Risk
   score in particular: what's the cost of error if the model approves
   something it shouldn't?

4. **Sketch the one-pager (Section 4).** You don't need to fill in every
   field, but write 1-2 sentences each for: Problem, Proposed approach, and
   Risks & mitigations.

5. **Set a launch gate (Section 6-7).** Propose one business metric and one
   model/quality metric with a target, and say which rollout phase (1-4)
   this should *start* at, given your Risk score from step 3.

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. **Good signals:** high volume (1,500/month), repetitive judgment call,
   existing data (past approved/flagged reports as examples for an eval
   set), and tolerant of error *if* a human still reviews flagged/uncertain
   cases. **Red flag to plan for:** the 5% policy-violation cases are
   exactly the ones where getting it wrong matters most — if the model is
   worse than humans at catching *those*, the easy 95% being faster doesn't
   help much. The team should plan to measure accuracy specifically on the
   flagged subset, not just overall accuracy.

2. This is **multimodal RAG** (Module 02, Exercise 4) — the model needs to
   read receipt images (or extracted text/amounts from them) *and* check
   against a text-based policy document, which is a retrieval problem over
   policy text plus an image-understanding step.

3. Sample scores: **Impact = 4** (1,500 × 8 min ≈ 200 hours/month of review
   time). **Feasibility = 3** (the multimodal + policy-RAG combination is
   more involved than a single prompt, but each piece has a precedent in
   this curriculum). **Risk = 2** (the cost of error is a missed policy
   violation that gets reimbursed incorrectly — real money, though
   individually small and auditable after the fact). Priority score =
   (4+3+2)/3 ≈ 3.0. Since impact ≥ 4 and the score is below 4, this lands as
   a **"Strategic bet"** — worth doing, but needs a phased plan, not a
   one-sprint quick win.

4. **Problem:** Finance spends ~200 hours/month manually reviewing expense
   reports, most of which are eventually approved as-is.
   **Proposed approach:** An assistant reads each report (receipts + policy
   document via RAG) and produces a recommendation — approve, needs info, or
   flag for manager — with a brief explanation.
   **Risks & mitigations:** A false "approve" on a policy violation costs
   real money but is individually small and caught in later audits; a false
   "flag" just adds reviewer work. Given Risk = 2, every recommendation
   should be reviewed by a human in early phases (Module 09's
   human-in-the-loop pattern) rather than auto-approving.

5. **Business metric:** average reviewer minutes per report, target: reduce
   from 8 min to ≤3 min (reviewing the assistant's recommendation, not doing
   the lookup from scratch). **Model/quality metric:** agreement with the
   reviewer's actual decision on the flagged (policy-violation) subset,
   target ≥ 95% — deliberately higher than an overall-accuracy target,
   because that's where the cost of error is concentrated. Given Risk = 2
   (not the lowest), this should start at **Phase 1 (shadow mode)**: run the
   assistant's recommendations alongside real reviews for a few weeks before
   showing anything to reviewers, to measure the flagged-subset agreement
   rate before it affects anyone's workflow.

</details>
