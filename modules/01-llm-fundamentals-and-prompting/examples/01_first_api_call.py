"""
01 - First API Call

A minimal example of calling the Claude Messages API, with the model
chosen via a config value rather than hardcoded — so it can be swapped
(or A/B tested) without touching the call site.
"""

import os

from anthropic import Anthropic

# Model tiers, from most to least capable/expensive.
# Pick the cheapest tier that meets your quality bar, then move up only
# if needed. See the module README for the full pricing/context table.
MODELS = {
    "best": "claude-opus-4-8",
    "balanced": "claude-sonnet-4-6",
    "fast": "claude-haiku-4-5",
}

MODEL = MODELS["balanced"]


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="You are a concise technical writing assistant. Answer in 2-3 sentences.",
        messages=[
            {
                "role": "user",
                "content": "Explain what a context window is, for a software engineer.",
            }
        ],
    )

    # `content` is a list of blocks; for a simple text reply there's one text block.
    print(response.content[0].text)

    print("\n--- usage ---")
    print(f"input tokens:  {response.usage.input_tokens}")
    print(f"output tokens: {response.usage.output_tokens}")


if __name__ == "__main__":
    main()
