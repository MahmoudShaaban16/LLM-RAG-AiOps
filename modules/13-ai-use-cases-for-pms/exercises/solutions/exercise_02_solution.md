# AI Feature One-Pager: Inbound Lead Routing

## 1. Problem

- Today, a coordinator spends ~15 minutes per inbound lead reading the
  website/LinkedIn and inquiry form to decide whether to route the lead to
  Enterprise, SMB, or Partnerships.
- At ~2,000 leads/month and a loaded rate of ~$40/hour, that's
  2,000 × (15/60) × $40 = **$20,000/month** of coordinator time.
- Misroutes are usually caught within a day, but the original rep loses
  time and the prospect's response is slower - a secondary, harder-to-quantify cost.

## 2. Proposed approach

- Matches the "Classify inbound leads by intent" pattern (catalog row:
  single prompt, structured output - Module 01), reading the inquiry form
  text plus a short scrape/summary of the company's website if available.
- Input: lead form text (+ optional company description). Output: a
  structured `{"team": "enterprise" | "smb" | "partnerships", "confidence": 0-1}`.

## 3. Success metrics

| Type | Metric | Target |
|---|---|---|
| Business | Coordinator time spent on routing | Reduce from 15 min/lead to <2 min/lead (spot-check only) |
| Model/quality | Routing accuracy vs. a labeled eval set of past leads | >= 90% agreement with the coordinator's historical decision |
| Cost & ops | Cost per lead | < $0.02/lead |

## 4. Risks & mitigations

- A misroute costs at most ~1 day of delay and some rep time - low,
  reversible cost of error.
- Because the cost of error is low and reversible, this can run
  **auto-route with a confidence threshold**: below the threshold, fall back
  to the coordinator (human-in-the-loop); above it, route automatically.
- No financial or irreversible action is taken - no approval queue needed
  (Module 09's allow/approve/block: this is "allow", with a confidence-based
  fallback rather than a blanket human review).

## 5. Estimated cost

- Expected volume: 2,000 leads/month
- Estimated cost per request: ~$0.01-0.02 (short prompt, structured output)
  → ~$20-40/month in API costs
- One-time implementation cost: ~$10,000 (prompt + eval set + integration
  with CRM)
- Estimated monthly savings: ~$18,000+ (most of the $20,000 coordinator cost,
  minus spot-checking time and API cost) → payback in well under 1 month

## 6. Rollout plan

- [x] **Phase 1 - Shadow mode**: run the classifier on incoming leads for 2
  weeks, log its routing decision alongside the coordinator's actual
  decision, measure agreement rate (Section 3's accuracy metric).
- [x] **Phase 2 - Human-in-the-loop**: for low-confidence predictions, show
  the coordinator the model's suggestion as a default they can override.
- [x] **Phase 3 - Auto-route above a confidence threshold**, fall back to
  Phase 2 below it.
- [ ] **Phase 4 - Full automation**: only if Phase 3's accuracy holds steady
  over a full quarter and misroutes stay rare/low-cost.

Advancing from Phase 1 → 2 requires hitting the 90% agreement target on the
shadow-mode data; advancing 2 → 3 requires the confidence threshold to be
calibrated against real outcomes, not just held-out accuracy.
