"""
Exercise 1: Validate and format a training dataset

TODO:
  1. Extend validation to also check:
       - No duplicate `input` values across the dataset
       - `output` is <= 200 characters
  2. Run validation and report valid vs. invalid examples (with reasons).
  3. Write the valid examples to JSONL in the `messages` format (see
     examples/01_prepare_training_data.py for the conversion helper),
     using a system prompt you write describing the desired style.
"""

import json
from pathlib import Path

# Raw examples for a "release notes summarizer": turn a raw changelog entry
# into a single customer-facing sentence.
RAW_EXAMPLES = [
    {
        "input": "Fixed a bug where the export button was unresponsive on Safari.",
        "output": "Exporting now works reliably in Safari.",
    },
    {
        "input": "Added support for dark mode across the dashboard.",
        "output": "You can now switch the dashboard to dark mode.",
    },
    {
        "input": "Improved query performance for large datasets by 40%.",
        "output": "Reports on large datasets now load significantly faster.",
    },
    # Duplicate input (same as the first example) — should be flagged.
    {
        "input": "Fixed a bug where the export button was unresponsive on Safari.",
        "output": "Export issues on Safari are resolved.",
    },
    # Output far too long for a "single sentence" style dataset.
    {
        "input": "Migrated the billing backend to a new provider.",
        "output": (
            "We have completed a major migration of our billing infrastructure "
            "to a new provider, which involved months of planning, extensive "
            "testing, and a phased rollout to ensure no disruption to existing "
            "customers during the transition period."
        ),
    },
    # Missing output field — should be caught by the existing validation.
    {
        "input": "Removed the legacy reporting API.",
    },
]

REQUIRED_FIELDS = {"input", "output"}
MAX_OUTPUT_CHARS = 200

OUTPUT_PATH = Path(__file__).parent / "release_notes_training_data.jsonl"


def validate_example(example: dict, index: int) -> list[str]:
    """Return a list of validation errors for a single example (empty if valid)."""
    errors = []

    missing = REQUIRED_FIELDS - example.keys()
    if missing:
        errors.append(f"example {index}: missing required field(s): {sorted(missing)}")
        return errors

    for field in REQUIRED_FIELDS:
        if not isinstance(example[field], str):
            errors.append(f"example {index}: field '{field}' must be a string")
        elif not example[field].strip():
            errors.append(f"example {index}: field '{field}' is empty")

    # TODO: check len(example["output"]) <= MAX_OUTPUT_CHARS

    return errors


def validate_dataset(examples: list[dict]) -> tuple[list[dict], list[str]]:
    """Split examples into (valid, errors)."""
    valid_examples = []
    all_errors = []

    # TODO: track seen `input` values to detect duplicates across the
    # whole dataset (not just within a single example).

    for i, example in enumerate(examples):
        errors = validate_example(example, i)
        if errors:
            all_errors.extend(errors)
        else:
            valid_examples.append(example)

    return valid_examples, all_errors


def to_messages_format(example: dict, system_prompt: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": example["input"]},
            {"role": "assistant", "content": example["output"]},
        ]
    }


def main() -> None:
    # TODO: write a system prompt describing the desired style
    system_prompt = "TODO"

    valid_examples, errors = validate_dataset(RAW_EXAMPLES)

    print(f"Total examples: {len(RAW_EXAMPLES)}")
    print(f"Valid examples: {len(valid_examples)}")

    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"  - {error}")

    # TODO: write valid_examples to OUTPUT_PATH as JSONL using
    # to_messages_format()


if __name__ == "__main__":
    main()
