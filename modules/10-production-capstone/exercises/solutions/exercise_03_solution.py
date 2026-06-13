"""
Solution: Exercise 3 - Add a guardrail for the suggested response

Run from modules/10-production-capstone/examples/capstone_app/, e.g.:

    cd modules/10-production-capstone/examples/capstone_app
    python ../../exercises/solutions/exercise_03_solution.py
"""

import json
import os

from anthropic import Anthropic

from main import SAMPLE_TICKETS, triage_ticket  # type: ignore


LEAK_INDICATORS = [
    "system prompt",
    "<untrusted_input>",
    "</untrusted_input>",
]


def validate_suggested_response(triage_result: dict) -> dict:
    """Flag suggested responses that look like they leak internal prompt details."""
    suggested = triage_result.get("suggested_response", "") or ""
    suggested_lower = suggested.lower()

    found = [indicator for indicator in LEAK_INDICATORS if indicator.lower() in suggested_lower]

    if found:
        triage_result["needs_human_review"] = True
        note = (
            "Guardrail: suggested_response appears to reference internal "
            f"prompt details ({', '.join(found)}). Flagged for human review."
        )
        notes = triage_result.setdefault("guardrail_notes", [])
        notes.append(note)

    return triage_result


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # The third sample ticket contains the prompt injection attempt.
    ticket = SAMPLE_TICKETS[2]
    result = triage_ticket(client, ticket)
    print("Raw result:")
    print(json.dumps(result, indent=2))

    guarded = validate_suggested_response(result)
    print("\nAfter guardrail:")
    print(json.dumps(guarded, indent=2))


if __name__ == "__main__":
    main()


# Bonus discussion: input guardrail vs. output guardrail
#
# - The <untrusted_input> wrapping (Module 09) is an *input* guardrail: it
#   tries to prevent the model from ever treating ticket/article text as
#   instructions in the first place.
# - validate_suggested_response is an *output* guardrail: it checks the
#   model's final answer for signs that something went wrong anyway.
#
# Why have both? Input guardrails reduce the *likelihood* of an attack
# succeeding, but prompt injection defenses are not 100% reliable - a
# sufficiently creative attacker may still get the model to leak something.
# Output guardrails act as a safety net: even if the input defense is
# bypassed, a bad response gets caught (and routed to a human) before it
# reaches the customer. Defense in depth - neither layer alone is sufficient.
