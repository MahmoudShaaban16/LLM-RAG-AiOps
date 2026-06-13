"""
01 - Eval Dataset

Defines a small evaluation dataset: representative inputs paired with
expected *properties* of a good response (not exact-match strings), then
runs each input through the model and prints the output.

This is the raw material that 02_llm_as_judge.py and
03_prompt_regression_test.py build on.
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = (
    "You are a support assistant for a SaaS product called 'Acme Cloud'. "
    "Acme Cloud's refund policy: customers on monthly plans can request a "
    "full refund within 14 days of charge; annual plans within 30 days. "
    "After that window, no refunds are issued, but customers can cancel "
    "to stop future charges. Answer customer questions in 2-4 sentences, "
    "using only the policy information given above."
)

# Each case: a representative input + the properties a good answer should have.
# These criteria are checked by the LLM-as-judge in 02_llm_as_judge.py.
EVAL_DATASET = [
    {
        "id": "refund_within_window",
        "input": "I'm on the monthly plan and was charged 5 days ago. Can I get a refund?",
        "criteria": [
            "States that a refund is possible",
            "References the 14-day window for monthly plans",
            "Does not invent details not in the policy",
        ],
    },
    {
        "id": "refund_outside_window",
        "input": "I bought the annual plan 2 months ago. Can I still get a refund?",
        "criteria": [
            "States that a refund is NOT possible (outside the 30-day window)",
            "Mentions the option to cancel to stop future charges",
            "Does not invent details not in the policy",
        ],
    },
    {
        "id": "ambiguous_plan_type",
        "input": "I want my money back, I only used the product for a week.",
        "criteria": [
            "Asks or accounts for the fact that the policy differs by plan type "
            "(monthly vs. annual)",
            "Does not assume a refund is guaranteed without knowing the plan type",
            "Is helpful and concise (2-4 sentences)",
        ],
    },
    {
        "id": "off_policy_question",
        "input": "Can you also process refunds for my gym membership?",
        "criteria": [
            "Politely declines / clarifies this is out of scope",
            "Does not invent a gym refund policy",
            "Stays on-topic for Acme Cloud support",
        ],
    },
]


def run_eval_inputs(client: Anthropic) -> list[dict]:
    """Run every eval case through the model and collect the outputs."""
    results = []
    for case in EVAL_DATASET:
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": case["input"]}],
        )
        output = response.content[0].text
        results.append({**case, "output": output})
    return results


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    results = run_eval_inputs(client)

    for r in results:
        print(f"=== {r['id']} ===")
        print(f"Input:    {r['input']}")
        print(f"Output:   {r['output']}")
        print(f"Criteria: {r['criteria']}")
        print()


if __name__ == "__main__":
    main()
