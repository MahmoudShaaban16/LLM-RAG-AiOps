"""
Exercise 1: Estimate and verify token usage

TODO:
  1. Count tokens for SYSTEM_PROMPT + USER_PARAGRAPH using count_tokens.
  2. Make the actual API call and print real usage from the response.
  3. Calculate the estimated cost in USD using the Sonnet 4.6 pricing
     from the module README ($3.00 / 1M input tokens, $15.00 / 1M output tokens).
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

# Sonnet 4.6 pricing (see module README)
INPUT_PRICE_PER_MILLION = 3.00
OUTPUT_PRICE_PER_MILLION = 15.00

SYSTEM_PROMPT = "You are a helpful assistant. Answer in one short paragraph."

USER_PARAGRAPH = (
    "Our team is evaluating whether to migrate our customer support chatbot "
    "from a rules-based system to an LLM-based one. We're concerned about "
    "cost predictability, response quality, and how to handle questions the "
    "model doesn't know the answer to. What should we consider first?"
)


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # TODO 1: count tokens before sending
    # count = client.messages.count_tokens(...)
    # print(f"Estimated input tokens: {count.input_tokens}")

    # TODO 2: make the real call and print response.usage
    # response = client.messages.create(...)
    # print(response.content[0].text)
    # print(response.usage)

    # TODO 3: calculate cost
    # input_cost = response.usage.input_tokens / 1_000_000 * INPUT_PRICE_PER_MILLION
    # output_cost = response.usage.output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MILLION
    # print(f"Estimated cost: ${input_cost + output_cost:.6f}")

    pass


if __name__ == "__main__":
    main()
