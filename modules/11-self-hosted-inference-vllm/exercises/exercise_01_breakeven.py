"""
Exercise 1: Model the breakeven for your own workload

TODO:
  1. Write breakeven_requests_per_month(avg_input_tokens, avg_output_tokens,
     gpu_cost_per_hour, hours_per_month=24*30) that returns the monthly
     request volume at which self-hosted GPU cost == managed API cost.
  2. Compute it for the 3 scenarios below.
  3. Print all three.
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
    # TODO: implement
    pass


def main() -> None:
    for name, params in SCENARIOS.items():
        # TODO: compute and print the breakeven for this scenario
        pass


if __name__ == "__main__":
    main()
