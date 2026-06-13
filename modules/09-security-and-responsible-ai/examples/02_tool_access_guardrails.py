"""
02 - Tool Access Guardrails

Demonstrates an agent with multiple tools, where a guardrail function
validates every tool_use request BEFORE it is executed — independent of
what the model "decided" to do.

The guardrail enforces:
  - An allow-list: only tools the current task is permitted to use can run.
  - A "requires human approval" flag: destructive tools (e.g., delete_file)
    are never auto-executed — they're surfaced for approval instead.

This follows the agentic-loop pattern from Module 03
(examples/02_agentic_loop.py): the model proposes tool calls via tool_use
blocks, and application code decides what actually runs.
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 5

# --- Tool definitions --------------------------------------------------

SEARCH_FILES_TOOL = {
    "name": "search_files",
    "description": "Search for files by name in the workspace. Read-only.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Filename or partial name to search for."},
        },
        "required": ["query"],
    },
}

READ_FILE_TOOL = {
    "name": "read_file",
    "description": "Read the contents of a file. Read-only.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path of the file to read."},
        },
        "required": ["path"],
    },
}

DELETE_FILE_TOOL = {
    "name": "delete_file",
    "description": "Permanently delete a file from the workspace. Destructive.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path of the file to delete."},
        },
        "required": ["path"],
    },
}

SEND_EMAIL_TOOL = {
    "name": "send_email",
    "description": "Send an email on behalf of the user. Has external side effects.",
    "input_schema": {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["to", "subject", "body"],
    },
}

TOOLS = [SEARCH_FILES_TOOL, READ_FILE_TOOL, DELETE_FILE_TOOL, SEND_EMAIL_TOOL]

# --- Guardrail policy ----------------------------------------------------

# The allow-list for THIS task. A different task (e.g., a "file cleanup"
# agent) might have a different allow-list — the point is that it's
# explicit and scoped to what the current task actually needs.
ALLOWED_TOOLS = {"search_files", "read_file", "delete_file", "send_email"}

# Tools that have real-world side effects and must never be auto-executed,
# even if they're on the allow-list.
REQUIRES_APPROVAL = {"delete_file", "send_email"}


# --- Fake tool implementations (for demo purposes) ------------------------

FAKE_FILESYSTEM = {
    "/workspace/notes.txt": "Meeting notes from Q3 planning.",
    "/workspace/draft_report.txt": "Draft report content here.",
    "/workspace/old_backup.zip": "(binary content)",
}


def search_files(query: str) -> str:
    matches = [path for path in FAKE_FILESYSTEM if query.lower() in path.lower()]
    return json.dumps(matches)


def read_file(path: str) -> str:
    return FAKE_FILESYSTEM.get(path, f"File not found: {path}")


def delete_file(path: str) -> str:
    if path in FAKE_FILESYSTEM:
        del FAKE_FILESYSTEM[path]
        return f"Deleted {path}"
    return f"File not found: {path}"


def send_email(to: str, subject: str, body: str) -> str:
    return f"Email sent to {to} with subject '{subject}'"


TOOL_IMPLEMENTATIONS = {
    "search_files": search_files,
    "read_file": read_file,
    "delete_file": delete_file,
    "send_email": send_email,
}


# --- Guardrail ------------------------------------------------------------


class ToolCallBlocked(Exception):
    """Raised when a tool call is rejected by the guardrail."""


def check_tool_call(name: str, tool_input: dict) -> str | None:
    """Validate a proposed tool call against policy.

    Returns:
        None if the call is allowed to execute immediately.
        A string explaining why it's pending approval, if it requires
        human approval (and should NOT be executed automatically).

    Raises:
        ToolCallBlocked if the call is not allowed at all.
    """
    if name not in ALLOWED_TOOLS:
        raise ToolCallBlocked(
            f"Tool '{name}' is not on the allow-list for this task."
        )

    if name in REQUIRES_APPROVAL:
        return (
            f"Tool '{name}' with input {json.dumps(tool_input)} requires "
            f"human approval before it can run."
        )

    return None


def run_tool(name: str, tool_input: dict) -> str:
    return TOOL_IMPLEMENTATIONS[name](**tool_input)


# --- Agent loop ------------------------------------------------------------


def run_agent(client: Anthropic, user_request: str) -> None:
    messages = [{"role": "user", "content": user_request}]

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n=== Iteration {iteration} ===")

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"[text] {block.text.strip()}")
            elif block.type == "tool_use":
                print(f"[tool_use] {block.name}({json.dumps(block.input)})")

        if response.stop_reason != "tool_use":
            print("\n--- Final response ---")
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            return

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            try:
                pending_reason = check_tool_call(block.name, block.input)
            except ToolCallBlocked as exc:
                print(f"[blocked] {exc}")
                result = f"Tool call blocked by policy: {exc}"
            else:
                if pending_reason is not None:
                    print(f"[pending approval] {pending_reason}")
                    result = (
                        "This action requires human approval and has NOT been "
                        "executed. A request has been queued for review."
                    )
                else:
                    result = run_tool(block.name, block.input)
                    print(f"[tool_result] {result}")

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            )

        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"\nStopped after reaching MAX_ITERATIONS={MAX_ITERATIONS}.")


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("########## Scenario: read-only request ##########")
    run_agent(
        client,
        "Find any files related to 'report' and tell me what's in them.",
    )

    print("\n\n########## Scenario: destructive request ##########")
    run_agent(
        client,
        "Delete the old backup file at /workspace/old_backup.zip, it's no "
        "longer needed.",
    )


if __name__ == "__main__":
    main()
