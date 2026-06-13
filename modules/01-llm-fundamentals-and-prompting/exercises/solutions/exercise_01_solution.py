"""
Solution: Exercise 1 - Estimate and verify token usage
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

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

    messages = [{"role": "user", "content": USER_PARAGRAPH}]

    # 1. Estimate input tokens before sending
    count = client.messages.count_tokens(
        model=MODEL,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    print(f"Estimated input tokens: {count.input_tokens}")

    # 2. Make the real call
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    print("\n--- response ---")
    print(response.content[0].text)

    print("\n--- actual usage ---")
    print(f"input tokens:  {response.usage.input_tokens}")
    print(f"output tokens: {response.usage.output_tokens}")

    # 3. Estimate cost
    input_cost = response.usage.input_tokens / 1_000_000 * INPUT_PRICE_PER_MILLION
    output_cost = response.usage.output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MILLION
    total_cost = input_cost + output_cost
    print(f"\nEstimated cost for this request: ${total_cost:.6f}")

    # Discussion:
    # - At 10,000 requests/day with similar token counts, monthly cost is
    #   roughly: total_cost * 10,000 * 30
    # - Switching to Haiku 4.5 ($1/$5 per million vs $3/$15) would cut this
    #   cost by roughly 3x, IF the quality bar is still met — always validate
    #   quality before optimizing for cost.
    daily_requests = 10_000
    days_per_month = 30
    monthly_cost = total_cost * daily_requests * days_per_month
    print(f"Projected monthly cost at {daily_requests:,} requests/day: ${monthly_cost:,.2f}")


if __name__ == "__main__":
    main()
