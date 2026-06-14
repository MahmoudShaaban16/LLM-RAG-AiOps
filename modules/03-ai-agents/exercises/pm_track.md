# Module 03 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises — tool
design, planning pattern, and "should I build an agent?" — using a written
scenario instead of Python. Useful if you want to apply the module's
concepts without running any code.

## Scenario

Your company runs an internal IT helpdesk. Employees submit requests like:

- "My laptop won't connect to the VPN."
- "I need access to the shared finance drive."
- "What's the status of ticket #4521?"
- "Reset my password — I'm locked out."

Leadership wants to explore whether an LLM-based assistant could handle a
chunk of these requests, either by answering directly or by taking action
(e.g., creating a ticket, checking a ticket's status, resetting a password
via the IT system's API).

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Single call vs. agent.** Which of the four example requests above could
   be answered with a *single* LLM call (Module 01-style — no tools), and
   which would need the model to call a *tool* and see the result before
   responding? Explain why for each.

2. **Tool design.** For the requests that need a tool, sketch out (in plain
   English — no JSON/code) 2-3 tools this assistant would need. For each
   tool, write:
   - A name
   - A one-sentence description of when the model should use it
   - What information it needs as input
   - What it returns

3. **Planning pattern.** Would this assistant be better suited to a ReAct
   style (decide one step at a time) or plan-and-execute (list all steps,
   then execute)? Consider: do requests typically need just one tool call,
   or could a single request plausibly need several (e.g., "reset my
   password and also check on ticket #4521")?

4. **Should we build this?** Using the four criteria from the module
   (complexity, value, viability, cost of error), make the case for or
   against building this as an agent. In particular: what's the **cost of
   error** for each of the four example requests — which ones are safe for
   the model to act on directly, and which should require a human to
   confirm before anything happens (e.g., resetting a password)?

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. **"What's the status of ticket #4521?"** clearly needs a tool — the
   model has no way to know ticket statuses, so it must call a
   `get_ticket_status` tool and report the result. **"My laptop won't
   connect to the VPN"** could often be answered *without* a tool, by
   walking through standard troubleshooting steps (Module 01-style),
   though if those steps fail, the assistant might need to call a
   `create_ticket` tool. "Need access to the shared finance drive" and
   "reset my password" both require tools, because they're requests to
   *change* something in a real system, not just answer a question.

2. Example tools:
   - `get_ticket_status(ticket_id)` — "Use when the user asks about the
     status of an existing ticket." Returns the ticket's current status
     and last update.
   - `create_ticket(category, description)` — "Use when the user has an
     issue that needs IT follow-up and no existing ticket covers it."
     Returns a new ticket ID.
   - `reset_password(employee_id)` — "Use when the user explicitly asks to
     reset their own password and has been identity-verified." Returns
     confirmation or an error if verification hasn't happened.

3. Most single requests need at most one tool call, which leans toward
   ReAct (simple, adaptive). But the combined example ("reset my password
   *and* check on ticket #4521") needs two independent tool calls — ReAct
   handles this fine too, by simply calling each tool in sequence as it
   reasons. Plan-and-execute would be overkill unless requests routinely
   involve many dependent steps (e.g., "reset my password, then update my
   VPN ticket to note it's resolved, then notify my manager").

4. **Complexity:** moderate — multiple request types, some needing tools.
   **Value:** likely high — IT helpdesks handle large volumes of repetitive
   requests. **Viability:** depends on whether `get_ticket_status` /
   `create_ticket` APIs already exist and are reliable. **Cost of error:**
   this is the key one — `get_ticket_status` and `create_ticket` are
   low-risk (read-only or easily reversible/auditable), so the agent can
   act on these automatically. `reset_password` has a *high* cost of error
   if the requester isn't who they claim to be (account takeover risk) —
   this should require identity verification and/or human approval before
   executing, following the same approval-flow thinking as Module 09.

</details>
