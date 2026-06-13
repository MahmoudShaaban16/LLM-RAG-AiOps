"""
02 - LLM-as-Judge

Uses a second Claude call (the "judge") to score the outputs produced by
01_eval_dataset.py against each case's expected criteria. The judge returns
a structured verdict (score 1-5 + reasoning) via tool_choice, following the
same structured-output pattern as Module 01's examples/04_structured_output.py.
"""

import json
import os

from anthropic import Anthropic

from importlib import import_module

# Reuse the dataset + runner from 01_eval_dataset.py
eval_dataset_module = import_module("01_eval_dataset")

MODEL = "claude-sonnet-4-6"

JUDGE_SYSTEM_PROMPT = (
    "You are a strict evaluator of AI assistant responses. You will be given "
    "a user question, a list of criteria the response should satisfy, and the "
    "response itself. Score how well the response meets ALL the criteria on a "
    "1-5 scale:\n"
    "  5 = fully meets every criterion\n"
    "  4 = meets all criteria with minor issues (e.g., slightly verbose)\n"
    "  3 = meets most criteria but misses or partially misses one\n"
    "  2 = meets some criteria but has a significant gap (e.g., invents a fact)\n"
    "  1 = fails most or all criteria\n"
    "Be specific in your reasoning about which criteria were or were not met."
)

JUDGE_SCHEMA = {
    "name": "record_judgment",
    "description": "Record a quality score and reasoning for an AI response.",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {
                "type": "integer",
                "description": "Overall quality score from 1 (worst) to 5 (best).",
                "minimum": 1,
                "maximum": 5,
            },
            "reasoning": {
                "type": "string",
                "description": "Brief explanation referencing which criteria were met or missed.",
            },
        },
        "required": ["score", "reasoning"],
    },
}


def judge_response(client: Anthropic, case: dict) -> dict:
    """Score a single (input, output, criteria) case using the judge model."""
    criteria_text = "\n".join(f"- {c}" for c in case["criteria"])
    judge_prompt = (
        f"User question:\n{case['input']}\n\n"
        f"Criteria the response should satisfy:\n{criteria_text}\n\n"
        f"Response to evaluate:\n{case['output']}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=JUDGE_SYSTEM_PROMPT,
        tools=[JUDGE_SCHEMA],
        tool_choice={"type": "tool", "name": "record_judgment"},
        messages=[{"role": "user", "content": judge_prompt}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "record_judgment":
            return block.input

    return {"score": None, "reasoning": "judge did not return a verdict"}


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Step 1: generate outputs for each eval case
    results = eval_dataset_module.run_eval_inputs(client)

    # Step 2: judge each output against its criteria
    for r in results:
        verdict = judge_response(client, r)
        print(f"=== {r['id']} ===")
        print(f"Input:  {r['input']}")
        print(f"Output: {r['output']}")
        print(f"Score:  {verdict['score']}/5")
        print(f"Reason: {verdict['reasoning']}")
        print()


if __name__ == "__main__":
    main()
