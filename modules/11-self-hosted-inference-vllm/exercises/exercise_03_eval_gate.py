"""
Exercise 3: Eval-gate a self-hosting migration

TODO:
  1. In a comment, sketch the eval gate for migrating ticket categorization
     from the Anthropic API to a self-hosted vLLM model: what would you
     compare (old model vs. new model on what dataset), and what counts as
     a regression?
  2. Implement should_migrate(old_scores, new_scores, threshold) -> bool.
  3. Test it with a few example score lists.
"""

# TODO 1: sketch the eval gate here as a comment, e.g.
# - Run the Module 06 eval dataset (representative tickets with expected
#   category) through both the old (Anthropic API) and new (self-hosted)
#   pipelines.
# - Score each with the same LLM-as-judge rubric (or exact-match accuracy
#   for the category field).
# - A regression is a meaningful drop in average score (or accuracy) on the
#   new model vs. the old one - "meaningful" defined by `threshold` below.


def should_migrate(old_scores: list[float], new_scores: list[float], threshold: float) -> bool:
    # TODO: return True only if avg(new_scores) >= avg(old_scores) - threshold
    pass


def main() -> None:
    old_scores = [4.5, 4.0, 4.8, 3.9, 4.2]
    new_scores_ok = [4.3, 4.1, 4.6, 3.8, 4.0]
    new_scores_regressed = [3.0, 2.5, 3.2, 2.8, 2.9]

    # TODO: call should_migrate for both new_scores examples and print results
    pass


if __name__ == "__main__":
    main()
