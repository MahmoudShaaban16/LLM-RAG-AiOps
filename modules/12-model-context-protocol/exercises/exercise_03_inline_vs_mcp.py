"""
Exercise 3: Inline tools vs. an MCP server - decision framework

For each scenario below, decide whether the team should keep the tool as
an inline tool definition (Module 03 style) or expose/consume it via an
MCP server (Module 12 style), and write a one-sentence justification.

TODO:
  1. Implement `recommend(scenario)` to return a `Recommendation` for each
     `Scenario` in SCENARIOS, using the criteria from the module README
     section 3 (reuse across apps, who owns/operates it, independent
     update cycles, operational surface).
  2. Run this script and review your justifications against the
     `EXPECTED` hints printed alongside each scenario - they're not exact
     wording to match, but your reasoning should point the same direction.

This is a reasoning exercise - no API key or MCP server needed.
"""

from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    description: str
    # Hint about the kind of reasoning expected (not graded automatically).
    hint: str


@dataclass
class Recommendation:
    choice: str  # "inline" or "mcp"
    justification: str


SCENARIOS = [
    Scenario(
        name="single_internal_calculator",
        description=(
            "A single agent in your codebase needs a 'calculate' tool for "
            "basic arithmetic. No other team or app needs it."
        ),
        hint="Reuse benefit is ~zero; extra operational surface isn't justified.",
    ),
    Scenario(
        name="shared_company_wiki_search",
        description=(
            "Five different internal agents (support bot, onboarding "
            "assistant, sales assistant, and two others) all need to search "
            "the same internal company wiki. The wiki team wants to own and "
            "update this search tool independently of each agent's release "
            "cycle."
        ),
        hint="Multiple consumers + independent ownership/update cycle -> MCP.",
    ),
    Scenario(
        name="third_party_github_server",
        description=(
            "Your agent needs to read issues and PRs from GitHub. An "
            "open-source GitHub MCP server already exists and is maintained "
            "by someone else."
        ),
        hint="Don't reimplement someone else's integration - consume their MCP server.",
    ),
    Scenario(
        name="prototype_with_one_off_mock_tool",
        description=(
            "You're prototyping a new agent feature this week. It needs a "
            "throwaway 'get_fake_weather' tool that returns hardcoded data "
            "for a demo, and will likely be deleted after the demo."
        ),
        hint="Short-lived, single-use, no reuse story -> simplest option.",
    ),
]


def recommend(scenario: Scenario) -> Recommendation:
    # TODO: implement the decision + justification for each scenario.
    pass


def main() -> None:
    for scenario in SCENARIOS:
        print(f"\n=== {scenario.name} ===")
        print(f"Scenario: {scenario.description}")
        print(f"Hint: {scenario.hint}")
        rec = recommend(scenario)
        if rec is None:
            print("(not implemented yet)")
            continue
        print(f"-> Recommendation: {rec.choice}")
        print(f"-> Justification: {rec.justification}")


if __name__ == "__main__":
    main()
