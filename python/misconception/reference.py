"""
reference.py — working versions of every TODO in this project.

⚠️  DON'T READ THIS UNTIL YOU'VE HAD A GO YOURSELF.  ⚠️

It exists so everything runs end to end the moment you clone the repo. Each
function here is what `todo.pending()` falls back to when the matching TODO
isn't filled in yet.

Looking after you're genuinely stuck is fine and normal — that's what it's for.
Looking *first* costs you the only part of this that actually teaches you
anything. Your call; nobody's watching.

Every function here is four lines or fewer. That's on purpose: the TODOs are
small, and if one feels enormous you've probably misread it.
"""

from typing import List


# ── TODO 2 / 3 / 4a ────────────────────────────────────────────────────────
def build_prompt(condition: str, response_text: str, misconception_list: List[str]) -> str:
    """TODO 4a — pick the right prompt builder for this condition."""
    from prompts import (build_baseline_prompt, build_misconception_aware_prompt,
                         build_decoy_prompt)
    if condition == "baseline":
        return build_baseline_prompt(response_text)
    if condition == "decoy":
        return build_decoy_prompt(response_text, misconception_list)
    return build_misconception_aware_prompt(response_text, misconception_list)


# ── TODO 4b ────────────────────────────────────────────────────────────────
def ask_model(ask_fn, prompt: str) -> str:
    """TODO 4b — send the prompt to the model."""
    return ask_fn(prompt)


# ── TODO 5a–5d ─────────────────────────────────────────────────────────────
def count(scored, truth_col: str, pred_col: str, truth_val: str, pred_val: str) -> int:
    """
    TODO 5a-5d — count the rows where your label is `truth_val` AND the model
    said `pred_val`.

    This one function covers all four boxes of the confusion matrix:
        TP = count(df, "ground_truth", "prediction", "M", "M")
        FN = count(df, "ground_truth", "prediction", "M", "C")
        FP = count(df, "ground_truth", "prediction", "C", "M")
        TN = count(df, "ground_truth", "prediction", "C", "C")
    """
    return len(scored[(scored[truth_col] == truth_val) & (scored[pred_col] == pred_val)])
