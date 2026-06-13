"""
Solution: Exercise 2 - Handle a tool that can fail
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
    return ORDERS[order_id]  # raises KeyError if missing


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Returns (content, is_error). Catches known failure modes and turns
    them into descriptive tool_result content instead of letting exceptions
    propagate out of the loop."""
    if name == "get_order_status":
        try:
            result = get_order_status(**tool_input)
            return json.dumps(result), False
        except KeyError:
            order_id = tool_input.get("order_id", "<missing>")
            return f"error: no order found with id '{order_id}'", True
    return f"error: unknown tool '{name}'", True


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
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content,
                }
                if is_error:
                    tool_result["is_error"] = True
                tool_results.append(tool_result)
        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"\nStopped after reaching MAX_ITERATIONS={MAX_ITERATIONS}.")

    # Discussion:
    # - Before the fix, get_order_status("Z9999") raises KeyError, which
    #   propagates out of run_tool and crashes the entire script - one bad
    #   argument from the model takes down the whole agent.
    # - After the fix, the error is caught and turned into a tool_result
    #   with is_error=True and a human-readable message. The model sees this
    #   as "the tool call failed, here's why" and typically responds by
    #   telling the user the order wasn't found - exactly the behavior we
    #   want.
    # - `is_error=True` vs. a plain string: both put the same text in front
    #   of the model, but `is_error` is part of the tool_result schema
    #   specifically so the model can distinguish "the tool ran and this is
    #   the answer" from "the tool attempt failed" - models are trained to
    #   treat these differently (e.g., considering a retry with different
    #   arguments vs. taking the text at face value as data).


if __name__ == "__main__":
    main()
