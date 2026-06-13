"""
Exercise 3: Limit max iterations and handle the cap gracefully

TODO:
  1. Run this as-is and observe what happens when MAX_ITERATIONS is reached
     while the model still wants to call tools (the for...else branch).
  2. When the cap is reached, make one final call WITHOUT tools (or with
     tool_choice={"type": "none"}) asking the model to summarize what it
     found so far from the messages already in the conversation.
  3. Confirm the user gets a useful partial answer instead of just
     "Stopped after reaching MAX_ITERATIONS".
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 3  # Deliberately too low for this task.

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

TOOLS = [SEARCH_TOOL]

KNOWLEDGE_BASE = {
    "refund policy": "Full refund within 30 days of purchase.",
    "shipping policy": "Standard shipping takes 5-7 business days; express is 1-2 days.",
    "warranty policy": "All hardware comes with a 1-year limited warranty.",
    "support hours": "Support is available Monday-Friday, 9am-6pm ET.",
}

SYSTEM_PROMPT = (
    "You help answer customer questions using the search_knowledge_base "
    "tool. Look up each topic the user asks about separately - call the "
    "tool once per topic before answering."
)


def search_knowledge_base(query: str) -> str:
    query_lower = query.lower()
    for key, value in KNOWLEDGE_BASE.items():
        if key in query_lower or query_lower in key:
            return value
    return f"No knowledge base entry found for '{query}'."


def run_tool(name: str, tool_input: dict) -> str:
    if name == "search_knowledge_base":
        return search_knowledge_base(**tool_input)
    return f"Unknown tool: {name}"


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # This requires 4 lookups - more than MAX_ITERATIONS allows.
    messages = [
        {
            "role": "user",
            "content": (
                "What are your refund policy, shipping policy, warranty "
                "policy, and support hours?"
            ),
        }
    ]

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n=== Iteration {iteration} ===")

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
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
        # TODO: make one final call here without `tools` (or with
        # tool_choice={"type": "none"}), asking the model to summarize what
        # it has found so far based on the tool results already in
        # `messages`, and print that summary.


if __name__ == "__main__":
    main()
