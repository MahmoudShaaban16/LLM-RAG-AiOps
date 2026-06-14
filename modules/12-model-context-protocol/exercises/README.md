# Module 12 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

## Exercise 1: Add a new tool to the MCP server and confirm auto-discovery

**Files:** [`exercise_01_add_server_tool.py`](exercise_01_add_server_tool.py), [`mcp_server.py`](mcp_server.py)

`mcp_server.py` is a local copy of [`examples/01_simple_mcp_server.py`](../examples/01_simple_mcp_server.py).

1. Add a `get_shipping_estimate` tool to `mcp_server.py` that takes a
   `country` string and returns a hardcoded shipping estimate (a
   `SHIPPING_ESTIMATES` dict is suggested in the starter file).
2. Run `exercise_01_add_server_tool.py`. It connects to the server over
   stdio and lists its tools — confirm `get_shipping_estimate` appears
   automatically, with no changes needed to the client code.
3. Call `get_shipping_estimate` directly via `session.call_tool(...)` for
   a known country and an unknown one, and print both results.

No `ANTHROPIC_API_KEY` is needed — this exercise only exercises the
MCP client/server connection.

**Think about:** What had to change on the *client* side to make the new
tool available? (Hint: nothing — that's the point of `list_tools()`.)

---

## Exercise 2: Apply Module 09's allow-list guardrail to MCP tools

**File:** [`exercise_02_mcp_allowlist.py`](exercise_02_mcp_allowlist.py)

A third-party "ops-tools" MCP server advertises `get_service_status`,
`restart_service`, `wipe_database`, and `tail_logs`. Your agent should
never be offered (or allowed to call) `wipe_database`, and
`restart_service` should require human approval.

1. Implement `check_tool_call(name, tool_input)` following the
   allow/approve/block pattern from Module 09.
2. Implement `filter_discovered_tools(discovered_names)` so the list of
   tools you'd pass to Claude excludes anything not on `ALLOWED_TOOLS`.
3. Run the script and confirm `wipe_database` is both filtered out of the
   tools sent to Claude *and* blocked if called directly.

**Think about:** Why check the allow-list in two places (once when
building the tool list, once at call time) instead of just one?

---

## Exercise 3: Inline tools vs. an MCP server — decision framework

**File:** [`exercise_03_inline_vs_mcp.py`](exercise_03_inline_vs_mcp.py)

Four scenarios describe different tool situations. For each one,
implement `recommend(scenario)` to return whether the team should use an
inline tool definition (Module 03) or an MCP server (Module 12), with a
one-sentence justification based on reuse, ownership, and operational
surface (module README section 3).

**Think about:** Which single factor — number of consumers, who owns the
implementation, or update-cycle independence — most often decides this in
practice on a real team?
