"""
Solution: Exercise 1 - Score and prioritize a use-case backlog
"""

from dataclasses import dataclass


@dataclass
class UseCase:
    name: str
    impact: int
    feasibility: int
    risk: int


BACKLOG = [
    UseCase("Auto-generate release notes from merged PRs", impact=2, feasibility=5, risk=5),
    UseCase("Voice assistant that can edit live production config", impact=4, feasibility=2, risk=1),
    UseCase("Classify inbound leads by intent for the sales team", impact=4, feasibility=4, risk=4),
    UseCase("Multilingual translation of marketing copy", impact=3, feasibility=5, risk=4),
    UseCase("Agent that reconciles invoices against purchase orders", impact=5, feasibility=3, risk=2),
]


def priority_score(use_case: UseCase) -> float:
    return (use_case.impact + use_case.feasibility + use_case.risk) / 3


def tier(use_case: UseCase) -> str:
    score = priority_score(use_case)

    if use_case.impact <= 2:
        return "Reconsider"
    if use_case.feasibility <= 2 and use_case.risk <= 2:
        return "Reconsider"
    if score >= 4:
        return "Quick win"
    if use_case.impact >= 4:
        return "Strategic bet"
    return "Fill-in"


def main() -> None:
    ranked = sorted(BACKLOG, key=priority_score, reverse=True)

    print(f"{'Use case':<55} {'Score':>6} {'Tier'}")
    print("-" * 80)
    for use_case in ranked:
        print(f"{use_case.name:<55} {priority_score(use_case):>6.2f} {tier(use_case)}")

    # Discussion:
    # - "Voice assistant that can edit live production config" scores low
    #   (2.33) and is "Reconsider" - both low feasibility AND low risk-score
    #   (i.e. high actual risk). Even though "impact" was rated 4, the
    #   combination of "hard to build" and "high cost of error" means this
    #   shouldn't be scoped yet, regardless of its impact score.
    # - "Auto-generate release notes" is high feasibility/risk-score but low
    #   impact (2) - it's explicitly "Reconsider" by the impact<=2 rule, even
    #   though it would otherwise look like an easy "Quick win". This is the
    #   scoring framework's way of saying "don't spend a sprint on something
    #   that doesn't move the needle, even if it's easy."
    # - The framework doesn't capture *dependencies* between use cases (e.g.,
    #   "lead classification" might be a prerequisite for a later, higher-impact
    #   feature) - that's a real gap; sequencing still needs human judgment.


if __name__ == "__main__":
    main()
