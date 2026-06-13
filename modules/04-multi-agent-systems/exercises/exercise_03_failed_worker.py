"""
Exercise 3: Handle a failed worker in the supervisor pattern

TODO:
  1. Wrap each worker call so that if run_risks_worker raises, the
     supervisor still runs - tell it the risks analysis is unavailable.
  2. Run multiple times and confirm sensible output in both cases.
  3. Bonus: add one retry attempt before falling back to "unavailable".
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


def run_supervisor(client: Anthropic, task: str, pros: str, risks: str | None) -> str:
    # TODO: when risks is None, tell the supervisor it's unavailable instead
    # of just passing an empty/missing value silently.
    system_prompt = (
        "You are a pragmatic technical advisor. You'll be given a decision, "
        "a list of benefits, and (if available) a list of risks. Synthesize "
        "these into a short recommendation: 1) a one-sentence recommendation, "
        "2) the key tradeoff to weigh, 3) one concrete next step. If risk "
        "analysis is unavailable, note that explicitly and recommend "
        "obtaining it before a final decision. Keep it under 150 words."
    )
    user_content = (
        f"Decision: {task}\n\n"
        f"Benefits identified:\n{pros}\n\n"
        f"Risks identified:\n{risks if risks else '(unavailable)'}"
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

    print("\n=== Worker B: risks ===")
    # TODO: wrap this call - on failure, set risks = None instead of
    # crashing the whole script. Bonus: retry once first.
    risks = run_risks_worker(client, TASK)
    print(risks)

    print("\n=== Supervisor: synthesized recommendation ===")
    recommendation = run_supervisor(client, TASK, pros, risks)
    print(recommendation)


if __name__ == "__main__":
    main()
