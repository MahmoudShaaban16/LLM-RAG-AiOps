"""
Solution: Exercise 3 - Extend the fallback chain with a circuit breaker
"""

MODEL_FALLBACK_CHAIN = ["claude-sonnet-4-6", "claude-haiku-4-5"]

FAILURE_THRESHOLD = 3
COOLDOWN_REQUESTS = 5


class CircuitBreaker:
    """Tracks consecutive failures for the primary model and 'opens'
    (skips the primary) for COOLDOWN_REQUESTS calls once the failure
    threshold is reached."""

    def __init__(self, failure_threshold: int, cooldown_requests: int):
        self.failure_threshold = failure_threshold
        self.cooldown_requests = cooldown_requests
        self.consecutive_failures = 0
        self.cooldown_remaining = 0

    @property
    def is_open(self) -> bool:
        """True if the primary model should be skipped."""
        return self.cooldown_remaining > 0

    def record_success(self) -> None:
        self.consecutive_failures = 0

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.cooldown_remaining = self.cooldown_requests
            self.consecutive_failures = 0  # reset counter for next time

    def tick_cooldown(self) -> None:
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1


def simulate_call(model: str, should_fail: bool) -> str:
    if should_fail:
        raise RuntimeError(f"{model} unavailable")
    return f"response from {model}"


def main() -> None:
    # Primary model fails for the first 4 requests, then recovers.
    primary_fails = [True, True, True, True, False, False, False, False, False, False]

    breaker = CircuitBreaker(FAILURE_THRESHOLD, COOLDOWN_REQUESTS)
    primary, fallback = MODEL_FALLBACK_CHAIN

    for i, should_fail in enumerate(primary_fails):
        if breaker.is_open:
            # Circuit is open: skip the primary entirely, go straight to fallback.
            result = simulate_call(fallback, should_fail=False)
            served_by = fallback
            breaker.tick_cooldown()
            print(f"request {i}: circuit OPEN -> served by {served_by} ({result})")
            continue

        try:
            result = simulate_call(primary, should_fail)
            breaker.record_success()
            served_by = primary
            print(f"request {i}: served by {served_by} ({result})")
        except RuntimeError as e:
            breaker.record_failure()
            result = simulate_call(fallback, should_fail=False)
            served_by = fallback
            status = "circuit just OPENED" if breaker.is_open else "circuit closed"
            print(f"request {i}: primary failed ({e}) -> served by {served_by} [{status}]")


# Discussion:
# Skipping retries during a known outage matters for two reasons:
#   - Latency: every retry attempt against a failing primary model adds
#     real wall-clock delay (with backoff, often seconds) to a request that
#     will fail anyway -- multiplied across every user request during the
#     outage, this directly hurts user-perceived latency.
#   - Cost/load: depending on the failure mode, a "failed" request may still
#     consume rate-limit quota or partial processing on the provider side,
#     and it definitely consumes your own service's resources (threads,
#     connections, retry timers). A circuit breaker stops sending doomed
#     requests to a known-bad model, freeing capacity for the fallback and
#     reducing the chance that retries against an already-overloaded
#     endpoint make the outage worse (a "retry storm").
# The cooldown-then-retry-primary pattern lets the system self-heal once the
# primary recovers, without needing a human to manually flip a switch.


if __name__ == "__main__":
    main()
