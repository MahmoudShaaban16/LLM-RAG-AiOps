"""
Exercise 2: Build a judge for a different task (summarization)

TODO:
  1. Fill in SUMMARY_EVAL_DATASET with 2-3 cases: each a short "text" to
     summarize, plus "criteria" describing a good summary.
  2. For each case, call the model to generate a summary.
  3. Define a JUDGE_SCHEMA + judge_summary function (similar to
     examples/02_llm_as_judge.py) that scores the summary against its
     criteria with a 1-5 score + reasoning, using tool_choice.
  4. Print the score and reasoning for each case.
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

# TODO: fill in 2-3 cases
SUMMARY_EVAL_DATASET = [
    # {
    #     "id": "case_1",
    #     "text": "<a short paragraph to summarize>",
    #     "criteria": [
    #         "Captures the main point in one sentence",
    #         "Does not exceed 25 words",
    #         "Does not include opinions not present in the source",
    #     ],
    # },
]

# TODO: define a tool schema for the judge's verdict (score 1-5 + reasoning)
JUDGE_SCHEMA = {
    "name": "record_judgment",
    "description": "TODO",
    "input_schema": {
        "type": "object",
        "properties": {
            # TODO: score, reasoning
        },
        "required": [],
    },
}


def summarize(client: Anthropic, text: str) -> str:
    # TODO: call client.messages.create asking the model to summarize `text`
    pass


def judge_summary(client: Anthropic, case: dict, summary: str) -> dict:
    # TODO: call client.messages.create with tools=[JUDGE_SCHEMA] and
    # tool_choice={"type": "tool", "name": "record_judgment"}, passing the
    # original text, the criteria, and the summary to evaluate.
    pass


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    for case in SUMMARY_EVAL_DATASET:
        summary = summarize(client, case["text"])
        verdict = judge_summary(client, case, summary)
        print(f"=== {case['id']} ===")
        print(f"Summary: {summary}")
        print(f"Score:   {verdict['score']}/5")
        print(f"Reason:  {verdict['reasoning']}")
        print()


if __name__ == "__main__":
    main()
