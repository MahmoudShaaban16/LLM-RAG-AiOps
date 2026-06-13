"""
Solution: Exercise 1 - Model the breakeven for your own workload
"""

API_INPUT_PRICE_PER_MILLION = 3.00
API_OUTPUT_PRICE_PER_MILLION = 15.00

SCENARIOS = {
    "classification": {"avg_input_tokens": 50, "avg_output_tokens": 10, "gpu_cost_per_hour": 2.00},
    "rag_support_assistant": {"avg_input_tokens": 1500, "avg_output_tokens": 300, "gpu_cost_per_hour": 2.00},
    "long_document_summarizer": {"avg_input_tokens": 8000, "avg_output_tokens": 500, "gpu_cost_per_hour": 2.00},
}


def api_cost_per_request(input_tokens: int, output_tokens: int) -> float:
    input_cost = input_tokens / 1_000_000 * API_INPUT_PRICE_PER_MILLION
    output_cost = output_tokens / 1_000_000 * API_OUTPUT_PRICE_PER_MILLION
    return input_cost + output_cost


def breakeven_requests_per_month(avg_input_tokens, avg_output_tokens, gpu_cost_per_hour, hours_per_month=24 * 30):
    monthly_gpu_cost = gpu_cost_per_hour * hours_per_month
    per_request_cost = api_cost_per_request(avg_input_tokens, avg_output_tokens)
    return monthly_gpu_cost / per_request_cost


def main() -> None:
    for name, params in SCENARIOS.items():
        breakeven = breakeven_requests_per_month(**params)
        per_request_cost = api_cost_per_request(params["avg_input_tokens"], params["avg_output_tokens"])
        print(f"{name}:")
        print(f"  API cost/request: ${per_request_cost:.6f}")
        print(f"  Breakeven: ~{breakeven:,.0f} requests/month (~{breakeven / 30:,.0f}/day)")
        print()


if __name__ == "__main__":
    main()


# Discussion:
#
# - "classification" (50/10 tokens) has the cheapest per-request API cost,
#   so it takes the HIGHEST request volume to justify a fixed GPU - but
#   classification workloads are exactly the kind that run at very high
#   volume in practice (every user action, every event), so they often DO
#   cross this threshold.
# - "long_document_summarizer" (8000/500 tokens) has the most expensive
#   per-request API cost, so its breakeven volume is lowest - even a modest
#   number of large-document requests per month can justify self-hosting,
#   IF an open-weight model produces summaries good enough (Module 06 eval).
# - "rag_support_assistant" sits in between - this matches the Module 10
#   capstone's profile, and is a common candidate for a *hybrid* approach:
#   self-host for the high-volume, well-defined categorization step, keep
#   the API for the final response generation where quality matters most.
#
# This matches real-world patterns: narrow, extremely high-volume,
# well-evaluated tasks (classification, extraction, moderation) are the most
# common self-hosting candidates - not because they're individually
# expensive, but because volume dominates the breakeven calculation.
