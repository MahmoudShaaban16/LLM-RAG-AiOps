"""
Exercise 1: Write a guardrail function

TODO:
  1. Implement check_tool_call(name, tool_input) following the pattern in
     examples/02_tool_access_guardrails.py:
       - Return None if the call can execute immediately.
       - Return a string explaining why, if it requires human approval.
       - Raise ToolCallBlocked if the tool isn't allowed at all.
  2. Add test calls covering each category and print the result.
"""

import json

# Tools for an "inbox assistant" agent.
ALLOWED_TOOLS = {"search_emails", "read_email", "archive_email", "send_email", "delete_email"}

READ_ONLY_OR_LOW_RISK = {"search_emails", "read_email", "archive_email"}
REQUIRES_APPROVAL = {"send_email", "delete_email"}


class ToolCallBlocked(Exception):
    """Raised when a tool call is rejected by the guardrail."""


def check_tool_call(name: str, tool_input: dict) -> str | None:
    # TODO: implement the guardrail logic described above.
    pass


def main() -> None:
    test_calls = [
        ("search_emails", {"query": "invoice"}),
        ("archive_email", {"id": "msg_123"}),
        ("send_email", {"to": "customer@example.com", "subject": "Re: Issue", "body": "..."}),
        ("delete_email", {"id": "msg_456"}),
        ("export_all_contacts", {}),  # not on the allow-list at all
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
