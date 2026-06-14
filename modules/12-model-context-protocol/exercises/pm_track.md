# Module 12 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises — inline
tools vs. an MCP server, ownership/reuse tradeoffs, and the security/
allow-list considerations — using a written scenario instead of Python.
Useful if you want to apply the module's concepts without running any code.

## Scenario

Your company has three internal AI agents, built by three different teams:

- A **support agent** (handles customer email triage, similar to Module 10)
- An **internal IT helpdesk agent** (similar to Module 03's PM track scenario)
- A **sales-ops agent** that drafts account summaries for the sales team

All three agents currently define their own tools inline (Module 03-style),
each with its own copy of:

- `get_customer_account(account_id)` — looks up account/billing info from the
  CRM
- `get_ticket_status(ticket_id)` — looks up support ticket status

In addition, the IT helpdesk agent has a `restart_service(service_name)` tool
that can restart internal services, and a `wipe_test_database()` tool used
only during QA testing — both currently exposed to the same agent that
handles regular employee requests.

The platform team is asking: should `get_customer_account` and
`get_ticket_status` be pulled out into a shared MCP server that all three
agents connect to? And separately, should anything change about how
`restart_service` and `wipe_test_database` are exposed?

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Reuse and ownership.** Using the module's three-factor framing (number
   of consumers, who owns the implementation, update-cycle independence),
   make the case for pulling `get_customer_account` and `get_ticket_status`
   out into a shared MCP server. Who would plausibly *own* that server, and
   what changes for each of the three agent teams when that team updates the
   underlying CRM/ticketing integration?

2. **Operational surface tradeoff.** The module notes that MCP adds an extra
   operational surface (a second service to run and secure). What's the
   tradeoff here — currently, if the CRM's API changes, what has to happen
   today (with three inline copies) vs. after the shared MCP server exists?
   Is the added operational surface worth it in this scenario? Why or why
   not?

3. **Security and allow-listing.** `restart_service` and `wipe_test_database`
   are currently both available to the IT helpdesk agent that also handles
   regular employee requests. Using Module 09's allow/approve/block pattern
   (as applied to MCP tools in Section 6 of this module):
   - Which of these two tools, if any, should be removed from the tool list
     entirely for this agent?
   - Which, if any, should remain available but require human approval
     before execution?
   - If `restart_service` were later exposed via a shared "ops-tools" MCP
     server that *other* agents could also connect to, what extra question
     would you want answered about that server before connecting your IT
     helpdesk agent to it?

4. **Decision summary.** Write a one-paragraph recommendation to the platform
   team covering: (a) what to do about `get_customer_account` /
   `get_ticket_status`, and (b) what to do about `restart_service` /
   `wipe_test_database`, referencing the relevant tradeoffs from above.

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. Both `get_customer_account` and `get_ticket_status` have **three
   consumers** (the support, IT helpdesk, and sales-ops agents) and are
   currently **duplicated three times**, each maintained independently. This
   is exactly the situation the module flags as a good fit for MCP: the same
   tools, used by multiple applications, ideally owned by whoever owns the
   underlying CRM/ticketing system (likely a data/platform team, not any of
   the three agent teams). After the move, when the CRM API changes, the
   platform team updates the MCP server **once**, and all three agents pick
   up the change automatically via `list_tools()` / `call_tool()` — no
   redeploys needed in the agent codebases.

2. Today, if the CRM API changes, **three separate teams** each need to
   notice, update their inline tool implementation, test, and redeploy —
   and they may do so at different times, leading to inconsistent behavior
   across agents in the meantime. After the shared MCP server exists, that
   becomes **one team, one update, one deploy** — but now that server is a
   new service that must be kept running, monitored, and secured (Module 07
   concerns apply to it too). In this scenario, with three real consumers and
   a shared underlying system, the added operational surface is very likely
   worth it — the current cost (three teams maintaining duplicate
   integrations that can drift out of sync) is the kind of recurring,
   distributed cost that MCP is designed to remove.

3. `wipe_test_database` should be **removed from the tool list entirely**
   for the IT helpdesk agent — it has no legitimate role in handling regular
   employee requests, and its presence is pure downside (Module 09's "block"
   category). `restart_service` is plausibly a legitimate action for an IT
   helpdesk agent to take, but restarting a service is disruptive and hard to
   undo cleanly — it should remain available but **require human approval**
   before execution (Module 09's "approve" category), following the
   allow/approve/block pattern from Section 6. If `restart_service` were
   later exposed via a shared third-party "ops-tools" MCP server, the extra
   question to answer is: **who operates that server, and what is its full
   tool list?** — per Section 6, an MCP server you don't operate is untrusted
   in two ways: its tool *descriptions* could be crafted to manipulate the
   model, and it may expose more tools (like `wipe_database`) than your
   agent should ever see, so you'd want to confirm your allow-list filters
   the discovered tool list down to only what this agent needs, not just
   block at call time.

4. **Recommendation:** Pull `get_customer_account` and `get_ticket_status`
   into a shared MCP server owned by the team that owns the CRM/ticketing
   integration — with three real consumers and a shared underlying system
   that changes independently of any one agent, the reuse and
   update-cycle benefits clearly outweigh the cost of running one additional
   service. For `restart_service` and `wipe_test_database`: remove
   `wipe_test_database` from the IT helpdesk agent's tool list entirely (it
   should never have been reachable from a request-handling agent), and keep
   `restart_service` available but gated behind human approval. If
   `restart_service` is later moved to a shared ops-tools MCP server, apply
   the allow-list filter at tool-discovery time (not just at call time) so
   that only the approved tools — not the server's full catalog — are ever
   offered to the model.

</details>
