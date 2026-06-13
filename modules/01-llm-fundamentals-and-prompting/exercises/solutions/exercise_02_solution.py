"""
Solution: Exercise 2 - Fix a vague prompt
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = (
    "You are a product marketing assistant writing for prospective enterprise "
    "customers. When asked about 'our product', respond with exactly 3 bullet "
    "points, in a formal tone suitable for an enterprise buyer. "
    "Do not invent specific features, pricing, or statistics you don't have "
    "information about — if you don't have enough information about the "
    "product, say so explicitly instead of making something up."
)

USER_PROMPT = (
    "Tell me about our product. If you don't have details about it, say that "
    "clearly rather than guessing."
)


def vague_version(client: Anthropic) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": "Tell me about our product."}],
    )
    return response.content[0].text


def your_improved_version(client: Anthropic) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT}],
    )
    return response.content[0].text


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== Vague version ===")
    print(vague_version(client))

    print("\n=== Improved version (run 3x) ===")
    for i in range(3):
        print(f"\n--- run {i + 1} ---")
        print(your_improved_version(client))

    # Discussion:
    # - The system prompt fixes the *role* (marketing assistant), *audience*
    #   (enterprise buyer), *format* (exactly 3 bullets), and *constraint*
    #   (don't invent details) once, so it applies consistently across runs.
    # - The user prompt reinforces the "don't guess" constraint, which
    #   reduces (but doesn't eliminate) hallucination risk.
    # - For true consistency in production, you'd also want to ground this
    #   in real product docs via RAG (Module 02) rather than relying on the
    #   model's general knowledge.


if __name__ == "__main__":
    main()
