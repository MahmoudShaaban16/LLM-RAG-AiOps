"""
Exercise 2: Apply the decision framework

TODO:
  1. For each scenario, fill in the 5 framework answers (True/False) for:
       - high_steady_volume
       - data_residency_required
       - open_weight_model_sufficient
       - has_ml_infra_expertise
       - latency_insensitive_or_fallback
  2. Implement recommend(scenario) -> str returning "favor self-hosting",
     "favor managed API", or "hybrid - investigate further" based on how
     many answers are True.
  3. Print the recommendation + reasoning for each scenario.
"""

SCENARIOS = {
    "startup_prototype": {
        "description": "A startup prototyping a new AI feature, uncertain of demand",
        # TODO: fill in the 5 booleans
    },
    "healthcare_compliance": {
        "description": "A healthcare company that cannot send patient data to third-party APIs",
        # TODO: fill in the 5 booleans
    },
    "content_moderation": {
        "description": "A high-volume content-moderation classifier running on every user post",
        # TODO: fill in the 5 booleans
    },
    "coding_assistant": {
        "description": "A coding assistant that needs the strongest available reasoning model",
        # TODO: fill in the 5 booleans
    },
}


def recommend(scenario: dict) -> str:
    # TODO: implement based on the framework table in the module README
    pass


def main() -> None:
    for name, scenario in SCENARIOS.items():
        print(f"{name}: {scenario['description']}")
        # TODO: print recommend(scenario) and your reasoning
        print()


if __name__ == "__main__":
    main()
