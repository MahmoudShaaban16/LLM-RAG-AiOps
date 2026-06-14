"""
Exercise 1: Score and prioritize a use-case backlog

TODO:
  1. Implement `priority_score(use_case)` as
     `(impact + feasibility + risk) / 3` (see module README Section 3).
  2. Implement `tier(use_case)` following the README's tiering rules:
       - "Reconsider" if impact <= 2
       - "Reconsider" if feasibility <= 2 AND risk <= 2
       - "Quick win" if priority_score >= 4
       - "Strategic bet" if impact >= 4 (and not already a quick win)
       - otherwise "Fill-in"
  3. Run this script and review the ranked output. Pick the two
     highest-ranked items - are they actually the two you'd pick if you
     were prioritizing a real backlog? If not, which axis (impact,
     feasibility, risk) is the scoring missing for your context?

No API key required - this is pure scoring/ranking logic, like
examples/01_use_case_scoring.py but with a different backlog.
"""

from dataclasses import dataclass


@dataclass
class UseCase:
    name: str
    impact: int       # 1-5, higher = more impact
    feasibility: int  # 1-5, higher = easier to build
    risk: int         # 1-5, higher = LOWER risk (inverse scale, see README)


BACKLOG = [
    UseCase("Auto-generate release notes from merged PRs", impact=2, feasibility=5, risk=5),
    UseCase("Voice assistant that can edit live production config", impact=4, feasibility=2, risk=1),
    UseCase("Classify inbound leads by intent for the sales team", impact=4, feasibility=4, risk=4),
    UseCase("Multilingual translation of marketing copy", impact=3, feasibility=5, risk=4),
    UseCase("Agent that reconciles invoices against purchase orders", impact=5, feasibility=3, risk=2),
]


def priority_score(use_case: UseCase) -> float:
    # TODO
    pass


def tier(use_case: UseCase) -> str:
    # TODO
    pass


def main() -> None:
    scored = [(uc, priority_score(uc)) for uc in BACKLOG]
    if any(score is None for _, score in scored):
        print("(priority_score not implemented yet)")
        return

    ranked = sorted(scored, key=lambda pair: pair[1], reverse=True)

    print(f"{'Use case':<55} {'Score':>6} {'Tier'}")
    print("-" * 80)
    for use_case, score in ranked:
        print(f"{use_case.name:<55} {score:>6.2f} {tier(use_case)}")


if __name__ == "__main__":
    main()
