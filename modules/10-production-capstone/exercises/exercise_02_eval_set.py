"""
Exercise 2: Build an eval set for the triage assistant

TODO:
  1. Write 5 sample tickets covering different categories (account, billing,
     order, technical, other) with an *expected* category and urgency for each.
  2. Run each through `triage_ticket` (imported from the capstone app).
  3. Check whether the model's `category` and `urgency` match your
     expectations, and print a pass/fail summary.

This reuses `triage_ticket` from ../../examples/capstone_app/main.py. Run
this file from the `examples/capstone_app/` directory (or adjust the import
path) so the import below resolves.
"""

import json
import os

from anthropic import Anthropic

# Import the pipeline under test.
from main import triage_ticket  # type: ignore


# TODO 1: fill in 5 tickets with expected category/urgency.
EVAL_CASES = [
    {
        "ticket": "I can't export my report to CSV, the export button does nothing.",
        "expected_category": "technical",
        "expected_urgency": "low",
    },
    # Add 4 more cases covering account, billing, order, and "other".
]


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    passed = 0
    for case in EVAL_CASES:
        # TODO 2: run the ticket through triage_ticket
        result = triage_ticket(client, case["ticket"])

        # TODO 3: compare result["category"] / result["urgency"] against
        # case["expected_category"] / case["expected_urgency"], print
        # pass/fail, and tally `passed`.
        print(json.dumps(result, indent=2))

    print(f"\n{passed}/{len(EVAL_CASES)} passed")


if __name__ == "__main__":
    main()
