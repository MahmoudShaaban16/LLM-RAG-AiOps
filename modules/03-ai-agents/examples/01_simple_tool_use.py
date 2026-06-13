"""
01 - Simple Tool Use

The smallest possible "agent" interaction: a single tool, a single
round trip. The model decides to call the tool, we run it ourselves,
and send the result back so the model can produce a final answer.

This is the building block the full agentic loop (02_agentic_loop.py)
repeats.
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

CALCULATOR_TOOL = {
    "name": "calculate",
    "description": (
        "Evaluate a basic arithmetic expression (numbers, +, -, *, /, "
        "parentheses). Use this whenever the user asks for a calculation "
        "instead of computing it yourself."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "An arithmetic expression, e.g. '23 * 47'",
            },
        },
        "required": ["expression"],
    },
}


def calculate(expression: str) -> float:
    """Very small, safe-ish arithmetic evaluator for the demo."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        raise ValueError(f"Unsupported characters in expression: {expression!r}")
    return eval(expression)  # noqa: S307 - restricted character set above


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [
        {"role": "user", "content": "What is 23 * 47? Use the calculator tool."}
    ]

    # First call: give the model the tool and force it to use this one.
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[CALCULATOR_TOOL],
        tool_choice={"type": "tool", "name": "calculate"},
        messages=messages,
    )

    print("--- Step 1: model's response ---")
    print(f"stop_reason: {response.stop_reason}")

    # Append the assistant's tool-call message to the conversation.
    messages.append({"role": "assistant", "content": response.content})

    # Find the tool_use block and run the tool ourselves.
    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    print(f"Model wants to call: {tool_use_block.name}({tool_use_block.input})")

    result = calculate(**tool_use_block.input)
    print(f"Tool result: {result}")

    # Send the tool result back as a user message containing a tool_result block.
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": str(result),
                }
            ],
        }
    )

    # Second call: model sees the tool result and responds in plain text.
    # No tool_choice here - we want a normal text reply this time.
    final_response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[CALCULATOR_TOOL],
        messages=messages,
    )

    print("\n--- Step 2: final response ---")
    print(f"stop_reason: {final_response.stop_reason}")
    for block in final_response.content:
        if block.type == "text":
            print(block.text)


if __name__ == "__main__":
    main()
