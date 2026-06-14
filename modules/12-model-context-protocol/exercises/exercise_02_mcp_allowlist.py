"""
Exercise 2: Apply Module 09's allow-list guardrail to MCP tool calls

A third-party "ops-tools" MCP server advertises the tools below via
`list_tools()`. Some are safe to call automatically, some should require
human approval, and `wipe_database` should never be called by this agent
at all - even though the server offers it.

TODO:
  1. Implement `check_tool_call(name, tool_input)`:
       - Raise ToolCallBlocked if `name` is not in ALLOWED_TOOLS.
       - Return a string explaining why, if `name` is in REQUIRES_APPROVAL.
       - Return None if the call can execute immediately.
  2. Implement `filter_discovered_tools(discovered_names)` which takes the
     list of tool names returned by the MCP server's `list_tools()` and
     returns only the ones in ALLOWED_TOOLS - this is the list you'd
     actually pass to Claude as `tools`.
  3. Run this script and confirm:
       - `wipe_database` is filtered out of the tools sent to Claude.
       - A direct call to `wipe_database` is BLOCKED by check_tool_call,
         even though the server *advertises* it.
       - `restart_service` requires approval; `get_service_status` does not.

This script does NOT call Claude or an MCP server - it's a standalone
guardrail exercise, no ANTHROPIC_API_KEY needed.
"""

import json

# Tools discovered from list_tools() on a third-party ops-tools MCP server.
DISCOVERED_TOOLS = [
    "get_service_status",
    "restart_service",
    "wipe_database",
    "tail_logs",
]

# This agent's allow-list - deliberately narrower than what the server offers.
ALLOWED_TOOLS = {"get_service_status", "restart_service", "tail_logs"}

READ_ONLY_OR_LOW_RISK = {"get_service_status", "tail_logs"}
REQUIRES_APPROVAL = {"restart_service"}


class ToolCallBlocked(Exception):
    """Raised when a tool call is rejected by the guardrail."""


def check_tool_call(name: str, tool_input: dict) -> str | None:
    # TODO: implement as described above.
    pass


def filter_discovered_tools(discovered_names: list[str]) -> list[str]:
    # TODO: return only the names that are in ALLOWED_TOOLS.
    pass


def main() -> None:
    allowed = filter_discovered_tools(DISCOVERED_TOOLS)
    print(f"Tools sent to Claude: {allowed}")
    print(f"Filtered out (not on allow-list): "
          f"{[t for t in DISCOVERED_TOOLS if t not in (allowed or [])]}")

    test_calls = [
        ("get_service_status", {"service": "api"}),
        ("restart_service", {"service": "api"}),
        ("wipe_database", {"database": "prod"}),
    ]

    for name, tool_input in test_calls:
        try:
            result = check_tool_call(name, tool_input)
        except ToolCallBlocked as exc:
            print(f"{name}({json.dumps(tool_input)}) -> BLOCKED: {exc}")
            continue

        if result is None:
            print(f"{name}({json.dumps(tool_input)}) -> ALLOWED (executes immediately)")
        else:
            print(f"{name}({json.dumps(tool_input)}) -> PENDING APPROVAL: {result}")


if __name__ == "__main__":
    main()
