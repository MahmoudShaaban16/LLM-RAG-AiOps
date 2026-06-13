"""
Exercise 2: Apply the decision framework

For each scenario below, fill in:
  - `recommendation`: one of "prompting", "rag", "tool_use", "fine_tuning"
  - `justification`: 2-3 sentences referencing Section 1 of the module README

For any scenario where you choose "fine_tuning", also fill in
`try_first` describing what you'd attempt before committing to it.
"""

SCENARIOS = [
    {
        "id": "scenario_1",
        "description": (
            "A customer support bot frequently gives answers that are factually "
            "correct about general SaaS concepts, but wrong about this "
            "company's specific pricing tiers, which change every quarter."
        ),
        "recommendation": None,  # TODO
        "justification": None,  # TODO
        "try_first": None,
    },
    {
        "id": "scenario_2",
        "description": (
            "An internal tool summarizes legal contracts. Legal wants every "
            "summary to follow an exact 5-section template (Parties, Term, "
            "Obligations, Termination, Risks) with consistent headers, and "
            "the current prompt with a 5-example few-shot block works about "
            "85% of the time but sometimes drops a section or renames a header."
        ),
        "recommendation": None,  # TODO
        "justification": None,  # TODO
        "try_first": None,
    },
    {
        "id": "scenario_3",
        "description": (
            "A product team wants the assistant to be able to actually create "
            "a ticket in their issue tracker when a user reports a bug, not "
            "just describe what ticket *should* be created."
        ),
        "recommendation": None,  # TODO
        "justification": None,  # TODO
        "try_first": None,
    },
    {
        "id": "scenario_4",
        "description": (
            "A high-volume classification pipeline (2M requests/day) currently "
            "uses a ~1,500 token few-shot prompt to classify support tickets "
            "into 12 categories with 94% accuracy (measured against a labeled "
            "eval set). The team has 50,000 historically labeled tickets and "
            "wants to reduce per-request cost."
        ),
        "recommendation": None,  # TODO
        "justification": None,  # TODO
        "try_first": None,
    },
]


def main() -> None:
    for scenario in SCENARIOS:
        print(f"=== {scenario['id']} ===")
        print(scenario["description"])
        print(f"Recommendation: {scenario['recommendation']}")
        print(f"Justification:  {scenario['justification']}")
        if scenario["recommendation"] == "fine_tuning":
            print(f"Try first:      {scenario['try_first']}")
        print()


if __name__ == "__main__":
    main()
