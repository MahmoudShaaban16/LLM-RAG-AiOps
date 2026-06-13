"""
Solution: Exercise 2 - Apply the decision framework
"""

SCENARIOS = {
    "startup_prototype": {
        "description": "A startup prototyping a new AI feature, uncertain of demand",
        "high_steady_volume": False,
        "data_residency_required": False,
        "open_weight_model_sufficient": False,  # unknown yet - no evals exist
        "has_ml_infra_expertise": False,
        "latency_insensitive_or_fallback": False,
    },
    "healthcare_compliance": {
        "description": "A healthcare company that cannot send patient data to third-party APIs",
        "high_steady_volume": False,
        "data_residency_required": True,
        "open_weight_model_sufficient": True,  # assume evaluated and acceptable
        "has_ml_infra_expertise": True,  # required, given the constraint
        "latency_insensitive_or_fallback": False,
    },
    "content_moderation": {
        "description": "A high-volume content-moderation classifier running on every user post",
        "high_steady_volume": True,
        "data_residency_required": False,
        "open_weight_model_sufficient": True,  # classification tasks often work well with smaller models
        "has_ml_infra_expertise": True,
        "latency_insensitive_or_fallback": True,  # can fall back to a rules check or queue
    },
    "coding_assistant": {
        "description": "A coding assistant that needs the strongest available reasoning model",
        "high_steady_volume": True,
        "data_residency_required": False,
        "open_weight_model_sufficient": False,  # needs frontier reasoning quality
        "has_ml_infra_expertise": True,
        "latency_insensitive_or_fallback": False,
    },
}


def recommend(scenario: dict) -> str:
    # Hard requirement: if an open-weight model isn't good enough, self-hosting
    # isn't viable regardless of other factors.
    if not scenario["open_weight_model_sufficient"]:
        return "favor managed API"

    # Hard requirement: compliance can force self-hosting even at low volume.
    if scenario["data_residency_required"]:
        return "favor self-hosting" if scenario["has_ml_infra_expertise"] else "hybrid - investigate further"

    favorable = sum(
        scenario[k]
        for k in (
            "high_steady_volume",
            "has_ml_infra_expertise",
            "latency_insensitive_or_fallback",
        )
    )

    if favorable >= 2:
        return "favor self-hosting"
    if favorable == 0:
        return "favor managed API"
    return "hybrid - investigate further"


def main() -> None:
    for name, scenario in SCENARIOS.items():
        print(f"{name}: {scenario['description']}")
        print(f"  -> {recommend(scenario)}")
        print()


if __name__ == "__main__":
    main()


# Discussion:
#
# - startup_prototype: "favor managed API" - no evals exist yet to know if an
#   open-weight model is sufficient, volume is unknown, and the team's time is
#   better spent validating the product than standing up GPU infrastructure.
#   This can (and should) be revisited once the feature has real usage data.
# - healthcare_compliance: data residency may FORCE self-hosting even if the
#   cost math alone wouldn't favor it - this is the "hard requirement" case
#   from the README, not a pure cost tradeoff.
# - content_moderation: classic self-hosting candidate - high volume, narrow
#   task, evaluable, and a fallback (e.g., a simpler rules-based check or a
#   review queue) exists if the self-hosted server is briefly unavailable.
# - coding_assistant: "favor managed API" - the whole point is frontier
#   reasoning/tool-use quality, which is exactly what self-hosting trades away.
#
# Revisiting over time: the cleanest way to avoid a rewrite is to keep the
# *client-side* interface stable (e.g., a thin wrapper function like
# `triage_ticket()` in Module 10) and swap the implementation behind it once
# evals support the change - the rest of the application shouldn't need to
# know which backend served the request.
