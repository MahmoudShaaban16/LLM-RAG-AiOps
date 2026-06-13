"""
Solution: Exercise 3 - Handle a failed worker in the supervisor pattern
"""

import os
import random

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

TASK = (
    "We're deciding whether to migrate our customer support chatbot from a "
    "rules-based system to an LLM-based one. Give us a balanced recommendation."
)


def call_worker(client: Anthropic, system_prompt: str, task: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": task}],
    )
    return response.content[0].text


def run_pros_worker(client: Anthropic, task: str) -> str:
    system_prompt = (
        "You are an analyst who argues FOR a proposed change. Given a "
        "decision the user is considering, list the strongest 3 benefits "
        "or opportunities. Be specific and concise - 3 short bullet points."
    )
    return call_worker(client, system_prompt, task)


def run_risks_worker(client: Anthropic, task: str) -> str:
    """Simulates an unreliable worker - fails about half the time."""
    if random.random() < 0.5:
        raise RuntimeError("risks worker: simulated upstream failure")

    system_prompt = (
        "You are a risk analyst who argues AGAINST a proposed change. Given "
        "a decision the user is considering, list the strongest 3 risks or "
        "downsides. Be specific and concise - 3 short bullet points."
    )
    return call_worker(client, system_prompt, task)


def run_risks_worker_with_retry(client: Anthropic, task: str, retries: int = 1) -> str | None:
    """Calls run_risks_worker, retrying once on failure before giving up and
    returning None (signaling "unavailable" to the supervisor)."""
    attempts = retries + 1
    for attempt in range(1, attempts + 1):
        try:
            return run_risks_worker(client, task)
        except RuntimeError as exc:
            print(f"[risks worker] attempt {attempt} failed: {exc}")
    return None


def run_supervisor(client: Anthropic, task: str, pros: str, risks: str | None) -> str:
    system_prompt = (
        "You are a pragmatic technical advisor. You'll be given a decision, "
        "a list of benefits, and (if available) a list of risks. Synthesize "
        "these into a short recommendation: 1) a one-sentence recommendation, "
        "2) the key tradeoff to weigh, 3) one concrete next step. If risk "
        "analysis is unavailable, note that explicitly and recommend "
        "obtaining it before a final decision. Keep it under 150 words."
    )
    risks_section = risks if risks is not None else (
        "(unavailable - the risk analysis step failed and should be "
        "retried before a final decision is made)"
    )
    user_content = (
        f"Decision: {task}\n\n"
        f"Benefits identified:\n{pros}\n\n"
        f"Risks identified:\n{risks_section}"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== Task ===")
    print(TASK)

    print("\n=== Worker A: pros/benefits ===")
    pros = run_pros_worker(client, TASK)
    print(pros)

    print("\n=== Worker B: risks (with retry) ===")
    risks = run_risks_worker_with_retry(client, TASK, retries=1)
    if risks is None:
        print("(risks worker unavailable after retry)")
    else:
        print(risks)

    print("\n=== Supervisor: synthesized recommendation ===")
    recommendation = run_supervisor(client, TASK, pros, risks)
    print(recommendation)

    # Discussion:
    # - In Module 03, a failing tool call returns a tool_result with
    #   is_error=True *within the same conversation* - the same agent sees
    #   the failure and can react to it in its next turn.
    # - Here, run_risks_worker's failure happens in a completely separate
    #   API call/conversation. The supervisor has no automatic way to "see"
    #   that it failed - your orchestrator code has to catch the exception
    #   and explicitly translate it into something the supervisor's prompt
    #   can react to (the "(unavailable - ...)" string above).
    # - This is a more general point about multi-agent systems: error
    #   handling is entirely your orchestrator's responsibility. There's no
    #   shared mechanism (like is_error) that automatically threads failure
    #   information between independent agent calls - you have to design
    #   that handoff explicitly, the same way you'd design an error response
    #   between two microservices.
    # - The one-retry pattern is a reasonable default for transient failures
    #   (timeouts, rate limits) but won't help if the failure is
    #   deterministic (e.g., a bad prompt) - in that case, retrying just
    #   doubles the cost for the same failure.


if __name__ == "__main__":
    main()
