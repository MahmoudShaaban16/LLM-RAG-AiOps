"""
Exercise 3: Add a guardrail for the suggested response

TODO:
  1. Implement `validate_suggested_response(triage_result)` which checks the
     `suggested_response` text for anything that looks like a system prompt
     leak (e.g., contains the literal words "system prompt" or
     "<untrusted_input>").
  2. If found, set `needs_human_review = True` and append a note to the
     result explaining why (e.g. under a "guardrail_notes" key).
  3. Run this guardrail on the result for the third sample ticket (the one
     with the prompt injection attempt) and confirm it flags correctly.

Run this file from the `examples/capstone_app/` directory (or adjust the
import path) so the import below resolves.
"""

import json
import os

from anthropic import Anthropic

from main import SAMPLE_TICKETS, triage_ticket  # type: ignore


def validate_suggested_response(triage_result: dict) -> dict:
    # TODO: implement the checks described above and return the
    # (possibly modified) triage_result.
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
