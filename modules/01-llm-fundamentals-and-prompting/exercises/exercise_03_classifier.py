"""
Exercise 3: Build a structured classifier

TODO:
  1. Define a tool schema "classify_feedback" with:
       - sentiment: "positive" | "neutral" | "negative"
       - topics: array of strings from {"pricing", "performance", "ui",
         "support", "reliability"}
       - requires_followup: boolean
  2. For each sample in SAMPLE_FEEDBACK, call the API with tool_choice
     forcing this tool, and print the structured result.
  3. Bonus: remove tool_choice and observe what changes.
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

SAMPLE_FEEDBACK = [
    "Your product is great but it's way too expensive for what it offers.",
    "The dashboard takes forever to load and sometimes just shows a blank screen.",
    "Support resolved my issue quickly, really happy with the experience!",
]

# TODO: define your tool schema here
CLASSIFY_FEEDBACK_SCHEMA = {
    "name": "classify_feedback",
    "description": "TODO",
    "input_schema": {
        "type": "object",
        "properties": {
            # TODO: sentiment, topics, requires_followup
        },
        "required": [],
    },
}


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    for feedback in SAMPLE_FEEDBACK:
        # TODO: call the API with tools=[CLASSIFY_FEEDBACK_SCHEMA] and
        # tool_choice={"type": "tool", "name": "classify_feedback"}
        # then print the tool_use block's `.input` as JSON
        pass


if __name__ == "__main__":
    main()
