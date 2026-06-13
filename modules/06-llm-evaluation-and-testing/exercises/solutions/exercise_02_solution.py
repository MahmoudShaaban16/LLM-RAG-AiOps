"""
Solution: Exercise 2 - Build a judge for a different task (summarization)
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

SUMMARY_EVAL_DATASET = [
    {
        "id": "product_update_email",
        "text": (
            "Hi team, just a heads up that starting next Monday we're rolling out "
            "the new billing dashboard to all customers on the Pro and Enterprise "
            "tiers. Free-tier customers will get access in about a month, once "
            "we've finished load testing. The new dashboard includes usage "
            "forecasts, downloadable invoices, and a redesigned plan-comparison "
            "page. No action is needed from existing customers -- the change "
            "will appear automatically in their account."
        ),
        "criteria": [
            "Captures the main point (new billing dashboard rollout) in one sentence",
            "Does not exceed 25 words",
            "Does not include opinions or claims not present in the source",
        ],
    },
    {
        "id": "incident_postmortem_excerpt",
        "text": (
            "During the deploy at 14:02 UTC, a misconfigured feature flag caused "
            "10% of API requests to receive 500 errors for approximately 12 "
            "minutes. The on-call engineer rolled back the deploy at 14:14 UTC, "
            "after which error rates returned to baseline. No customer data was "
            "affected. A follow-up action item is to add a canary deploy stage "
            "that would have caught this before full rollout."
        ),
        "criteria": [
            "Mentions the duration and approximate error rate of the incident",
            "Mentions the resolution (rollback) and that no data was affected",
            "Does not exceed 30 words",
        ],
    },
]

JUDGE_SCHEMA = {
    "name": "record_judgment",
    "description": "Record a quality score and reasoning for a summary.",
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

JUDGE_SYSTEM_PROMPT = (
    "You are a strict evaluator of text summaries. You will be given the "
    "original text, a list of criteria a good summary should satisfy, and a "
    "candidate summary. Score how well the summary meets ALL the criteria on "
    "a 1-5 scale:\n"
    "  5 = fully meets every criterion\n"
    "  4 = meets all criteria with a minor issue (e.g., slightly over the word limit)\n"
    "  3 = meets most criteria but misses one\n"
    "  2 = misses the main point or adds unsupported claims\n"
    "  1 = fails most or all criteria\n"
    "Be specific about which criteria were or were not met, including exact word counts."
)


def summarize(client: Anthropic, text: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=150,
        system="Summarize the given text in one sentence, as concisely as possible.",
        messages=[{"role": "user", "content": text}],
    )
    return response.content[0].text


def judge_summary(client: Anthropic, case: dict, summary: str) -> dict:
    criteria_text = "\n".join(f"- {c}" for c in case["criteria"])
    judge_prompt = (
        f"Original text:\n{case['text']}\n\n"
        f"Criteria the summary should satisfy:\n{criteria_text}\n\n"
        f"Summary to evaluate:\n{summary}"
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

    for case in SUMMARY_EVAL_DATASET:
        summary = summarize(client, case["text"])
        verdict = judge_summary(client, case, summary)
        print(f"=== {case['id']} ===")
        print(f"Summary: {summary}")
        print(f"Score:   {verdict['score']}/5")
        print(f"Reason:  {verdict['reasoning']}")
        print()


# Discussion:
# The same 1-5 *scale* works, but the rubric *description* per score level
# needs to change to match what "good" means for this task. For the support
# task, "5" meant "addresses the policy question correctly and completely."
# For summarization, "5" needs to encode objective, checkable properties like
# word count and faithfulness to the source -- criteria that are much more
# mechanical than "is this a helpful support response." In general: keep the
# 1-5 scale for consistency across your eval suite, but always rewrite what
# each score level *means* for the specific task being judged.


if __name__ == "__main__":
    main()
