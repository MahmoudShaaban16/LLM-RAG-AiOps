"""
Solution: Exercise 3 - Build a structured classifier
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

CLASSIFY_FEEDBACK_SCHEMA = {
    "name": "classify_feedback",
    "description": "Classify a piece of customer feedback.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "enum": ["positive", "neutral", "negative"],
            },
            "topics": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["pricing", "performance", "ui", "support", "reliability"],
                },
            },
            "requires_followup": {"type": "boolean"},
        },
        "required": ["sentiment", "topics", "requires_followup"],
    },
}


def classify(client: Anthropic, feedback: str, force_tool: bool = True) -> dict:
    kwargs = {
        "model": MODEL,
        "max_tokens": 300,
        "tools": [CLASSIFY_FEEDBACK_SCHEMA],
        "messages": [{"role": "user", "content": feedback}],
    }
    if force_tool:
        kwargs["tool_choice"] = {"type": "tool", "name": "classify_feedback"}

    response = client.messages.create(**kwargs)

    for block in response.content:
        if block.type == "tool_use" and block.name == "classify_feedback":
            return block.input

    return {"_note": "model did not call the tool", "raw": [b.type for b in response.content]}


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== With tool_choice forced ===")
    for feedback in SAMPLE_FEEDBACK:
        result = classify(client, feedback, force_tool=True)
        print(f"\nFeedback: {feedback}")
        print(json.dumps(result, indent=2))

    # Bonus: without tool_choice, the model decides whether to call the tool
    # at all. For a clear classification task it will usually still call it,
    # but for ambiguous or off-topic input it might reply with plain text
    # instead — so code that assumes a tool_use block will break. Forcing
    # tool_choice guarantees a parseable result, which matters when your
    # code depends on the structured output.
    print("\n=== Without tool_choice (model decides) ===")
    for feedback in SAMPLE_FEEDBACK:
        result = classify(client, feedback, force_tool=False)
        print(f"\nFeedback: {feedback}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
