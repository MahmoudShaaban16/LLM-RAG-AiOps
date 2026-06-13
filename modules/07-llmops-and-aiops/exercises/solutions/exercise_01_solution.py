"""
Solution: Exercise 1 - Add a cost budget alert
"""

import os
from importlib import import_module

from anthropic import Anthropic

logging_module = import_module("02_request_logging_and_cost_tracking")

MODEL = "claude-sonnet-4-6"

BUDGET_USD_PER_USER = 0.003  # deliberately low so the sample data trips it


def total_cost_for_user(user_id: str) -> float:
    return sum(
        r["estimated_cost_usd"]
        for r in logging_module.REQUEST_LOG
        if r["user_id"] == user_id
    )


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    sample_requests = [
        ("support_assistant", "user_1", "How do I reset my password?"),
        ("support_assistant", "user_1", "What's included in the Enterprise plan?"),
        ("support_assistant", "user_1", "Can you explain your refund policy in detail?"),
        ("support_assistant", "user_2", "What are your support hours?"),
        ("doc_summarizer", "user_2", "Summarize: Our roadmap focuses on reliability and onboarding."),
    ]

    alerted_users = set()

    for feature, user_id, question in sample_requests:
        logging_module.logged_create(
            client,
            feature=feature,
            user_id=user_id,
            model=MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": question}],
        )

        running_total = total_cost_for_user(user_id)
        if running_total > BUDGET_USD_PER_USER and user_id not in alerted_users:
            print(f"BUDGET ALERT: {user_id} has exceeded ${BUDGET_USD_PER_USER:.4f} "
                  f"(current: ${running_total:.6f})")
            alerted_users.add(user_id)

    logging_module.print_summary()


# Discussion:
# What should happen when a user crosses a budget threshold depends heavily
# on context:
#   - Internal tool / employee usage: an alert to an admin or Slack channel
#     is often enough -- you want visibility, not necessarily a hard stop.
#   - Customer-facing feature with a free tier: downgrading to a cheaper
#     model (or a stricter max_tokens) preserves the feature working at all,
#     while limiting cost -- often better UX than a hard block.
#   - Customer-facing feature with paid usage-based billing: a hard block
#     (or a prompt to upgrade) may be the correct product behavior, similar
#     to any other metered API.
# In all cases, the alert/threshold logic should be centralized (e.g., in
# the logging wrapper or a middleware layer) rather than duplicated at each
# call site, and the threshold itself should be configurable per plan/tier.


if __name__ == "__main__":
    main()
