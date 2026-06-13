"""
02 - Token Counting

Demonstrates two ways to reason about tokens:
  1. Counting tokens *before* sending a request (to estimate cost / check
     you're within the context window).
  2. Reading actual token usage *after* a response (what you're billed for).
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    system_prompt = "You are a helpful assistant that answers in one short paragraph."
    messages = [
        {
            "role": "user",
            "content": (
                "A team is deciding between a 200K-token and a 1M-token context "
                "window model for a document-QA feature. What should they consider?"
            ),
        }
    ]

    # 1. Estimate tokens before sending — useful for cost estimation and for
    #    checking you're not about to exceed the model's context window.
    count = client.messages.count_tokens(
        model=MODEL,
        system=system_prompt,
        messages=messages,
    )
    print(f"Estimated input tokens: {count.input_tokens}")

    # 2. Make the actual call and read real usage from the response.
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=system_prompt,
        messages=messages,
    )

    print("\n--- response ---")
    print(response.content[0].text)

    print("\n--- actual usage ---")
    print(f"input tokens:  {response.usage.input_tokens}")
    print(f"output tokens: {response.usage.output_tokens}")


if __name__ == "__main__":
    main()
