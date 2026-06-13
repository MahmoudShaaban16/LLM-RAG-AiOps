"""
Solution: Exercise 1 - Add a new tool to the agentic loop
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

ORDER_STATUS_TOOL = {
    "name": "get_order_status",
    "description": (
        "Look up the shipping status and estimated delivery date for a "
        "customer order by its order ID. Use this when the user asks about "
        "the status of a specific order - do not use search_knowledge_base "
        "for order status questions."
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

TOOLS = [SEARCH_TOOL, ORDER_STATUS_TOOL]

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


def get_order_status(order_id: str) -> str:
    order = ORDERS.get(order_id)
    if order is None:
        return f"No order found with id '{order_id}'."
    return f"Order {order_id} is {order['status']}, estimated delivery {order['eta']}."


def run_tool(name: str, tool_input: dict) -> str:
    if name == "search_knowledge_base":
        return search_knowledge_base(**tool_input)
    if name == "get_order_status":
        return get_order_status(**tool_input)
    return f"Unknown tool: {name}"


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [
        {
            "role": "user",
            "content": (
                "What's our refund policy, and what's the status of order A1003?"
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

    # Discussion:
    # - The two tool descriptions are written to be mutually exclusive:
    #   search_knowledge_base explicitly covers "policies, products, or
    #   pricing", while get_order_status explicitly says "do not use
    #   search_knowledge_base for order status questions." This kind of
    #   cross-referencing in descriptions helps the model disambiguate when
    #   tools could otherwise overlap (e.g., "policy" could vaguely relate
    #   to an order too).
    # - Because the user message asks two distinct questions, the model
    #   typically calls both tools - sometimes in the same turn (multiple
    #   tool_use blocks in one response), sometimes across two iterations.
    #   Either is correct; the loop handles both.


if __name__ == "__main__":
    main()
