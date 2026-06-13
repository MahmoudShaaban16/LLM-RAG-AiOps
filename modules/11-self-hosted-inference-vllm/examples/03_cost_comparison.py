"""
Self-hosted (vLLM) vs. managed API: a back-of-envelope cost crossover.

Compares a fixed monthly GPU cost (self-hosted, vLLM) against a per-token
managed API cost (e.g. Sonnet 4.6 pricing from Module 01), to find the
request volume at which self-hosting becomes cheaper.

This is intentionally simple - it ignores utilization, multi-GPU scaling,
and quality differences between models (see the module README's decision
framework for those factors). It answers one narrow question: "at what
volume do the fixed and variable costs cross over?"
"""

# Managed API pricing (Sonnet 4.6, see Module 01 README)
API_INPUT_PRICE_PER_MILLION = 3.00
API_OUTPUT_PRICE_PER_MILLION = 15.00

# A single mid-range GPU suitable for a 7B-class model, on-demand cloud pricing.
GPU_COST_PER_HOUR = 2.00
HOURS_PER_MONTH = 24 * 30

# Assumed average request shape.
AVG_INPUT_TOKENS = 500
AVG_OUTPUT_TOKENS = 200


def api_cost_per_request(input_tokens: int, output_tokens: int) -> float:
    input_cost = input_tokens / 1_000_000 * API_INPUT_PRICE_PER_MILLION
    output_cost = output_tokens / 1_000_000 * API_OUTPUT_PRICE_PER_MILLION
    return input_cost + output_cost


def main() -> None:
    monthly_gpu_cost = GPU_COST_PER_HOUR * HOURS_PER_MONTH
    per_request_api_cost = api_cost_per_request(AVG_INPUT_TOKENS, AVG_OUTPUT_TOKENS)

    breakeven_requests_per_month = monthly_gpu_cost / per_request_api_cost

    print(f"Assumptions: ~{AVG_INPUT_TOKENS} input / {AVG_OUTPUT_TOKENS} output tokens per request")
    print(f"Managed API cost per request: ${per_request_api_cost:.6f}")
    print(f"Self-hosted GPU cost: ${GPU_COST_PER_HOUR:.2f}/hr -> ${monthly_gpu_cost:,.2f}/month (always-on)")
    print()
    print(
        f"Breakeven: ~{breakeven_requests_per_month:,.0f} requests/month "
        f"(~{breakeven_requests_per_month / 30:,.0f}/day)"
    )
    print()
    print(
        "Below this volume, the always-on GPU is more expensive than the API.\n"
        "Above it, the fixed GPU cost is amortized over more requests than the\n"
        "API's per-token cost would allow at the same budget.\n"
        "\n"
        "This ignores: GPU utilization (an idle GPU still costs money), the\n"
        "quality difference between the self-hosted open-weight model and the\n"
        "managed model, and the operational cost of running vLLM yourself.\n"
        "See the module README's decision framework for the fuller picture."
    )


if __name__ == "__main__":
    main()
