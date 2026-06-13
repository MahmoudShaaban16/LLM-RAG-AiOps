"""
02 - Agentic Loop

A manual implementation of the agentic loop described in the module
README: the model can call either of two tools, we execute whatever
it asks for, feed the results back, and repeat until the model stops
calling tools (or we hit a safety cap on iterations).
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 5

CALCULATOR_TOOL = {
    "name": "calculate",
    "description": (
        "Evaluate a basic arithmetic expression (numbers, +, -, *, /, "
        "parentheses). Use this for any numeric calculation."
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

SEARCH_TOOL = {
    "name": "search_knowledge_base",
    "description": (
        "Search the internal knowledge base for information about company "
        "policies, products, or pricing. Use this when the user asks about "
        "something that might be documented internally."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A short search query, e.g. 'refund policy'",
            },
        },
        "required": ["query"],
    },
}

TOOLS = [CALCULATOR_TOOL, SEARCH_TOOL]

# Hardcoded "knowledge base" for the demo - a real implementation would
# query a database, vector store (Module 02/05), or internal API.
KNOWLEDGE_BASE = {
    "refund policy": (
        "Customers can request a full refund within 30 days of purchase. "
        "Refunds are processed within 5-7 business days."
    ),
    "annual plan price": (
        "The annual plan costs $1,200/year, billed upfront, which is "
        "equivalent to a 20% discount versus the monthly plan."
    ),
    "monthly plan price": "The monthly plan costs $125/month.",
}


def calculate(expression: str) -> float:
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        raise ValueError(f"Unsupported characters in expression: {expression!r}")
    return eval(expression)  # noqa: S307 - restricted character set above


def search_knowledge_base(query: str) -> str:
    query_lower = query.lower()
    for key, value in KNOWLEDGE_BASE.items():
        if key in query_lower or query_lower in key:
            return value
    return f"No knowledge base entry found for '{query}'."


def run_tool(name: str, tool_input: dict) -> str:
    """Dispatch a tool call to its implementation, returning a string result."""
    if name == "calculate":
        return str(calculate(**tool_input))
    if name == "search_knowledge_base":
        return search_knowledge_base(**tool_input)
    return f"Unknown tool: {name}"


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [
        {
            "role": "user",
            "content": (
                "A customer is on the annual plan and wants to know how much "
                "they'd pay over 2 years, and also wants to know our refund policy."
            ),
        }
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

        # Print what the model did this step.
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

        # Execute every requested tool call and collect results.
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
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


if __name__ == "__main__":
    main()
