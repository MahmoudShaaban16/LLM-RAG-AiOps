"""
02 - ROI Estimator

A rough monthly-savings and payback-period calculator for an AI use case,
following the cost-estimation framing from the module README (Section 4)
and Module 07's cost-tracking mindset.

This deliberately uses simple, transparent arithmetic - the point is to
make assumptions explicit and easy to challenge in a one-pager review, not
to produce a precise forecast.

No API key required - this is pure arithmetic over example assumptions.
"""

from dataclasses import dataclass


@dataclass
class RoiAssumptions:
    name: str
    monthly_volume: int          # number of requests/tasks per month
    human_cost_per_task: float   # fully-loaded cost of a human handling one task today
    ai_cost_per_task: float      # API cost per task (from Module 07-style cost tracking)
    automation_rate: float       # fraction (0-1) of tasks the AI fully handles without a human
    one_time_cost: float         # implementation cost (engineering time, setup)


SCENARIOS = [
    RoiAssumptions(
        name="Support reply drafting (human-in-the-loop)",
        monthly_volume=10_000,
        human_cost_per_task=4.00,
        ai_cost_per_task=0.05,
        automation_rate=0.0,  # drafts only - human still sends, so no task is "fully" automated
        one_time_cost=25_000,
    ),
    RoiAssumptions(
        name="Ticket auto-routing",
        monthly_volume=10_000,
        human_cost_per_task=0.50,
        ai_cost_per_task=0.01,
        automation_rate=0.9,
        one_time_cost=15_000,
    ),
]


def monthly_savings(a: RoiAssumptions) -> float:
    """
    For automated tasks: savings = (human cost - AI cost) per task.
    For non-automated tasks (e.g., draft-only): the human still does the
    task, so the only "savings" is the *time* the draft saves them - which
    this simple model doesn't quantify directly. We report the AI cost as a
    pure additional expense for those tasks, so this function returns a
    conservative (possibly negative) number when automation_rate is low.
    """
    automated = a.monthly_volume * a.automation_rate
    not_automated = a.monthly_volume - automated

    savings_from_automation = automated * (a.human_cost_per_task - a.ai_cost_per_task)
    cost_of_ai_on_non_automated = not_automated * a.ai_cost_per_task

    return savings_from_automation - cost_of_ai_on_non_automated


def payback_period_months(a: RoiAssumptions) -> float | None:
    savings = monthly_savings(a)
    if savings <= 0:
        return None
    return a.one_time_cost / savings


def main() -> None:
    for scenario in SCENARIOS:
        savings = monthly_savings(scenario)
        payback = payback_period_months(scenario)

        print(f"\n=== {scenario.name} ===")
        print(f"  Monthly volume:        {scenario.monthly_volume:,}")
        print(f"  Automation rate:       {scenario.automation_rate:.0%}")
        print(f"  Estimated monthly savings: ${savings:,.2f}")
        if payback is None:
            print("  Payback period:        N/A (no positive monthly savings under these assumptions)")
        else:
            print(f"  Payback period:        {payback:.1f} months")


if __name__ == "__main__":
    main()
