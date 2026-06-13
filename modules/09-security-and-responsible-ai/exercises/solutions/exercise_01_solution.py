"""
Solution: Exercise 1 - Write a guardrail function
"""

import json

ALLOWED_TOOLS = {"search_emails", "read_email", "archive_email", "send_email", "delete_email"}

READ_ONLY_OR_LOW_RISK = {"search_emails", "read_email", "archive_email"}
REQUIRES_APPROVAL = {"send_email", "delete_email"}


class ToolCallBlocked(Exception):
    """Raised when a tool call is rejected by the guardrail."""


def check_tool_call(name: str, tool_input: dict) -> str | None:
    if name not in ALLOWED_TOOLS:
        raise ToolCallBlocked(f"Tool '{name}' is not on the allow-list for this task.")

    if name in REQUIRES_APPROVAL:
        return (
            f"Tool '{name}' with input {json.dumps(tool_input)} requires "
            f"human approval before it can run."
        )

    # name in READ_ONLY_OR_LOW_RISK
    return None


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

    # Discussion:
    # - "Reversibility" matters separately from "destructiveness" because it
    #   changes the cost of a *mistake*. archive_email is technically a state
    #   change, but it's cheap to undo (un-archive), so auto-executing it is
    #   low-risk even if the model misjudges. send_email and delete_email are
    #   either irreversible (an email can't be unsent) or hard to recover from
    #   (a deleted email may be gone for good) — so even if the *intent* was
    #   correct, an error in the model's judgment (or a successful prompt
    #   injection) has a permanent external effect. Approval gates are most
    #   valuable exactly where mistakes can't be cheaply undone.


if __name__ == "__main__":
    main()
