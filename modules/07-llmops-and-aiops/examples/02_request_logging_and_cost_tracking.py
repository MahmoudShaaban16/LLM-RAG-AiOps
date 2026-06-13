"""
02 - Request Logging & Cost Tracking

A small wrapper around client.messages.create that logs request/response
metadata (timestamp, model, token usage, estimated cost, latency) to a list
of records, then prints a cost summary. This is the minimal version of the
observability described in the module README -- in production you'd send
these records to your logging/metrics system instead of an in-memory list.
"""

import os
import time
from datetime import datetime, timezone

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

# Pricing table (USD per 1M tokens) -- see Module 01 README for the full
# table and a reminder to check https://www.anthropic.com/pricing for
# current rates.
PRICING_PER_MILLION = {
    "claude-opus-4-8": {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
}

# In-memory "log" of request records. In production, replace this with
# writes to your logging pipeline (e.g., structured logs shipped to your
# observability platform, or rows in a database/data warehouse).
REQUEST_LOG: list[dict] = []


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    prices = PRICING_PER_MILLION[model]
    return (
        input_tokens / 1_000_000 * prices["input"]
        + output_tokens / 1_000_000 * prices["output"]
    )


def logged_create(client: Anthropic, feature: str, user_id: str, **kwargs):
    """Wrapper around client.messages.create that logs metadata for every call."""
    model = kwargs.get("model", MODEL)

    start = time.monotonic()
    response = client.messages.create(**kwargs)
    latency_ms = (time.monotonic() - start) * 1000

    usage = response.usage
    cost = estimate_cost(model, usage.input_tokens, usage.output_tokens)

    REQUEST_LOG.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "feature": feature,
        "user_id": user_id,
        "model": model,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "latency_ms": round(latency_ms, 1),
        "estimated_cost_usd": cost,
    })

    return response


def print_summary() -> None:
    print("\n--- Request log ---")
    for r in REQUEST_LOG:
        print(
            f"[{r['timestamp']}] feature={r['feature']:<20} user={r['user_id']:<8} "
            f"model={r['model']:<20} in={r['input_tokens']:>5} out={r['output_tokens']:>5} "
            f"latency={r['latency_ms']:>7.1f}ms cost=${r['estimated_cost_usd']:.6f}"
        )

    print("\n--- Summary ---")
    total_cost = sum(r["estimated_cost_usd"] for r in REQUEST_LOG)
    total_input = sum(r["input_tokens"] for r in REQUEST_LOG)
    total_output = sum(r["output_tokens"] for r in REQUEST_LOG)
    avg_latency = sum(r["latency_ms"] for r in REQUEST_LOG) / len(REQUEST_LOG)

    print(f"Total requests:   {len(REQUEST_LOG)}")
    print(f"Total input tokens:  {total_input}")
    print(f"Total output tokens: {total_output}")
    print(f"Average latency:  {avg_latency:.1f}ms")
    print(f"Total estimated cost: ${total_cost:.6f}")

    # Per-user breakdown -- the kind of query a PM would want answered.
    by_user: dict[str, float] = {}
    for r in REQUEST_LOG:
        by_user[r["user_id"]] = by_user.get(r["user_id"], 0.0) + r["estimated_cost_usd"]

    print("\n--- Cost per user ---")
    for user_id, cost in by_user.items():
        print(f"{user_id}: ${cost:.6f}")


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    sample_requests = [
        ("support_assistant", "user_1", "How do I reset my password?"),
        ("support_assistant", "user_2", "What's included in the Enterprise plan?"),
        ("doc_summarizer", "user_1", "Summarize: Our Q3 roadmap focuses on three pillars: "
            "reliability, self-serve onboarding, and expanding API coverage."),
    ]

    for feature, user_id, question in sample_requests:
        logged_create(
            client,
            feature=feature,
            user_id=user_id,
            model=MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": question}],
        )

    print_summary()


if __name__ == "__main__":
    main()
