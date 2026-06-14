# AI Feature One-Pager: <name of the use case>

> Fill in each section in plain language. If you can't fill in a section,
> that's a signal the use case needs more discovery before scoping
> (module README Section 4).

## 1. Problem

- What's the current process, step by step?
- What does it cost today (time per task × volume, or $ directly)?
- Who feels this pain, and how often?

## 2. Proposed approach

- Which pattern from the [use-case catalog](../../README.md#2-use-case-catalog-patterns-and-where-they-fit-in-this-curriculum)
  does this match? (e.g., "RAG over our help docs", "agent with order-lookup
  and refund tools")
- What does the model see as input, and produce as output?

## 3. Success metrics

| Type | Metric | Target |
|---|---|---|
| Business | | |
| Model/quality | | |
| Cost & ops | | |

## 4. Risks & mitigations

- What happens when the model is wrong? Who sees/reviews the output?
- Which actions (if any) need approval before they execute? (allow / approve / block)
- Any prompt-injection exposure (untrusted user content, web pages, documents)?

## 5. Estimated cost

- Expected volume per month: ____
- Estimated cost per request: ____ (see [`02_roi_estimator.py`](../02_roi_estimator.py))
- One-time implementation cost (engineering estimate): ____
- Estimated monthly savings / value: ____

## 6. Rollout plan

- [ ] Phase 1 - Shadow mode (log only, no user-facing change)
- [ ] Phase 2 - Human-in-the-loop (model drafts, human approves/sends)
- [ ] Phase 3 - Auto for low-risk actions, approval queue for high-risk
- [ ] Phase 4 - Full automation (only for actions proven reliable in 1-3)

What metric (from Section 3) decides moving from one phase to the next?
