"""
Exercise 3: Design a before/after evaluation plan

A team wants to fine-tune a model to always respond to customer emails in a
specific brand voice ("warm, plain-language, no corporate jargon"). Acting
as tech lead, define the eval set that would tell you whether it worked
*and* whether anything regressed.

TODO:
  1. Add at least 4 cases to EVAL_DATASET:
       - At least 2 should test the target brand voice directly.
       - At least 2 should test something OUTSIDE the fine-tuning focus
         (e.g., handling an off-topic or sensitive request safely) to
         catch regressions.
  2. Each case needs an `id`, `input`, and `criteria` (list of strings),
     matching the shape used in Module 06's EVAL_DATASET and
     examples/02_evaluate_finetuned_vs_base.py.
  3. Fill in the SHIP_CRITERIA comment describing what score difference
     would justify shipping, and what result would block shipping even if
     the target-voice score improved.
"""

EVAL_DATASET = [
    # TODO: add at least 4 cases here, e.g.:
    # {
    #     "id": "warm_voice_apology",
    #     "input": "A customer's order is delayed by a week. Write the email.",
    #     "criteria": [
    #         "Uses a warm, plain-language tone (no corporate jargon like "
    #         "'we apologize for any inconvenience this may have caused')",
    #         "Clearly states the delay and an updated expectation",
    #         "Is not overly long",
    #     ],
    # },
]

# TODO: describe your shipping criteria here, e.g.:
# SHIP_CRITERIA = """
# Ship if:
#   - Average score on brand-voice cases improves by >= 1.0 point (out of 5)
#     over the base model
#   - Average score on regression cases does NOT drop by more than 0.3 points
#
# Do NOT ship if:
#   - Brand-voice score improves but any regression case drops below a 3/5
#     (e.g., the fine-tuned model starts being "warm" in ways that are
#     inappropriate for a sensitive/off-topic request)
# """
SHIP_CRITERIA = "TODO"


def main() -> None:
    print(f"Eval cases defined: {len(EVAL_DATASET)}")
    for case in EVAL_DATASET:
        print(f"\n=== {case['id']} ===")
        print(f"Input: {case['input']}")
        print("Criteria:")
        for c in case["criteria"]:
            print(f"  - {c}")

    print("\n--- Shipping criteria ---")
    print(SHIP_CRITERIA)


if __name__ == "__main__":
    main()
