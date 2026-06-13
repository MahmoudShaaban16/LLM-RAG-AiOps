"""
01 - Prepare Training Data

Fine-tuning APIs (across providers) typically consume JSONL — one JSON
object per line, each representing a single training example.

This script is purely data-prep: it takes a list of input/output examples,
validates them for consistency, and writes them out as JSONL. It does NOT
call any fine-tuning API — that's provider-specific and often
enterprise-only (see the module README).

A good training set is consistent (same schema every line), covers the
range of inputs you'll see in production, and is free of sensitive data.
"""

import json
from pathlib import Path

# Each example demonstrates the input/output behavior we'd want a
# fine-tuned model to reproduce consistently — here, a support-ticket
# triage assistant that always responds in a fixed, terse format.
RAW_EXAMPLES = [
    {
        "input": "I was charged twice for my subscription this month.",
        "output": "Category: billing | Urgency: high | Action: Refund duplicate charge.",
    },
    {
        "input": "The export button does nothing when I click it.",
        "output": "Category: bug | Urgency: medium | Action: Escalate to engineering with repro steps.",
    },
    {
        "input": "Can you add a dark mode to the dashboard?",
        "output": "Category: feature_request | Urgency: low | Action: Log to product backlog.",
    },
    {
        "input": "I can't log in, it says my password is wrong but I just reset it.",
        "output": "Category: account | Urgency: high | Action: Verify password reset flow, escalate if reproducible.",
    },
    {
        "input": "Just wanted to say the new update looks great!",
        "output": "Category: other | Urgency: low | Action: Forward to product team as positive feedback.",
    },
    # Intentionally malformed example to demonstrate validation catching it.
    {
        "input": "The app crashed during checkout.",
        # Missing "output" field.
    },
]

REQUIRED_FIELDS = {"input", "output"}

OUTPUT_PATH = Path(__file__).parent / "training_data.jsonl"


def validate_example(example: dict, index: int) -> list[str]:
    """Return a list of validation errors for a single example (empty if valid)."""
    errors = []

    missing = REQUIRED_FIELDS - example.keys()
    if missing:
        errors.append(f"example {index}: missing required field(s): {sorted(missing)}")
        return errors  # No point checking types if fields are missing.

    for field in REQUIRED_FIELDS:
        if not isinstance(example[field], str):
            errors.append(f"example {index}: field '{field}' must be a string")
        elif not example[field].strip():
            errors.append(f"example {index}: field '{field}' is empty")

    return errors


def validate_dataset(examples: list[dict]) -> tuple[list[dict], list[str]]:
    """Split examples into (valid, errors) — errors describe what's wrong with invalid ones."""
    valid_examples = []
    all_errors = []

    for i, example in enumerate(examples):
        errors = validate_example(example, i)
        if errors:
            all_errors.extend(errors)
        else:
            valid_examples.append(example)

    return valid_examples, all_errors


def to_messages_format(example: dict, system_prompt: str) -> dict:
    """Convert an input/output pair into the chat-messages JSONL shape
    used by many fine-tuning APIs (mirrors the Messages API format)."""
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": example["input"]},
            {"role": "assistant", "content": example["output"]},
        ]
    }


def write_jsonl(examples: list[dict], system_prompt: str, path: Path) -> None:
    with open(path, "w") as f:
        for example in examples:
            record = to_messages_format(example, system_prompt)
            f.write(json.dumps(record) + "\n")


def main() -> None:
    system_prompt = (
        "You triage support tickets. Respond in exactly this format: "
        "Category: <category> | Urgency: <low|medium|high> | Action: <one short action>."
    )

    valid_examples, errors = validate_dataset(RAW_EXAMPLES)

    print(f"Total examples: {len(RAW_EXAMPLES)}")
    print(f"Valid examples: {len(valid_examples)}")

    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"  - {error}")

    if not valid_examples:
        print("\nNo valid examples to write. Exiting.")
        return

    write_jsonl(valid_examples, system_prompt, OUTPUT_PATH)
    print(f"\nWrote {len(valid_examples)} examples to {OUTPUT_PATH}")

    # Show the first record so it's clear what the output format looks like.
    with open(OUTPUT_PATH) as f:
        first_line = f.readline()
    print("\n--- first record ---")
    print(json.dumps(json.loads(first_line), indent=2))


if __name__ == "__main__":
    main()
