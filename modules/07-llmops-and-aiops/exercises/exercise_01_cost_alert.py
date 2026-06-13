"""
Exercise 1: Add a cost budget alert

TODO:
  1. Add a BUDGET_USD_PER_USER constant.
  2. After each logged request, compute the running total cost for that
     user_id and print a warning if it exceeds the budget.
  3. Run a simulated batch of requests across 2-3 users so at least one
     crosses the budget.
"""

import os
from importlib import import_module

from anthropic import Anthropic

logging_module = import_module("02_request_logging_and_cost_tracking")

MODEL = "claude-sonnet-4-6"

# TODO: set a budget per user (in USD)
BUDGET_USD_PER_USER = None


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    sample_requests = [
        ("support_assistant", "user_1", "How do I reset my password?"),
        ("support_assistant", "user_1", "What's included in the Enterprise plan?"),
        ("support_assistant", "user_1", "Can you explain your refund policy in detail?"),
        ("support_assistant", "user_2", "What are your support hours?"),
        ("doc_summarizer", "user_2", "Summarize: Our roadmap focuses on reliability and onboarding."),
    ]

    for feature, user_id, question in sample_requests:
        logging_module.logged_create(
            client,
            feature=feature,
            user_id=user_id,
            model=MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": question}],
        )

        # TODO: compute running total cost for this user_id from
        # logging_module.REQUEST_LOG, and print a warning if it exceeds
        # BUDGET_USD_PER_USER.

    logging_module.print_summary()


if __name__ == "__main__":
    main()
