"""
Exercise 2: Make the cached prefix actually stable

TODO:
  1. Write BUGGY_SYSTEM_CONTEXT: like LARGE_SYSTEM_CONTEXT in
     examples/01_prompt_caching.py, but with an f-string embedding
     datetime.now() directly in the cached text block.
  2. Make two calls using BUGGY_SYSTEM_CONTEXT (a few seconds apart) and
     print cache_creation_input_tokens / cache_read_input_tokens for both.
     Confirm the cache is never reused.
  3. Write FIXED_SYSTEM_CONTEXT with the timestamp removed (or moved to a
     separate non-cached block / the user message), and re-run to confirm
     the second call now shows cache_read_input_tokens > 0.
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

# TODO: embed datetime.now() directly into this cached text block (the bug).
BUGGY_SYSTEM_CONTEXT = None  # f"{POLICY_TEXT}\nCurrent time: {datetime.now()}"

# TODO: a version without the dynamic timestamp in the cached block.
FIXED_SYSTEM_CONTEXT = None  # POLICY_TEXT


def ask(client: Anthropic, system_text: str, question: str):
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

    # TODO: two calls with BUGGY_SYSTEM_CONTEXT
    # TODO: two calls with FIXED_SYSTEM_CONTEXT
    pass


if __name__ == "__main__":
    main()
