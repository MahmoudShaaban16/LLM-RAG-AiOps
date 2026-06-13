"""
Solution: Exercise 2 - Make the cached prefix actually stable
"""

import os
import time
from datetime import datetime

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

POLICY_TEXT = """
REFUND POLICY: Monthly plans: full refund within 14 days of charge. Annual
plans: full refund within 30 days of charge. After the window, no refunds,
but customers may cancel to stop future charges.
""".strip()


def buggy_system_context() -> str:
    """BUG: embeds the current time directly in the cached block, so the
    text is different on every call -- the cache can never be reused."""
    return f"{POLICY_TEXT}\nCurrent time: {datetime.now().isoformat()}"


# FIXED: the cached block is now fully static. Any dynamic content (like a
# timestamp) should go in a separate, non-cached part of the request --
# e.g., appended to the user message -- not in the cached system block.
FIXED_SYSTEM_CONTEXT = POLICY_TEXT


def ask_with_cached_system(client: Anthropic, system_text: str, question: str):
    return client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": system_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": question}],
    )


def print_usage(label: str, response) -> None:
    usage = response.usage
    print(f"{label}: cache_creation={getattr(usage, 'cache_creation_input_tokens', 0)} "
          f"cache_read={getattr(usage, 'cache_read_input_tokens', 0)}")


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== Buggy: timestamp embedded in cached block ===")
    r1 = ask_with_cached_system(client, buggy_system_context(), "What's the refund window for annual plans?")
    print_usage("Call 1", r1)
    time.sleep(2)
    r2 = ask_with_cached_system(client, buggy_system_context(), "Can I cancel after the refund window?")
    print_usage("Call 2", r2)
    print("-> Expect cache_read_input_tokens == 0 on both calls: each call's "
          "cached text differs (different timestamp), so nothing is reused.\n")

    print("=== Fixed: static cached block ===")
    r3 = ask_with_cached_system(client, FIXED_SYSTEM_CONTEXT, "What's the refund window for annual plans?")
    print_usage("Call 1", r3)
    time.sleep(2)
    r4 = ask_with_cached_system(client, FIXED_SYSTEM_CONTEXT, "Can I cancel after the refund window?")
    print_usage("Call 2", r4)
    print("-> Expect cache_read_input_tokens > 0 on call 2: the cached "
          "block is byte-for-byte identical to call 1.")


if __name__ == "__main__":
    main()
