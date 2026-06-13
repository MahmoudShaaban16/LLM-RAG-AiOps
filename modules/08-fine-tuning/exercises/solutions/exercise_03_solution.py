"""
Solution: Exercise 3 - Design a before/after evaluation plan
"""

EVAL_DATASET = [
    # --- Target brand voice cases ---
    {
        "id": "delay_notification",
        "input": "A customer's order is delayed by a week. Write the email.",
        "criteria": [
            "Uses a warm, plain-language tone (no corporate jargon like "
            "'we apologize for any inconvenience this may have caused')",
            "Clearly states the delay and an updated expectation",
            "Is concise (not a wall of text)",
        ],
    },
    {
        "id": "refund_confirmation",
        "input": "Confirm to a customer that their refund of $42.00 has been processed.",
        "criteria": [
            "Uses a warm, plain-language tone",
            "States the refund amount clearly",
            "Does not use generic corporate phrases ('per our policy', "
            "'we value your business')",
        ],
    },
    # --- Regression cases (outside the fine-tuning focus) ---
    {
        "id": "off_topic_request",
        "input": "Can you also help me file my taxes?",
        "criteria": [
            "Politely declines / clarifies this is out of scope for customer support",
            "Does not invent tax advice",
            "Remains warm in tone but does not pretend to help with an "
            "unrelated task",
        ],
    },
    {
        "id": "sensitive_complaint",
        "input": (
            "I'm extremely upset — your product caused me to miss a major "
            "deadline and it cost my team real money. I want to speak to a "
            "manager immediately."
        ),
        "criteria": [
            "Acknowledges the customer's frustration appropriately without "
            "being falsely cheerful",
            "Does not make promises (e.g., compensation amounts) the assistant "
            "isn't authorized to make",
            "Offers a clear next step (e.g., escalation path)",
        ],
    },
]

# Shipping criteria:
#
# Ship the fine-tuned model if:
#   - Average score on the brand-voice cases (delay_notification,
#     refund_confirmation) improves by >= 1.0 point (out of 5) over the
#     base model with its current prompt.
#   - Average score on the regression cases (off_topic_request,
#     sensitive_complaint) does NOT drop by more than 0.3 points.
#
# Do NOT ship — even if the brand-voice score improves — if:
#   - Either regression case scores below 3/5 for the fine-tuned model.
#     A classic failure mode here is a model fine-tuned to be "warm" that
#     becomes inappropriately casual or over-promises when a customer is
#     angry or asking about something out of scope — exactly the kind of
#     overfitting/catastrophic-forgetting risk called out in the module
#     README (Section 4).
#   - The fine-tuned model's format/voice only looks right on the training
#     examples' exact phrasing and doesn't generalize to the eval set's
#     differently-worded inputs (a sign of overfitting to surface patterns
#     rather than learning the underlying style).
SHIP_CRITERIA = """
Ship if:
  - Average score on brand-voice cases improves by >= 1.0 point (out of 5)
    over the base model
  - Average score on regression cases does NOT drop by more than 0.3 points

Do NOT ship if:
  - Brand-voice score improves but any regression case drops below a 3/5
    (e.g., the fine-tuned model becomes "warm" in ways that are
    inappropriate for a sensitive/off-topic request)
"""


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
