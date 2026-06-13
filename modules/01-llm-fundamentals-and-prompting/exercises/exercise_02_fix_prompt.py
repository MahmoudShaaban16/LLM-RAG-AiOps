"""
Exercise 2: Fix a vague prompt

The vague version below produces inconsistent results. Rewrite it (using
a system prompt and/or a more explicit user prompt) so it reliably returns:
  - Exactly 3 bullet points
  - Formal tone, for a prospective enterprise customer
  - No invented product details — if unsure, it should say so

Run main() a few times and confirm the output format stays consistent.
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"


def vague_version(client: Anthropic) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": "Tell me about our product."}],
    )
    return response.content[0].text


def your_improved_version(client: Anthropic) -> str:
    # TODO: Replace this with a system prompt + user prompt that produces
    # a consistent, 3-bullet-point, formal response that doesn't invent
    # product details.
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": "Tell me about our product."}],
    )
    return response.content[0].text


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== Vague version ===")
    print(vague_version(client))

    print("\n=== Your improved version (run this 3x and compare) ===")
    for i in range(3):
        print(f"\n--- run {i + 1} ---")
        print(your_improved_version(client))


if __name__ == "__main__":
    main()
