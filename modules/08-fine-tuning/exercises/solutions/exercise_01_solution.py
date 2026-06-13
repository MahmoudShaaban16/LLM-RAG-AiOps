"""
Solution: Exercise 1 - Validate and format a training dataset
"""

import json
from pathlib import Path

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
    # Duplicate input (same as the first example) — flagged.
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
    # Missing output field.
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

    if "output" in example and isinstance(example["output"], str):
        if len(example["output"]) > MAX_OUTPUT_CHARS:
            errors.append(
                f"example {index}: 'output' is {len(example['output'])} chars, "
                f"exceeds the {MAX_OUTPUT_CHARS}-char style limit"
            )

    return errors


def validate_dataset(examples: list[dict]) -> tuple[list[dict], list[str]]:
    """Split examples into (valid, errors), including a duplicate-input check
    across the whole dataset."""
    valid_examples = []
    all_errors = []
    seen_inputs = set()

    for i, example in enumerate(examples):
        errors = validate_example(example, i)

        input_value = example.get("input")
        if input_value in seen_inputs:
            errors.append(f"example {i}: duplicate 'input' value (already seen earlier)")
        elif input_value is not None:
            seen_inputs.add(input_value)

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


def write_jsonl(examples: list[dict], system_prompt: str, path: Path) -> None:
    with open(path, "w") as f:
        for example in examples:
            record = to_messages_format(example, system_prompt)
            f.write(json.dumps(record) + "\n")


def main() -> None:
    system_prompt = (
        "You write one-sentence, customer-facing release notes from raw "
        "internal changelog entries. Always respond with exactly one "
        "sentence, in plain language, focused on the user-visible benefit."
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

    # Discussion: 3 out of 6 examples failed here — a duplicate, an
    # over-long output, and a missing field. That's a 50% failure rate on
    # a tiny sample. In a real dataset, that's a signal the *collection
    # process* is broken (e.g., copy-paste errors, no style guide given to
    # whoever wrote the outputs) — not just "throw away the bad rows and
    # move on." Fix the process, then re-collect.


if __name__ == "__main__":
    main()
