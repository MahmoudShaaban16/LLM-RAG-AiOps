"""
01 - Prompt Caching

Demonstrates Anthropic prompt caching: marking a large, unchanging block of
the system prompt with `cache_control: {"type": "ephemeral"}` so that
repeated requests reusing the same prefix can read from cache instead of
reprocessing it from scratch.

Run this script twice in a row (or run main() twice) to see:
  - First call: `cache_creation_input_tokens` > 0 (cache is written)
  - Second call: `cache_read_input_tokens` > 0 (cache is reused)

Note: this is illustrative of the documented cache_control content-block
shape and the `usage.cache_creation_input_tokens` / `usage.cache_read_input_tokens`
fields. Exact cache lifetimes, minimum cacheable token counts, and discount
rates change over time -- check https://docs.anthropic.com/ for current details.
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

# A large, stable block of context that's reused across many requests --
# e.g., a product policy document, a coding style guide, or a big set of
# few-shot examples. In a real app this might be several thousand tokens;
# it's kept short here for readability, but caching only "kicks in" above a
# minimum token threshold (check current docs for the exact number).
LARGE_SYSTEM_CONTEXT = """
You are a support assistant for 'Acme Cloud'. Use the following policy
reference for all answers:

REFUND POLICY: Monthly plans: full refund within 14 days of charge. Annual
plans: full refund within 30 days of charge. After the window, no refunds,
but customers may cancel to stop future charges.

DATA RETENTION POLICY: Account data is retained for 90 days after account
cancellation, after which it is permanently deleted. Customers can request
early deletion via a support ticket.

SLA: Enterprise customers receive a 99.9% uptime guarantee with service
credits for downtime exceeding the SLA, calculated monthly.

SUPPORT HOURS: Standard support is available Mon-Fri, 9am-6pm in the
customer's local time zone. Enterprise customers have 24/7 support access.

Answer customer questions in 2-3 sentences using only the information above.
""".strip()


def ask(client: Anthropic, question: str):
    """Send a request with the large context marked as cacheable."""
    return client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=[
            {
                "type": "text",
                "text": LARGE_SYSTEM_CONTEXT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": question}],
    )


def print_usage(label: str, response) -> None:
    usage = response.usage
    print(f"--- {label} ---")
    print(f"input_tokens:               {usage.input_tokens}")
    print(f"output_tokens:              {usage.output_tokens}")
    # These fields are only populated when cache_control is used.
    print(f"cache_creation_input_tokens: {getattr(usage, 'cache_creation_input_tokens', 0)}")
    print(f"cache_read_input_tokens:     {getattr(usage, 'cache_read_input_tokens', 0)}")
    print()


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # First call with this system prompt: the cache is created (written).
    response_1 = ask(client, "What's your refund policy for monthly plans?")
    print_usage("First call (expect cache_creation_input_tokens > 0)", response_1)
    print(response_1.content[0].text)
    print()

    # Second call, same cached prefix, different question: should read from
    # cache for the shared LARGE_SYSTEM_CONTEXT portion.
    response_2 = ask(client, "How long do you keep my data after I cancel?")
    print_usage("Second call (expect cache_read_input_tokens > 0)", response_2)
    print(response_2.content[0].text)


if __name__ == "__main__":
    main()
