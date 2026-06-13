"""
03 - Fallback and Retry

Demonstrates two resilience patterns for production LLM calls, using only
the Python standard library:

  1. Retry with exponential backoff for transient errors (rate limits,
     timeouts, server errors).
  2. A model fallback chain: if the primary model call fails after retries,
     fall back to a different (e.g., cheaper/faster) model rather than
     failing the whole request.
"""

import os
import random
import time

import anthropic
from anthropic import Anthropic

# Fallback chain, from primary to last resort.
MODEL_FALLBACK_CHAIN = ["claude-sonnet-4-6", "claude-haiku-4-5"]

MAX_RETRIES = 3
BASE_DELAY_SECONDS = 1.0

# Errors worth retrying: rate limits, transient server errors, and
# connection/timeout issues. 4xx errors other than 429 (e.g., invalid
# request, auth failure) are not retryable -- retrying them just wastes
# time and money without changing the outcome.
RETRYABLE_EXCEPTIONS = (
    anthropic.RateLimitError,
    anthropic.APIConnectionError,
    anthropic.APITimeoutError,
    anthropic.InternalServerError,
)


def call_with_retry(client: Anthropic, model: str, **kwargs):
    """Call messages.create with exponential backoff + jitter on retryable errors."""
    for attempt in range(MAX_RETRIES):
        try:
            return client.messages.create(model=model, **kwargs)
        except RETRYABLE_EXCEPTIONS as e:
            if attempt == MAX_RETRIES - 1:
                raise
            delay = BASE_DELAY_SECONDS * (2 ** attempt) + random.uniform(0, 0.5)
            print(f"  [{model}] {type(e).__name__} on attempt {attempt + 1}, "
                  f"retrying in {delay:.1f}s...")
            time.sleep(delay)


def call_with_fallback(client: Anthropic, **kwargs):
    """
    Try each model in MODEL_FALLBACK_CHAIN in order, with retries on each.
    Returns the first successful response, along with which model served it.
    """
    last_error = None

    for model in MODEL_FALLBACK_CHAIN:
        try:
            print(f"Trying model: {model}")
            response = call_with_retry(client, model, **kwargs)
            return response, model
        except RETRYABLE_EXCEPTIONS as e:
            print(f"  [{model}] failed after retries: {type(e).__name__}")
            last_error = e
            continue

    # Every model in the chain failed.
    raise RuntimeError(
        f"All models in fallback chain failed. Last error: {last_error}"
    )


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response, served_by = call_with_fallback(
        client,
        max_tokens=200,
        messages=[{"role": "user", "content": "Give me one tip for writing clear API docs."}],
    )

    print(f"\nServed by: {served_by}")
    print(response.content[0].text)
    print(f"\nusage: input={response.usage.input_tokens}, output={response.usage.output_tokens}")


if __name__ == "__main__":
    main()
