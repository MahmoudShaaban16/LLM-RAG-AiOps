"""
Exercise 3: Launch readiness check

A "launch readiness" check turns the success-metrics section of the
one-pager (README Section 6) into a go/no-go gate: before moving from
shadow mode to human-in-the-loop (or beyond), every metric with a target
must meet that target.

TODO:
  1. Implement `check_readiness(results, targets)` which compares each
     metric in `results` against the corresponding entry in `targets` and
     returns a dict mapping metric name -> "PASS" or "FAIL". A metric
     passes if it meets the target in the *favorable* direction given by
     `DIRECTIONS` (e.g., "higher_is_better" or "lower_is_better").
  2. Implement `overall_decision(readiness)` which returns "GO" if every
     metric passed, otherwise "NO-GO".
  3. Run this script for both SHADOW_MODE_RESULTS_A and
     SHADOW_MODE_RESULTS_B and print the per-metric results and overall
     decision for each.

No API key required - this is comparison logic over example metric values.
"""

# Targets from a one-pager's Section 3 (Success metrics), and which
# direction is "good" for each.
TARGETS = {
    "routing_accuracy": 0.90,        # fraction, e.g. 0.92 = 92%
    "avg_coordinator_minutes": 2.0,  # minutes per lead
    "cost_per_lead": 0.02,           # dollars
}

DIRECTIONS = {
    "routing_accuracy": "higher_is_better",
    "avg_coordinator_minutes": "lower_is_better",
    "cost_per_lead": "lower_is_better",
}

# Two weeks of shadow-mode results to evaluate.
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
    # TODO: for each metric in `targets`, compare results[metric] against
    # targets[metric] using DIRECTIONS[metric], and return
    # {metric_name: "PASS" or "FAIL"}.
    pass


def overall_decision(readiness: dict) -> str:
    # TODO: return "GO" if all values in `readiness` are "PASS", else "NO-GO"
    pass


def main() -> None:
    for label, results in (("A", SHADOW_MODE_RESULTS_A), ("B", SHADOW_MODE_RESULTS_B)):
        readiness = check_readiness(results, TARGETS)
        print(f"\n=== Shadow-mode results {label} ===")
        if readiness is None:
            print("  (check_readiness not implemented yet)")
            continue
        for metric, status in readiness.items():
            print(f"  {metric}: {results[metric]} (target {TARGETS[metric]}) -> {status}")
        print(f"  Decision: {overall_decision(readiness)}")


if __name__ == "__main__":
    main()
