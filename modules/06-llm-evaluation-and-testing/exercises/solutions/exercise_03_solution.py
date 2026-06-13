"""
Solution: Exercise 3 - Run a regression test with a real prompt change
"""

import os
from importlib import import_module

from anthropic import Anthropic

eval_dataset_module = import_module("01_eval_dataset")
regression_module = import_module("03_prompt_regression_test")

MODEL = "claude-sonnet-4-6"
EVAL_DATASET = eval_dataset_module.EVAL_DATASET

PROMPT_OLD = eval_dataset_module.SYSTEM_PROMPT

# A deliberately much shorter prompt: drops the explicit policy text and asks
# the model to "be brief" -- a plausible cost-cutting change (fewer system
# prompt tokens, likely shorter outputs), but risks the model being vaguer
# about the actual policy.
PROMPT_NEW = (
    "You are a support assistant for 'Acme Cloud'. Monthly plans: 14-day "
    "refund window. Annual plans: 30-day refund window. After that, no "
    "refund, but customers can cancel. Be brief."
)


def print_comparison(label: str, results_old: list[dict], results_new: list[dict]) -> tuple[float, float]:
    print(f"\n{'='*78}")
    print(f"{label}")
    print(f"{'Case':<24} {'Old score':>10} {'New score':>10} {'Delta':>8} {'Old tok':>8} {'New tok':>8}")
    print("=" * 78)

    total_old, total_new = 0, 0
    for old, new in zip(results_old, results_new):
        delta = new["score"] - old["score"]
        total_old += old["score"]
        total_new += new["score"]
        flag = " <-- regression" if delta < 0 else ""
        print(
            f"{old['id']:<24} {old['score']:>10} {new['score']:>10} "
            f"{delta:>+8} {old['output_tokens']:>8} {new['output_tokens']:>8}{flag}"
        )

    avg_old = total_old / len(results_old)
    avg_new = total_new / len(results_new)
    print("=" * 78)
    print(f"{'AVERAGE':<24} {avg_old:>10.2f} {avg_new:>10.2f} {avg_new - avg_old:>+8.2f}")
    return avg_old, avg_new


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # --- Main comparison: PROMPT_OLD vs PROMPT_NEW ---
    results_old = regression_module.score_results(
        client, regression_module.run_with_prompt(client, PROMPT_OLD)
    )
    results_new = regression_module.score_results(
        client, regression_module.run_with_prompt(client, PROMPT_NEW)
    )
    print_comparison("PROMPT_OLD vs PROMPT_NEW", results_old, results_new)

    # --- Bonus: run PROMPT_OLD through the pipeline a second time ---
    results_old_rerun = regression_module.score_results(
        client, regression_module.run_with_prompt(client, PROMPT_OLD)
    )
    print_comparison("PROMPT_OLD (run 1) vs PROMPT_OLD (run 2)", results_old, results_old_rerun)


# Answers (example, will vary by actual run):
# 1. Would you ship PROMPT_NEW?
#    Only if it shows no per-case regressions and a clear token/cost
#    reduction. A shorter prompt that drops the explicit policy text risks
#    the model being vaguer on edge cases (e.g., "ambiguous_plan_type"), so
#    that case specifically needs to be checked, not just the average.
#
# 2. What additional eval cases would increase confidence?
#    More cases near the refund-window boundary, and a second adversarial
#    case, since the shorter prompt has less explicit guardrail language.
#
# 3. (Bonus) Were the two PROMPT_OLD runs identical?
#    Often not -- judge scores can vary by +/-1 between runs even with the
#    same prompt and inputs, due to model non-determinism on both the
#    generation and judging steps. This means a 1-point average difference
#    on a 4-case dataset is within noise; you'd want a larger dataset (or to
#    average over multiple runs) before treating a small delta as a real
#    signal.


if __name__ == "__main__":
    main()
