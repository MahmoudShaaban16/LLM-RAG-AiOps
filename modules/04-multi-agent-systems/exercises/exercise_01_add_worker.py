"""
Exercise 1: Add a third worker to the supervisor

TODO:
  1. Add run_risks_worker (analyst arguing against the change).
  2. Add run_cost_worker (focuses on cost/effort considerations).
  3. Update run_supervisor to synthesize all three outputs.
"""

import os

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


# TODO: def run_risks_worker(client, task) -> str: ...


# TODO: def run_cost_worker(client, task) -> str: ...


def run_supervisor(client: Anthropic, task: str, pros: str) -> str:
    # TODO: accept risks and costs too, and include them in user_content
    system_prompt = (
        "You are a pragmatic technical advisor. You'll be given a decision "
        "and analysis from multiple specialists. Synthesize these into a "
        "short recommendation: 1) a one-sentence recommendation, 2) the key "
        "tradeoff to weigh, 3) one concrete next step. Keep it under 150 words."
    )
    user_content = f"Decision: {task}\n\nBenefits identified:\n{pros}"
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

    # TODO: call run_risks_worker and run_cost_worker, print their outputs

    print("\n=== Supervisor: synthesized recommendation ===")
    recommendation = run_supervisor(client, TASK, pros)
    print(recommendation)


if __name__ == "__main__":
    main()
