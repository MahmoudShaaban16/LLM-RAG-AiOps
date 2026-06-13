"""
03 - Prompting Techniques

Compares a vague prompt to a well-structured one, and demonstrates
few-shot examples for consistent output formatting.
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"


def vague_prompt(client: Anthropic) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": "Summarize this: " + SAMPLE_TICKET}],
    )
    return response.content[0].text


def well_structured_prompt(client: Anthropic) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=(
            "You summarize customer support tickets for a non-technical manager. "
            "Rules: respond in exactly 2 sentences, no jargon, and never include "
            "names, emails, or other personal information."
        ),
        messages=[{"role": "user", "content": SAMPLE_TICKET}],
    )
    return response.content[0].text


def few_shot_prompt(client: Anthropic) -> str:
    """Few-shot examples steer the model toward a specific output format."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system="Classify the sentiment of a support ticket. Respond with only one word: positive, neutral, or negative.",
        messages=[
            {"role": "user", "content": "My order arrived a day early, thanks!"},
            {"role": "assistant", "content": "positive"},
            {"role": "user", "content": "The app crashes every time I open settings."},
            {"role": "assistant", "content": "negative"},
            {"role": "user", "content": SAMPLE_TICKET},
        ],
    )
    return response.content[0].text


SAMPLE_TICKET = (
    "Hi, this is John Smith (john.smith@example.com). I've been trying to export "
    "my report to CSV for the last hour and it keeps timing out at 90%. "
    "This is blocking our end-of-month reporting, please help ASAP."
)


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== Vague prompt ===")
    print(vague_prompt(client))

    print("\n=== Well-structured prompt (system prompt + constraints) ===")
    print(well_structured_prompt(client))

    print("\n=== Few-shot classification ===")
    print(few_shot_prompt(client))


if __name__ == "__main__":
    main()
