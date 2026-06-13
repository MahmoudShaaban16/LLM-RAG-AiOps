"""
01 - Supervisor / Worker

A supervisor agent breaks a task into two sub-tasks and delegates each to a
specialized "worker" - a separate Claude call with its own system prompt.
The supervisor then synthesizes the workers' outputs into a final answer.

Each worker call is independent (no shared conversation history) - the
supervisor's code is responsible for passing the right information to each
worker and combining their results.
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

TASK = (
    "We're deciding whether to migrate our customer support chatbot from a "
    "rules-based system to an LLM-based one. Give us a balanced recommendation."
)


def call_worker(client: Anthropic, system_prompt: str, task: str) -> str:
    """A worker is just a focused Messages API call with its own system prompt."""
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
    system_prompt = (
        "You are a risk analyst who argues AGAINST a proposed change. Given "
        "a decision the user is considering, list the strongest 3 risks or "
        "downsides. Be specific and concise - 3 short bullet points."
    )
    return call_worker(client, system_prompt, task)


def run_supervisor(client: Anthropic, task: str, pros: str, risks: str) -> str:
    """The supervisor's final pass: synthesize both workers' outputs into one
    balanced recommendation."""
    system_prompt = (
        "You are a pragmatic technical advisor. You'll be given a decision, "
        "a list of benefits, and a list of risks (each produced separately). "
        "Synthesize these into a short recommendation: 1) a one-sentence "
        "recommendation, 2) the key tradeoff to weigh, 3) one concrete next "
        "step. Keep it under 150 words."
    )
    user_content = (
        f"Decision: {task}\n\n"
        f"Benefits identified:\n{pros}\n\n"
        f"Risks identified:\n{risks}"
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
    risks = run_risks_worker(client, TASK)
    print(risks)

    print("\n=== Supervisor: synthesized recommendation ===")
    recommendation = run_supervisor(client, TASK, pros, risks)
    print(recommendation)


if __name__ == "__main__":
    main()
