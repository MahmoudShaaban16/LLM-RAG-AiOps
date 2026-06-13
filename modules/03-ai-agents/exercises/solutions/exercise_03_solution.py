"""
Solution: Exercise 3 - Limit max iterations and handle the cap gracefully
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

        # Final call with no tools available: the model can't keep calling
        # tools, so it must answer using whatever tool_results are already
        # in `messages`.
        print("\n--- Requesting partial summary (no tools) ---")
        summary_messages = messages + [
            {
                "role": "user",
                "content": (
                    "You've run out of tool calls. Summarize what you've "
                    "found so far for each topic you looked up, and clearly "
                    "say which topics you weren't able to look up yet."
                ),
            }
        ]
        final_response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tool_choice={"type": "none"},
            messages=summary_messages,
        )
        for block in final_response.content:
            if block.type == "text":
                print(block.text)

    # Discussion:
    # - With MAX_ITERATIONS=3, the model usually manages 2-3 lookups before
    #   the cap hits, leaving at least one topic unanswered.
    # - Forcing tool_choice={"type": "none"} on the final call guarantees a
    #   text response - without it, the model might try to call a tool again
    #   and you'd be back where you started.
    # - Picking MAX_ITERATIONS: too low and well-defined multi-step tasks
    #   fail partway through (as seen here); too high and a misbehaving
    #   model can run up cost/latency before you intervene. A common
    #   approach is to set it generously above the *expected* number of
    #   steps for the task (e.g., 2-3x), and pair it with monitoring/alerts
    #   on iteration counts in production rather than relying on the cap
    #   alone as the primary safeguard.


if __name__ == "__main__":
    main()
