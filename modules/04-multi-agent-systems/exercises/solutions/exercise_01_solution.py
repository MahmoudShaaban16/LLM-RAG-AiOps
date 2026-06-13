"""
Solution: Exercise 1 - Add a third worker to the supervisor
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


def run_risks_worker(client: Anthropic, task: str) -> str:
    system_prompt = (
        "You are a risk analyst who argues AGAINST a proposed change. Given "
        "a decision the user is considering, list the strongest 3 risks or "
        "downsides. Be specific and concise - 3 short bullet points."
    )
    return call_worker(client, system_prompt, task)


def run_cost_worker(client: Anthropic, task: str) -> str:
    system_prompt = (
        "You are a cost/effort analyst. Given a decision the user is "
        "considering, list the 3 most significant cost or effort "
        "considerations (e.g., engineering time, ongoing operational cost, "
        "migration effort). Be specific and concise - 3 short bullet points."
    )
    return call_worker(client, system_prompt, task)


def run_supervisor(client: Anthropic, task: str, pros: str, risks: str, costs: str) -> str:
    system_prompt = (
        "You are a pragmatic technical advisor. You'll be given a decision "
        "and analysis from three specialists: benefits, risks, and "
        "cost/effort. Synthesize these into a short recommendation: "
        "1) a one-sentence recommendation, 2) the key tradeoff to weigh, "
        "3) one concrete next step. Keep it under 150 words."
    )
    user_content = (
        f"Decision: {task}\n\n"
        f"Benefits identified:\n{pros}\n\n"
        f"Risks identified:\n{risks}\n\n"
        f"Cost/effort considerations:\n{costs}"
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

    print("\n=== Worker C: cost/effort ===")
    costs = run_cost_worker(client, TASK)
    print(costs)

    print("\n=== Supervisor: synthesized recommendation ===")
    recommendation = run_supervisor(client, TASK, pros, risks, costs)
    print(recommendation)

    # Discussion:
    # - With 3 workers, the supervisor's synthesis prompt now includes 3
    #   blocks of worker output. This is still small (a few hundred tokens
    #   each), so for 3 workers it's a non-issue.
    # - The general concern: as M grows (say, 10+ workers), the synthesis
    #   call's input grows linearly with M, and at some point you'd want to:
    #   (a) have each worker return a tighter, structured summary (Exercise 2)
    #   rather than free-text paragraphs, and/or (b) have an intermediate
    #   "summarize the summaries" step before final synthesis, similar to a
    #   map-reduce pattern.


if __name__ == "__main__":
    main()
