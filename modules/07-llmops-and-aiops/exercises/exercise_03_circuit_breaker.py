"""
Exercise 3: Extend the fallback chain with a circuit breaker

TODO:
  1. Track consecutive failures for the primary model in a module-level
     dict or small class (CircuitBreaker).
  2. If consecutive failures >= FAILURE_THRESHOLD, skip the primary model
     entirely and go straight to the fallback for COOLDOWN_REQUESTS calls.
  3. Use simulate_call() below (which can be told to "fail") instead of a
     real API call, and print which model serves each of ~10 requests.
"""

import random

MODEL_FALLBACK_CHAIN = ["claude-sonnet-4-6", "claude-haiku-4-5"]

FAILURE_THRESHOLD = 3
COOLDOWN_REQUESTS = 5


def simulate_call(model: str, should_fail: bool) -> str:
    """Pretend to call `model`; raise if should_fail is True."""
    if should_fail:
        raise RuntimeError(f"{model} unavailable")
    return f"response from {model}"


def main() -> None:
    # Simulate an outage: the primary model fails for the first 4 requests,
    # then recovers.
    primary_fails = [True, True, True, True, False, False, False, False, False, False]

    # TODO: implement the circuit breaker logic here.
    # For each request i in range(10):
    #   - decide which model to try first (primary, unless the breaker is
    #     "open" due to FAILURE_THRESHOLD consecutive failures and we're
    #     still within the cooldown window)
    #   - call simulate_call(); on failure, increment the consecutive
    #     failure counter and fall back to the next model in the chain
    #   - on success, reset the consecutive failure counter
    #   - print which model served request i

    for i in range(10):
        # placeholder: replace with circuit-breaker-aware logic
        pass


if __name__ == "__main__":
    main()
