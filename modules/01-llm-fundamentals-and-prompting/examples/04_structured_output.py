"""
04 - Structured Output

Demonstrates getting reliable, parseable JSON out of the model by
defining a tool with a strict input schema and forcing the model to
call it. This avoids the common failure mode of parsing free-text
responses (extra prose, inconsistent formatting, etc.).
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

# Define the shape of the data we want back as a tool input schema.
TICKET_SCHEMA = {
    "name": "extract_ticket_info",
    "description": "Extract structured information from a support ticket.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "One-sentence summary of the issue.",
            },
            "category": {
                "type": "string",
                "enum": ["billing", "bug", "feature_request", "account", "other"],
            },
            "urgency": {
                "type": "string",
                "enum": ["low", "medium", "high"],
            },
        },
        "required": ["summary", "category", "urgency"],
    },
}

SAMPLE_TICKET = (
    "I was charged twice for my subscription this month. Can someone refund "
    "the duplicate charge? This is pretty urgent since it's a large amount."
)


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        tools=[TICKET_SCHEMA],
        # Force the model to use this tool rather than replying in plain text.
        tool_choice={"type": "tool", "name": "extract_ticket_info"},
        messages=[{"role": "user", "content": SAMPLE_TICKET}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_ticket_info":
            print(json.dumps(block.input, indent=2))


if __name__ == "__main__":
    main()
