"""
Exercise 3: Run a regression test with a real prompt change

TODO:
  1. Write PROMPT_OLD and PROMPT_NEW below. Make PROMPT_NEW a deliberate
     tradeoff (e.g., much shorter, to reduce output tokens/cost) compared to
     PROMPT_OLD.
  2. Run both against EVAL_DATASET, score with the judge, and print a
     comparison table (reuse run_with_prompt / score_results from
     examples/03_prompt_regression_test.py).
  3. Answer the questions at the bottom in a comment.
"""

import os
from importlib import import_module

from anthropic import Anthropic

eval_dataset_module = import_module("01_eval_dataset")
regression_module = import_module("03_prompt_regression_test")

MODEL = "claude-sonnet-4-6"
EVAL_DATASET = eval_dataset_module.EVAL_DATASET

# TODO: set these to your own old/new prompt variants
PROMPT_OLD = eval_dataset_module.SYSTEM_PROMPT
PROMPT_NEW = eval_dataset_module.SYSTEM_PROMPT  # replace with your shortened version


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # TODO: run + score both prompt variants using
    # regression_module.run_with_prompt and regression_module.score_results,
    # then print a comparison table similar to examples/03_prompt_regression_test.py.

    # TODO (bonus): run PROMPT_OLD through the full pipeline twice and compare
    # the two sets of scores. Are they identical? What does any difference
    # tell you about noise vs. signal in a small eval dataset?

    pass


# Answers (fill in after running):
# 1. Would you ship PROMPT_NEW? Why or why not?
#    ...
# 2. What additional eval cases would increase your confidence?
#    ...
# 3. (Bonus) Were the two PROMPT_OLD score runs identical? What does that
#    imply about the minimum dataset size needed to trust a small delta?
#    ...


if __name__ == "__main__":
    main()
