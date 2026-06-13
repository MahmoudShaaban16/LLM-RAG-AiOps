"""
Exercise 2: Handle a tool that can fail

TODO:
  1. Run this as-is with the user message asking about order "Z9999" (not in
     ORDERS) and observe the crash.
  2. Fix run_tool so a failing tool call returns a tool_result with
     "is_error": True and a descriptive message, instead of letting the
     exception crash the loop.
  3. Re-run and confirm the model handles the error gracefully.
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 5

ORDER_STATUS_TOOL = {
    "name": "get_order_status",
    "description": (
        "Look up the status and estimated delivery date for a customer "
        "order by its order ID. Use this when the user asks about the "
        "status of a specific order."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order ID, e.g. 'A1001'",
            },
        },
        "required": ["order_id"],
    },
}

TOOLS = [ORDER_STATUS_TOOL]

ORDERS = {
    "A1001": {"status": "shipped", "eta": "2026-06-15"},
    "A1002": {"status": "processing", "eta": "2026-06-18"},
    "A1003": {"status": "delivered", "eta": "2026-06-10"},
}


def get_order_status(order_id: str) -> dict:
    """Raises KeyError if the order doesn't exist - this is the failure
    mode this exercise asks you to handle."""
    return ORDERS[order_id]


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Returns (content, is_error).

    TODO: catch the KeyError from get_order_status and return a descriptive
    error message with is_error=True, instead of letting it propagate.
    """
    if name == "get_order_status":
        result = get_order_status(**tool_input)  # TODO: wrap in try/except
        return json.dumps(result), False
    return f"Unknown tool: {name}", True


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [
        {"role": "user", "content": "What's the status of order Z9999?"}
    ]

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
            print("\n--- Final answer ---")
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                content, is_error = run_tool(block.name, block.input)
                print(f"[tool_result] is_error={is_error} content={content}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": content,
                        # TODO: only set is_error when relevant
                        "is_error": is_error,
                    }
                )
        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"\nStopped after reaching MAX_ITERATIONS={MAX_ITERATIONS}.")


if __name__ == "__main__":
    main()
