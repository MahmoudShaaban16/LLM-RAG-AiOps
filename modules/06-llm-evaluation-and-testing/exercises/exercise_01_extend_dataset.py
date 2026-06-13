"""
Exercise 1: Extend the evaluation dataset

TODO:
  1. Add 3 new cases to EXTRA_CASES below:
       - one typical case
       - one edge case (boundary of the refund window)
       - one adversarial/off-policy case
     Each case needs: id, input, criteria (2-4 strings).
  2. Run all cases (the original dataset + your new ones) through the model
     and print the outputs.
"""

import os
from importlib import import_module

from anthropic import Anthropic

eval_dataset_module = import_module("01_eval_dataset")

MODEL = "claude-sonnet-4-6"
SYSTEM_PROMPT = eval_dataset_module.SYSTEM_PROMPT

# TODO: add your 3 new cases here
EXTRA_CASES = [
    # {
    #     "id": "your_case_id",
    #     "input": "...",
    #     "criteria": ["...", "..."],
    # },
]


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    all_cases = eval_dataset_module.EVAL_DATASET + EXTRA_CASES

    for case in all_cases:
        # TODO: call client.messages.create with SYSTEM_PROMPT and case["input"],
        # then print the case id, input, and output.
        pass


if __name__ == "__main__":
    main()
