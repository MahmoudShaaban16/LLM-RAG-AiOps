"""
Solution: Exercise 3 - Inline tools vs. an MCP server - decision framework.
"""

from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    description: str
    hint: str


@dataclass
class Recommendation:
    choice: str
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
    if scenario.name == "single_internal_calculator":
        return Recommendation(
            choice="inline",
            justification=(
                "One consumer, one owner, no need for independent updates - "
                "an inline tool definition is simpler and avoids running a "
                "second service for no benefit."
            ),
        )
    if scenario.name == "shared_company_wiki_search":
        return Recommendation(
            choice="mcp",
            justification=(
                "Multiple agents need the same tool and the owning team wants "
                "to update it on its own schedule - an MCP server lets the "
                "wiki team ship changes without redeploying every consumer."
            ),
        )
    if scenario.name == "third_party_github_server":
        return Recommendation(
            choice="mcp",
            justification=(
                "Consume the existing open-source GitHub MCP server rather "
                "than reimplementing the GitHub integration inline - apply "
                "Module 09's allow-list since it's a third-party server."
            ),
        )
    if scenario.name == "prototype_with_one_off_mock_tool":
        return Recommendation(
            choice="inline",
            justification=(
                "Short-lived, single-use prototype tool - the operational "
                "overhead of a separate MCP server isn't worth it for "
                "something likely to be deleted after the demo."
            ),
        )
    raise ValueError(f"Unknown scenario: {scenario.name}")


def main() -> None:
    for scenario in SCENARIOS:
        print(f"\n=== {scenario.name} ===")
        print(f"Scenario: {scenario.description}")
        print(f"Hint: {scenario.hint}")
        rec = recommend(scenario)
        print(f"-> Recommendation: {rec.choice}")
        print(f"-> Justification: {rec.justification}")


if __name__ == "__main__":
    main()
