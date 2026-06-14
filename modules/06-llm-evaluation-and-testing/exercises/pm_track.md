# Module 06 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises — building
an eval dataset, interpreting LLM-as-judge scores, and deciding whether a
prompt change is safe to ship — using a written scenario instead of Python.
Useful if you want to apply the module's concepts without running any code.

## Scenario

Your company has an AI assistant embedded in its expense-reporting app.
Employees type things like:

- "Can I expense a client dinner that cost $180 for 3 people?"
- "I lost my hotel receipt — what should I do?"
- "Submit a reimbursement request for my flight to Chicago."
- "My manager rejected my expense — can you approve it anyway?"

The engineering team wants to ship a new, shorter system prompt that they
believe will reduce response length (and therefore cost) — but they're not
sure if it will hurt answer quality. Before this module, the only "testing"
was a developer trying a few messages manually and eyeballing the replies.

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Building the eval set.** For each of the four example requests above,
   write 2-3 **criteria** (not exact expected text) that a good response
   should satisfy. Make sure at least one request's criteria includes
   something the assistant should explicitly *not* do.

2. **Picking eval cases that matter.** The module says a small, well-chosen
   eval set (20-50 cases) beats a huge set of near-duplicates. Beyond the
   four requests above, suggest 2 additional kinds of cases this eval set
   should include (e.g., edge cases, adversarial cases) and explain why each
   is important for an expense-reporting assistant specifically.

3. **Reading LLM-as-judge output.** Suppose the judge scores the new
   (shorter) prompt's responses on a 1-5 rubric and produces this summary:

   | Case | Old prompt score | New prompt score |
   |---|---|---|
   | Client dinner question | 4 | 4 |
   | Lost receipt | 5 | 3 |
   | Flight reimbursement | 4 | 4 |
   | "Approve it anyway" (adversarial) | 5 | 2 |

   The *average* score barely changed (4.5 → 3.25... actually compute it).
   Based on the module's guidance on reading regression results, what would
   you do with this data? Which case(s) most concern you, and why?

4. **Should we ship it?** Using the module's framework (net improvement vs.
   per-case regressions, plus cost/latency considerations), write a 2-3
   sentence recommendation: ship the new prompt, ship with modifications, or
   don't ship? What additional eval cases (if any) would make you more
   confident either way?

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. Example criteria:
   - **"Client dinner $180 for 3 people"**: States whether this is within
     policy (e.g., per-person meal limits), mentions any documentation
     needed (receipt, attendee names), and does not state a specific dollar
     limit unless that's actually in the company's policy (avoid inventing
     numbers).
   - **"Lost my hotel receipt"**: Explains the company's lost-receipt
     process (e.g., a signed affidavit form), and does **not** tell the
     employee they simply can't be reimbursed (this is the "should not do"
     criterion — an overly strict answer here is a real failure mode).
   - **"Submit a reimbursement for my flight"**: Either walks the user
     through the submission steps or (if a tool exists) initiates the
     submission, and confirms what information/receipts are required.

2. Two additional case types:
   - **Edge cases**: a request right at a policy boundary (e.g., "can I
     expense a $75 meal when the per-person limit is $75 exactly?") — these
     are where vague policy language most often produces inconsistent
     answers.
   - **Adversarial/off-policy cases**: requests asking the assistant to
     override a rejection, approve something against policy, or "make an
     exception just this once" (like the "approve it anyway" example) —
     these matter enormously for an expense assistant because a wrong answer
     here could mean the assistant effectively tells an employee they can
     bypass financial controls, which is a compliance and audit risk, not
     just a quality nit.

3. The average *does* drop — (4+5+4+5)/4 = 4.5 for the old prompt vs.
   (4+3+4+2)/4 = 3.25 for the new prompt — a meaningful regression, not "barely
   changed." But more importantly, the module's guidance is to look at
   **per-case deltas, not just the average**: the "lost receipt" case dropped
   2 points and the "approve it anyway" adversarial case dropped 3 points
   (from a 5, a strong correct refusal, down to a 2). The adversarial case is
   the most concerning — a shorter prompt may have dropped language that told
   the assistant to firmly decline policy-override requests, which is exactly
   the kind of regression that's invisible in casual manual testing but shows
   up immediately in a structured eval.

4. **Don't ship as-is.** Even though the prompt is shorter (likely cheaper
   and faster), it regresses on two cases — including the adversarial one,
   which has outsized real-world risk (an employee screenshotting "the
   assistant said I could expense this" as justification to their manager).
   Recommendation: investigate what specifically changed in the new prompt
   that affected the "lost receipt" and "approve it anyway" cases — likely
   some guardrail language was cut for brevity — and restore just that part
   while keeping the rest of the shortening. To be more confident either way,
   add 3-5 more adversarial cases (different phrasings of "override the
   policy/rejection") to confirm whether this is a one-off or a systematic
   gap in the new prompt.

</details>
