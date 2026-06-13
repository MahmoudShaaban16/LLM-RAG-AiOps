"""
03 - Prompt Regression Test

Runs the same eval dataset against two system prompt variants (old vs new),
scores each output with the LLM-as-judge from 02_llm_as_judge.py, and prints
a comparison table — the kind of check you'd run in CI before merging a
prompt change.
"""

import os
from importlib import import_module

from anthropic import Anthropic

eval_dataset_module = import_module("01_eval_dataset")
judge_module = import_module("02_llm_as_judge")

MODEL = "claude-sonnet-4-6"

EVAL_DATASET = eval_dataset_module.EVAL_DATASET

# The "old" prompt: the current production system prompt.
PROMPT_OLD = eval_dataset_module.SYSTEM_PROMPT

# The "new" prompt: a proposed change — here, we've made it more concise and
# explicitly told it to acknowledge uncertainty about plan type.
PROMPT_NEW = (
    "You are a support assistant for a SaaS product called 'Acme Cloud'. "
    "Acme Cloud's refund policy: customers on monthly plans can request a "
    "full refund within 14 days of charge; annual plans within 30 days. "
    "After that window, no refunds are issued, but customers can cancel "
    "to stop future charges. "
    "If the customer's plan type isn't stated, ask for it before giving a "
    "refund answer. Answer in 1-3 sentences, using only the policy "
    "information given above, and never invent policy details."
)


def run_with_prompt(client: Anthropic, system_prompt: str) -> list[dict]:
    """Run every eval case through the model with a given system prompt."""
    results = []
    for case in EVAL_DATASET:
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": case["input"]}],
        )
        output = response.content[0].text
        results.append({
            **case,
            "output": output,
            "output_tokens": response.usage.output_tokens,
        })
    return results


def score_results(client: Anthropic, results: list[dict]) -> list[dict]:
    """Attach a judge score + reasoning to each result."""
    scored = []
    for r in results:
        verdict = judge_module.judge_response(client, r)
        scored.append({**r, "score": verdict["score"], "reasoning": verdict["reasoning"]})
    return scored


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("Running eval dataset against PROMPT_OLD...")
    results_old = score_results(client, run_with_prompt(client, PROMPT_OLD))

    print("Running eval dataset against PROMPT_NEW...")
    results_new = score_results(client, run_with_prompt(client, PROMPT_NEW))

    # --- Comparison table ---
    print("\n" + "=" * 78)
    print(f"{'Case':<24} {'Old score':>10} {'New score':>10} {'Delta':>8} {'Old tok':>8} {'New tok':>8}")
    print("=" * 78)

    total_old, total_new = 0, 0
    regressions = []

    for old, new in zip(results_old, results_new):
        delta = new["score"] - old["score"]
        total_old += old["score"]
        total_new += new["score"]
        if delta < 0:
            regressions.append(old["id"])

        flag = " <-- regression" if delta < 0 else ""
        print(
            f"{old['id']:<24} {old['score']:>10} {new['score']:>10} "
            f"{delta:>+8} {old['output_tokens']:>8} {new['output_tokens']:>8}{flag}"
        )

    print("=" * 78)
    avg_old = total_old / len(results_old)
    avg_new = total_new / len(results_new)
    print(f"{'AVERAGE':<24} {avg_old:>10.2f} {avg_new:>10.2f} {avg_new - avg_old:>+8.2f}")

    print("\n--- Verdict ---")
    if regressions:
        print(f"FAIL: PROMPT_NEW regressed on case(s): {', '.join(regressions)}")
        print("Inspect these cases before merging this prompt change.")
    elif avg_new > avg_old:
        print("PASS: PROMPT_NEW improves average score with no per-case regressions.")
    elif avg_new == avg_old:
        print("NEUTRAL: no significant quality change. Consider cost/latency/length.")
    else:
        print("FAIL: PROMPT_NEW has a lower average score than PROMPT_OLD.")


if __name__ == "__main__":
    main()
