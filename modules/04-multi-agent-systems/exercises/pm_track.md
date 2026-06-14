# Module 04 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises —
orchestration pattern choice, agent handoff design, and cost/latency
tradeoffs — using a written scenario instead of Python. Useful if you want to
apply the module's concepts without running any code.

## Scenario

Your company wants to build an "Account Health Report" feature for customer
success managers (CSMs). For any given customer account, the feature should
produce a short report covering:

- A summary of recent support tickets (volume, themes, any unresolved
  critical issues)
- A summary of product usage trends (up, down, flat — and which features)
- An overall "risk level" (low/medium/high) with a 2-3 sentence justification
- A suggested next action for the CSM (e.g., "schedule a check-in call,"
  "no action needed")

Currently, a CSM does all of this manually by reading through tickets and
usage dashboards — it takes about 20 minutes per account, and CSMs manage
50-100 accounts each. Leadership wants an LLM-based system to generate this
report automatically, refreshed weekly for every account.

Early prototyping used a single agent with one large system prompt and access
to a `get_tickets` tool and a `get_usage_data` tool. Results were inconsistent
— sometimes the "risk level" didn't seem to reflect what was actually in the
ticket summary, and the report's tone/structure varied a lot between runs.

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Single agent vs. multi-agent.** Per Section 1, what specific symptoms in
   the scenario above suggest a single agent with one system prompt is
   straining? Which of the four reasons from Section 1 ("different
   expertise," "tool set too large," "independent steps," "separation of
   concerns") apply here, and why?

2. **Orchestration pattern.** Using Section 2's three patterns (pipeline,
   supervisor/worker, peer-to-peer), design a multi-agent architecture for
   this report. Sketch which agents/stages you'd have, what each one's job is,
   and which pattern (or combination) you chose. Justify why you didn't pick
   the other two patterns.

3. **Handoffs.** Per Section 3, define the "interface" between at least two of
   your stages — e.g., what specific structured fields would the
   "ticket-summary" stage need to hand to the "risk assessment" stage so that
   the risk level can actually be justified by the ticket data? Why would
   passing raw free-text summaries between stages be risky here, given the
   reported inconsistency problem?

4. **Cost and latency.** There are roughly 5,000 accounts company-wide,
   refreshed weekly. Using Section 4's framing, roughly how many total API
   calls per week would your design from question 2 require (give a rough
   range, accounting for any parallelism)? If the `get_tickets` and
   `get_usage_data` lookups can run independently, how would you use
   parallelism to keep latency manageable for a single account's report?

5. **Debugging a bad report.** A CSM reports that an account's risk level was
   marked "low" even though it had three unresolved critical tickets. Using
   Section 5, what's the first thing you'd want logged/inspectable to figure
   out which stage caused this, and what's your hypothesis for the most likely
   cause given the original single-agent prototype's symptoms?

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. Two of Section 1's reasons clearly apply. **"Different expertise"** — the
   single agent is being asked to act as a ticket analyst, a usage analyst,
   and a risk assessor all in one prompt, and the inconsistent risk-level
   results suggest it's not doing any of these jobs as well as a focused
   prompt would. **"Separation of concerns"** — the risk level should be
   *derived from* the ticket and usage summaries, but in a single agent
   there's no guarantee the model actually reasons from its own tool outputs
   in a structured way before stating a risk level; splitting "summarize"
   from "assess risk" into separate stages makes that dependency explicit and
   inspectable. "Tool set too large" doesn't really apply yet (only two
   tools), and "independent steps... in parallel" is more of a latency
   optimization (question 4) than the root cause of the inconsistency.

2. A **pipeline** is the best fit, because the steps are well-known and
   always happen in the same order for every account:
   - **Stage 1 — Ticket analyst agent**: calls `get_tickets`, outputs a
     structured summary (ticket volume, themes, list of unresolved critical
     tickets).
   - **Stage 2 — Usage analyst agent**: calls `get_usage_data`, outputs a
     structured summary (usage trend direction, which features changed).
   - **Stage 3 — Risk & recommendation agent**: takes the structured outputs
     of Stages 1 and 2 (no tools of its own) and produces the risk level,
     justification, and suggested next action.

   Stages 1 and 2 are independent of each other and could run in parallel
   (a light supervisor/worker flavor within an otherwise pipeline shape).
   Peer-to-peer is overkill and risky here — there's no back-and-forth
   negotiation needed, and an unbounded "conversation" between agents would
   add cost and unpredictability for a report that should be quick and
   consistent. Pure supervisor/worker (with a planning step) is also more
   than needed, since the set of subtasks is fixed and identical for every
   account — a pipeline is simpler to test and to add a human checkpoint to
   if needed later.

3. The handoff from Stage 1 (ticket analyst) to Stage 3 (risk assessor)
   should be **structured, not free text** — e.g., a JSON object with fields
   like `total_open_tickets`, `unresolved_critical_count`,
   `unresolved_critical_summaries` (a list of short strings), and
   `recent_theme_tags`. Similarly, Stage 2 → Stage 3 might hand off
   `usage_trend` (`"up" | "down" | "flat"`) and `affected_features`. If Stage
   1 instead handed Stage 3 a paragraph of prose, Stage 3 would have to
   *re-parse* and judge for itself whether "three unresolved critical
   tickets" should drive the risk level — which is exactly the kind of gap
   that likely caused the original inconsistency (the model "knew" about the
   tickets somewhere in its context but didn't reliably connect that to the
   risk level it stated). A structured `unresolved_critical_count` field
   makes it much harder for Stage 3 to produce a "low" risk level while that
   number is 3 — you could even add a simple deterministic check in code
   (not the LLM) that flags reports where `unresolved_critical_count > 0` but
   risk level is "low" for human review.

4. With the 3-stage pipeline (Stages 1 and 2 in parallel, then Stage 3), each
   account's report costs **3 API calls** (2 parallel + 1 synthesis). For
   5,000 accounts/week, that's roughly **15,000 API calls/week** total — not
   "5,000 reports = 5,000 calls" as a naive single-agent estimate might
   suggest. For latency on a single account: running the ticket-analyst and
   usage-analyst calls concurrently (e.g., `asyncio.gather`) means the total
   latency for those two stages is roughly the *slower* of the two, not the
   sum — then add Stage 3's latency on top. Across 5,000 accounts, the
   weekly batch job itself should also be parallelized (many accounts'
   pipelines running concurrently, within rate limits), since there's no
   dependency between different accounts' reports.

5. The first thing to inspect is **Stage 1's structured output for that
   account** — specifically, does `unresolved_critical_count` correctly show
   3, and does `unresolved_critical_summaries` actually list those tickets?
   If Stage 1's output is correct, the bug is in **Stage 3** — it received
   accurate data but didn't translate "3 unresolved critical tickets" into a
   higher risk level (a prompt issue in Stage 3, e.g., its risk-level
   criteria aren't explicit enough). If Stage 1's output is *itself* wrong
   (e.g., `unresolved_critical_count` is 0), the bug is upstream — either the
   `get_tickets` tool isn't returning the right data, or Stage 1's prompt
   isn't reliably extracting/counting critical tickets from what it gets
   back. Given the original single-agent prototype showed the same kind of
   "risk level doesn't match the underlying data" symptom, the most likely
   hypothesis is that this is a **Stage 3 reasoning/prompt issue** — the
   ticket data is probably present and correct, but the risk-assessment step
   needs more explicit criteria (e.g., "if `unresolved_critical_count` > 0,
   risk level must be at least 'medium'") rather than leaving the mapping
   from data to risk level entirely to the model's judgment.

</details>
