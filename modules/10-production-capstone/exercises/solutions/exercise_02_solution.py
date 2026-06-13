"""
Solution: Exercise 2 - Build an eval set for the triage assistant

Run from modules/10-production-capstone/examples/capstone_app/, e.g.:

    cd modules/10-production-capstone/examples/capstone_app
    python ../../exercises/solutions/exercise_02_solution.py
"""

import json
import os

from anthropic import Anthropic

from main import triage_ticket  # type: ignore


EVAL_CASES = [
    {
        "ticket": "I can't export my report to CSV, the export button does nothing.",
        "expected_category": "technical",
        "expected_urgency": "low",
    },
    {
        "ticket": "Where is my order ORD-5678? It's been over a week and I'm worried it's lost.",
        "expected_category": "order",
        "expected_urgency": "medium",
    },
    {
        "ticket": "I was charged twice for my subscription this month, please refund the duplicate charge.",
        "expected_category": "billing",
        "expected_urgency": "high",
    },
    {
        "ticket": "I forgot my password and the reset email never arrived. Can you help me get back into my account?",
        "expected_category": "account",
        "expected_urgency": "medium",
    },
    {
        "ticket": "Just wanted to say I love the new dashboard redesign, great work!",
        "expected_category": "other",
        "expected_urgency": "low",
    },
]


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    passed = 0
    for case in EVAL_CASES:
        result = triage_ticket(client, case["ticket"])

        category_match = result.get("category") == case["expected_category"]
        urgency_match = result.get("urgency") == case["expected_urgency"]
        ok = category_match and urgency_match

        print("=" * 70)
        print(f"Ticket: {case['ticket']}")
        print(json.dumps(result, indent=2))
        print(
            f"Expected category={case['expected_category']!r}, "
            f"urgency={case['expected_urgency']!r}"
        )

        # Discussion question: if the model sets needs_human_review=True but
        # our expected urgency is "low", is that a failure?
        #
        # We treat it as a soft pass (not a hard failure): the model erring
        # toward caution is generally acceptable behavior, even if it doesn't
        # match our expectation exactly. We still print a note so a human can
        # review whether the assistant is being *too* cautious on this kind
        # of ticket (which would hurt customer experience at scale).
        if not urgency_match and result.get("needs_human_review") and case["expected_urgency"] == "low":
            print("NOTE: urgency mismatch, but model flagged for human review - treating as soft pass.")
            urgency_match = True
            ok = category_match and urgency_match

        print("PASS" if ok else "FAIL")
        if ok:
            passed += 1

    print(f"\n{passed}/{len(EVAL_CASES)} passed")


if __name__ == "__main__":
    main()
