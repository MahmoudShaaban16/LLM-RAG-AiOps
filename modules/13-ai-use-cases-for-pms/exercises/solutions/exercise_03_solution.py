"""
Solution: Exercise 3 - Launch readiness check
"""

TARGETS = {
    "routing_accuracy": 0.90,
    "avg_coordinator_minutes": 2.0,
    "cost_per_lead": 0.02,
}

DIRECTIONS = {
    "routing_accuracy": "higher_is_better",
    "avg_coordinator_minutes": "lower_is_better",
    "cost_per_lead": "lower_is_better",
}

SHADOW_MODE_RESULTS_A = {
    "routing_accuracy": 0.93,
    "avg_coordinator_minutes": 1.5,
    "cost_per_lead": 0.015,
}

SHADOW_MODE_RESULTS_B = {
    "routing_accuracy": 0.87,
    "avg_coordinator_minutes": 1.8,
    "cost_per_lead": 0.018,
}


def check_readiness(results: dict, targets: dict) -> dict:
    readiness = {}
    for metric, target in targets.items():
        actual = results[metric]
        if DIRECTIONS[metric] == "higher_is_better":
            readiness[metric] = "PASS" if actual >= target else "FAIL"
        else:
            readiness[metric] = "PASS" if actual <= target else "FAIL"
    return readiness


def overall_decision(readiness: dict) -> str:
    return "GO" if all(status == "PASS" for status in readiness.values()) else "NO-GO"


def main() -> None:
    for label, results in (("A", SHADOW_MODE_RESULTS_A), ("B", SHADOW_MODE_RESULTS_B)):
        readiness = check_readiness(results, TARGETS)
        print(f"\n=== Shadow-mode results {label} ===")
        for metric, status in readiness.items():
            print(f"  {metric}: {results[metric]} (target {TARGETS[metric]}) -> {status}")
        print(f"  Decision: {overall_decision(readiness)}")

    # Discussion:
    # - Results A pass on every metric -> "GO": move from shadow mode to
    #   human-in-the-loop (README Section 7, Phase 1 -> 2).
    # - Results B fail only on routing_accuracy (87% vs. 90% target) ->
    #   overall "NO-GO", even though the other two metrics look good. This
    #   is the point of an all-or-nothing gate: a cost/time win doesn't
    #   compensate for a quality miss on the metric most tied to the
    #   *cost of error* (a misrouted lead). The fix is to extend shadow mode
    #   and improve the prompt/eval set (Module 06), not to ship anyway
    #   because two out of three metrics look good.


if __name__ == "__main__":
    main()
