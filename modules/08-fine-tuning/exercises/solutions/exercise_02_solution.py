"""
Solution: Exercise 2 - Apply the decision framework
"""

SCENARIOS = [
    {
        "id": "scenario_1",
        "description": (
            "A customer support bot frequently gives answers that are factually "
            "correct about general SaaS concepts, but wrong about this "
            "company's specific pricing tiers, which change every quarter."
        ),
        "recommendation": "rag",
        "justification": (
            "This is a knowledge-freshness problem, not a style/format problem "
            "— the model needs access to the *current* pricing data. Fine-tuning "
            "on pricing Q&A would bake in today's prices and go stale next "
            "quarter, requiring retraining every cycle. A retrieval index over "
            "the current pricing page can be updated in minutes."
        ),
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
        "recommendation": "tool_use",
        "justification": (
            "Before considering fine-tuning, this is a strong candidate for "
            "structured output: define a tool/schema with the 5 sections as "
            "required fields (Parties, Term, Obligations, Termination, Risks). "
            "A schema with `required` fields makes it structurally impossible "
            "for the model to silently drop or rename a section, which directly "
            "fixes the 85% failure mode without any new model artifact."
        ),
        "try_first": None,
    },
    {
        "id": "scenario_3",
        "description": (
            "A product team wants the assistant to be able to actually create "
            "a ticket in their issue tracker when a user reports a bug, not "
            "just describe what ticket *should* be created."
        ),
        "recommendation": "tool_use",
        "justification": (
            "This is a 'the model needs to take an action' problem, which is "
            "exactly what tool use is for (Module 03). Give the model a "
            "`create_ticket` tool with a defined input schema; the application "
            "executes the actual API call to the issue tracker. No new model "
            "weights are needed — this is an integration, not a behavior-shaping "
            "problem."
        ),
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
        "recommendation": "fine_tuning",
        "justification": (
            "This is the closest fit to fine-tuning's strengths: a narrow, "
            "well-defined classification task, a large labeled dataset already "
            "exists (50,000 examples), the task is measured (94% accuracy on an "
            "eval set gives a clear baseline), and the volume (2M req/day) means "
            "removing a 1,500-token prompt from every request produces real "
            "savings. This is 'shaving tokens off every request' from the "
            "module README's checklist."
        ),
        "try_first": (
            "Confirm a smaller model (e.g., Haiku-tier) with the existing "
            "few-shot prompt can't hit similar accuracy at lower cost first — "
            "that's a much smaller change. If accuracy holds with a cheaper "
            "model, that may be enough without fine-tuning at all. Only pursue "
            "fine-tuning if a cost/accuracy gap remains after that, and confirm "
            "your provider offers fine-tuning for the model tier you need."
        ),
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
