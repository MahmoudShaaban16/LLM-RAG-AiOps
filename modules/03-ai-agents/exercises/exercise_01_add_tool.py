"""
Exercise 1: Add a new tool to the agentic loop

TODO:
  1. Define a new tool `get_order_status` (input: order_id, output: a string
     describing the order's status) using the ORDERS data below.
  2. Add it to TOOLS and to run_tool's dispatch.
  3. Update the user message to ask about both the refund policy and an
     order's status, then run the loop and confirm both tools get called.
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 5

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

# TODO: define ORDER_STATUS_TOOL here, following the same shape as
# SEARCH_TOOL above. It should take an `order_id` string.

TOOLS = [SEARCH_TOOL]  # TODO: add ORDER_STATUS_TOOL once defined

KNOWLEDGE_BASE = {
    "refund policy": (
        "Customers can request a full refund within 30 days of purchase. "
        "Refunds are processed within 5-7 business days."
    ),
    "annual plan price": (
        "The annual plan costs $1,200/year, billed upfront, which is "
        "equivalent to a 20% discount versus the monthly plan."
    ),
}

# Hardcoded "order database" for the demo.
ORDERS = {
    "A1001": {"status": "shipped", "eta": "2026-06-15"},
    "A1002": {"status": "processing", "eta": "2026-06-18"},
    "A1003": {"status": "delivered", "eta": "2026-06-10"},
}


def search_knowledge_base(query: str) -> str:
    query_lower = query.lower()
    for key, value in KNOWLEDGE_BASE.items():
        if key in query_lower or query_lower in key:
            return value
    return f"No knowledge base entry found for '{query}'."


# TODO: implement get_order_status(order_id) using the ORDERS dict.


def run_tool(name: str, tool_input: dict) -> str:
    if name == "search_knowledge_base":
        return search_knowledge_base(**tool_input)
    # TODO: dispatch to get_order_status when name == "get_order_status"
    return f"Unknown tool: {name}"


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [
        {
            "role": "user",
            "content": "What's our refund policy?",  # TODO: also ask about an order
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
                result = run_tool(block.name, block.input)
                print(f"[tool_result] {result}")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"\nStopped after reaching MAX_ITERATIONS={MAX_ITERATIONS}.")


if __name__ == "__main__":
    main()
