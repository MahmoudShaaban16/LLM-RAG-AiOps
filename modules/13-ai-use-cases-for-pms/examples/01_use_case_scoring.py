"""
01 - Use-Case Scoring

Implements the Impact / Feasibility / Risk scoring framework from the
module README (Section 3) over a sample backlog of candidate AI use
cases, and sorts them into tiers.

No API key required - this is pure scoring/ranking logic.
"""

from dataclasses import dataclass


@dataclass
class UseCase:
    name: str
    impact: int       # 1-5, higher = more impact
    feasibility: int  # 1-5, higher = easier to build
    risk: int         # 1-5, higher = LOWER risk (inverse scale, see README)


BACKLOG = [
    UseCase("Draft replies to common support emails", impact=4, feasibility=5, risk=4),
    UseCase("Internal 'ask the handbook' search assistant", impact=3, feasibility=4, risk=5),
    UseCase("Agent that can issue refunds automatically", impact=4, feasibility=3, risk=1),
    UseCase("Summarize sales call transcripts for CRM notes", impact=3, feasibility=5, risk=4),
    UseCase("Auto-route support tickets to the right team", impact=4, feasibility=4, risk=3),
    UseCase("Fully autonomous outbound sales emailer", impact=5, feasibility=2, risk=1),
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

    print(f"{'Use case':<48} {'Score':>6} {'Tier'}")
    print("-" * 70)
    for use_case in ranked:
        print(f"{use_case.name:<48} {priority_score(use_case):>6.2f} {tier(use_case)}")


if __name__ == "__main__":
    main()
