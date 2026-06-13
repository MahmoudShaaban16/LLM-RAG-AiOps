"""
02 - Evaluate "Fine-Tuned" vs. Base (Conceptual)

We can't actually fine-tune a model in this example (Anthropic's
fine-tuning offerings are limited/enterprise-focused, and the point of
this module is the decision framework, not a training walkthrough).

Instead, this script simulates the *shape* of a base-vs-fine-tuned
comparison using two different system prompts against the same model:

  - "Model A" (base)        — a generic system prompt, no domain-specific
                               formatting guidance.
  - "Model B" (specialized) — a system prompt that encodes the exact
                               style/format a fine-tuned model would have
                               learned implicitly from training examples.

Both are run against the same eval set, then judged with the LLM-as-judge
pattern from Module 06 (examples/02_llm_as_judge.py). The output is a
side-by-side comparison report — exactly the kind of report you'd want
before promoting a fine-tuned model to production.
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

# "Model A" — base model, generic instructions. Stands in for "the base
# model with whatever prompt you have today."
SYSTEM_PROMPT_A = (
    "You are a support assistant. Help the user with their support ticket."
)

# "Model B" — specialized. Stands in for "what a fine-tuned model would
# produce by default, without needing this much prompting every call."
SYSTEM_PROMPT_B = (
    "You triage support tickets. Respond in EXACTLY this format, with no "
    "extra commentary:\n"
    "Category: <billing|bug|feature_request|account|other> | "
    "Urgency: <low|medium|high> | Action: <one short action>"
)

# The eval set: representative inputs + the properties a *good* response
# should have, regardless of which "model" produced it. Mirrors the shape
# of Module 06's EVAL_DATASET.
EVAL_DATASET = [
    {
        "id": "duplicate_charge",
        "input": "I was charged twice for my subscription this month.",
        "criteria": [
            "Identifies this as a billing issue",
            "Conveys appropriate urgency",
            "Is concise and actionable",
            "Follows the format: Category: ... | Urgency: ... | Action: ...",
        ],
    },
    {
        "id": "broken_export",
        "input": "The export button does nothing when I click it.",
        "criteria": [
            "Identifies this as a bug",
            "Conveys appropriate urgency",
            "Is concise and actionable",
            "Follows the format: Category: ... | Urgency: ... | Action: ...",
        ],
    },
    {
        "id": "feature_request",
        "input": "Can you add a dark mode to the dashboard?",
        "criteria": [
            "Identifies this as a feature request",
            "Conveys low urgency",
            "Is concise and actionable",
            "Follows the format: Category: ... | Urgency: ... | Action: ...",
        ],
    },
]

JUDGE_SYSTEM_PROMPT = (
    "You are a strict evaluator of AI assistant responses. You will be given "
    "a user question, a list of criteria the response should satisfy, and the "
    "response itself. Score how well the response meets ALL the criteria on a "
    "1-5 scale:\n"
    "  5 = fully meets every criterion\n"
    "  4 = meets all criteria with minor issues (e.g., slightly verbose)\n"
    "  3 = meets most criteria but misses or partially misses one\n"
    "  2 = meets some criteria but has a significant gap\n"
    "  1 = fails most or all criteria\n"
    "Be specific in your reasoning about which criteria were or were not met, "
    "especially formatting requirements."
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


def run_model(client: Anthropic, system_prompt: str, user_input: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=system_prompt,
        messages=[{"role": "user", "content": user_input}],
    )
    return response.content[0].text


def judge_response(client: Anthropic, case: dict, output: str) -> dict:
    criteria_text = "\n".join(f"- {c}" for c in case["criteria"])
    judge_prompt = (
        f"User question:\n{case['input']}\n\n"
        f"Criteria the response should satisfy:\n{criteria_text}\n\n"
        f"Response to evaluate:\n{output}"
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

    total_a, total_b = 0, 0
    n = 0

    for case in EVAL_DATASET:
        output_a = run_model(client, SYSTEM_PROMPT_A, case["input"])
        output_b = run_model(client, SYSTEM_PROMPT_B, case["input"])

        verdict_a = judge_response(client, case, output_a)
        verdict_b = judge_response(client, case, output_b)

        print(f"=== {case['id']} ===")
        print(f"Input: {case['input']}\n")

        print("--- Model A (base / generic prompt) ---")
        print(f"Output: {output_a}")
        print(f"Score:  {verdict_a['score']}/5")
        print(f"Reason: {verdict_a['reasoning']}\n")

        print("--- Model B (specialized prompt, stands in for fine-tuned) ---")
        print(f"Output: {output_b}")
        print(f"Score:  {verdict_b['score']}/5")
        print(f"Reason: {verdict_b['reasoning']}\n")

        if verdict_a["score"] is not None and verdict_b["score"] is not None:
            total_a += verdict_a["score"]
            total_b += verdict_b["score"]
            n += 1

    if n:
        print("=== Summary ===")
        print(f"Model A average score: {total_a / n:.2f}/5")
        print(f"Model B average score: {total_b / n:.2f}/5")
        print(
            "\nIn a real evaluation, 'Model B' would be your fine-tuned model "
            "and this report would be the evidence required before promoting "
            "it to production — including checking that it didn't regress on "
            "cases outside its specialized focus."
        )


if __name__ == "__main__":
    main()
