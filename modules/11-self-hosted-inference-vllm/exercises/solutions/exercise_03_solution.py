"""
Solution: Exercise 3 - Eval-gate a self-hosting migration
"""

# 1. The eval gate (Module 06 pattern applied to a self-hosting migration):
#
#    EVAL_DATASET (representative tickets, with expected category)
#        |--> run through OLD pipeline (Anthropic API)   --> outputs_old
#        |--> run through NEW pipeline (self-hosted vLLM) --> outputs_new
#
#    Score both sets of outputs with the SAME judge/rubric (or, for a
#    classification field like `category`, exact-match accuracy against the
#    expected label).
#
#    A regression = the new model's average score drops by more than an
#    acceptable `threshold` vs. the old model - not just "any" drop, since
#    LLM outputs (and judge scores) have natural variance. Always check
#    per-case deltas too, not just the average (Module 06) - a migration
#    that's fine "on average" but breaks one common ticket type is still a
#    problem worth catching before cutover.


def should_migrate(old_scores: list[float], new_scores: list[float], threshold: float) -> bool:
    old_avg = sum(old_scores) / len(old_scores)
    new_avg = sum(new_scores) / len(new_scores)
    return new_avg >= old_avg - threshold


def main() -> None:
    old_scores = [4.5, 4.0, 4.8, 3.9, 4.2]
    new_scores_ok = [4.3, 4.1, 4.6, 3.8, 4.0]
    new_scores_regressed = [3.0, 2.5, 3.2, 2.8, 2.9]

    threshold = 0.3

    print(f"old avg: {sum(old_scores) / len(old_scores):.2f}")
    print(f"new (ok) avg: {sum(new_scores_ok) / len(new_scores_ok):.2f}")
    print(f"new (regressed) avg: {sum(new_scores_regressed) / len(new_scores_regressed):.2f}")
    print()

    print(f"should_migrate (ok case): {should_migrate(old_scores, new_scores_ok, threshold)}")
    print(f"should_migrate (regressed case): {should_migrate(old_scores, new_scores_regressed, threshold)}")


if __name__ == "__main__":
    main()


# Bonus discussion: even with a passing eval gate, before cutting over
# production traffic you'd also want:
#
# - A fallback chain (Module 07): if the self-hosted vLLM server is
#   unreachable (GPU node down, server restart), fall back to the Anthropic
#   API rather than failing the request outright - the exact failure mode
#   the module README calls out as new with self-hosting.
# - Observability (Module 07) on the new server: token usage, latency, and
#   cost logging, same as you had "for free" with the managed API.
# - A staged rollout (e.g., shadow traffic or a small percentage of real
#   traffic first) rather than a full cutover, so a problem the eval set
#   didn't catch shows up on a small slice of traffic, not all of it.
# - A rollback plan: switching the client-side wrapper back to the
#   Anthropic API should be a config change, not a code change.
