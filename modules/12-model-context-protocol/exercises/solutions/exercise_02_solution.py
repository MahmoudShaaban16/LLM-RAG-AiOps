"""
Solution: Exercise 2 - Apply Module 09's allow-list guardrail to MCP tool
calls.
"""

import json

DISCOVERED_TOOLS = [
    "get_service_status",
    "restart_service",
    "wipe_database",
    "tail_logs",
]

ALLOWED_TOOLS = {"get_service_status", "restart_service", "tail_logs"}

READ_ONLY_OR_LOW_RISK = {"get_service_status", "tail_logs"}
REQUIRES_APPROVAL = {"restart_service"}


class ToolCallBlocked(Exception):
    """Raised when a tool call is rejected by the guardrail."""


def check_tool_call(name: str, tool_input: dict) -> str | None:
    if name not in ALLOWED_TOOLS:
        raise ToolCallBlocked(f"Tool '{name}' is not on the allow-list for this agent.")

    if name in REQUIRES_APPROVAL:
        return (
            f"Tool '{name}' with input {json.dumps(tool_input)} requires "
            f"human approval before it can run."
        )

    return None


def filter_discovered_tools(discovered_names: list[str]) -> list[str]:
    return [name for name in discovered_names if name in ALLOWED_TOOLS]


def main() -> None:
    allowed = filter_discovered_tools(DISCOVERED_TOOLS)
    print(f"Tools sent to Claude: {allowed}")
    print(f"Filtered out (not on allow-list): "
          f"{[t for t in DISCOVERED_TOOLS if t not in allowed]}")

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

    # Discussion:
    # - The allow-list is enforced in two places on purpose: filtering
    #   `tools` sent to Claude means the model is never even *offered*
    #   wipe_database, which reduces the chance it's called at all. But a
    #   compromised or buggy MCP server could still return a tool_use block
    #   for a tool it wasn't offered (or a client bug could call it
    #   directly) - so check_tool_call is a second, independent gate at
    #   execution time. Defense in depth: don't rely on the model only
    #   seeing the tools you intend it to use.


if __name__ == "__main__":
    main()
