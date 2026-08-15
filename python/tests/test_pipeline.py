"""
Automated checks for this project.

WHAT TESTS ARE FOR (worth knowing about generally)
--------------------------------------------------
A test is a tiny program that checks another program still works. You run them
after every change. If you break something, you find out in two seconds instead
of two weeks — or worse, instead of finding out from a wrong number in your
write-up.

Run them with:

    pytest -q

The approach here: build small bits of data where you already know the right
answer, then check the code agrees. That's the standard way to test code that
calculates things. If you can't check your numbers are right, you can't trust
them.

You don't need to write any tests for this. But have a look through — the
"work it out by hand, then check the code matches" pattern is worth stealing.
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "misconception"
sys.path.insert(0, str(SRC))

import analyze  # noqa: E402
import config  # noqa: E402
import llm_client  # noqa: E402
import prompts  # noqa: E402
import todo  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# The arithmetic. These functions just do maths, so they're easy to pin down.
# ─────────────────────────────────────────────────────────────────────────────
def test_metrics_match_hand_calculation():
    cm = {"TP": 8, "FP": 2, "FN": 4, "TN": 6}
    m = analyze.compute_metrics(cm)
    # Worked out by hand: accuracy (8+6)/20 = 0.7 · precision 8/10 = 0.8 · recall 8/12 = 0.667
    assert m["accuracy"] == 0.7
    assert m["precision"] == 0.8
    assert m["recall"] == pytest.approx(0.667, abs=1e-3)
    assert m["f1"] == pytest.approx(0.727, abs=1e-3)


def test_metrics_never_divide_by_zero():
    """A model that says 'correct' to everything mustn't crash the analysis."""
    m = analyze.compute_metrics({"TP": 0, "FP": 0, "FN": 20, "TN": 20})
    assert m["precision"] == 0.0 and m["recall"] == 0.0 and m["f1"] == 0.0
    assert m["accuracy"] == 0.5


def test_all_zero_counts_are_survivable():
    assert analyze.compute_metrics({"TP": 0, "FP": 0, "FN": 0, "TN": 0})["accuracy"] == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Confusion matrix
# ─────────────────────────────────────────────────────────────────────────────
def _frame(pairs):
    return pd.DataFrame(
        [{"ground_truth": t, "prediction": p} for t, p in pairs]
    )


def test_confusion_counts_land_in_the_right_boxes():
    df = _frame([("M", "M"), ("M", "M"), ("M", "C"), ("C", "M"), ("C", "C"), ("C", "C")])
    cm = analyze.compute_confusion(df)
    assert (cm["TP"], cm["FN"], cm["FP"], cm["TN"]) == (2, 1, 1, 2)
    assert cm["unparseable"] == 0


def test_unparseable_predictions_are_excluded_not_guessed():
    """A garbled reply gets reported, never quietly scored as correct."""
    df = _frame([("M", "M"), ("M", "?"), ("C", "C")])
    cm = analyze.compute_confusion(df)
    assert cm["unparseable"] == 1
    assert cm["TP"] + cm["FN"] + cm["FP"] + cm["TN"] == 2


def test_confusion_agrees_with_sklearn():
    """Check our counts against the library, same as analyze.py does."""
    sklearn_metrics = pytest.importorskip("sklearn.metrics")
    pairs = [("M", "M")] * 7 + [("M", "C")] * 3 + [("C", "M")] * 2 + [("C", "C")] * 8
    df = _frame(pairs)
    cm = analyze.compute_confusion(df)
    tn, fp, fn, tp = sklearn_metrics.confusion_matrix(
        df["ground_truth"], df["prediction"], labels=["C", "M"]
    ).ravel()
    assert (tp, fp, fn, tn) == (cm["TP"], cm["FP"], cm["FN"], cm["TN"])


# ─────────────────────────────────────────────────────────────────────────────
# Reading the model's reply. Small models are sloppy, so this has to be
# forgiving in the right places and strict in the right places.
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("reply,expected", [
    ("VERDICT: M\nREASON: it says always", "M"),
    ("VERDICT: C\nREASON: correct", "C"),
    ("verdict: **M**", "M"),
    ("M", "M"),
    ("This response is correct.", "C"),
    ("banana", "?"),
])
def test_parse_verdict(reply, expected):
    assert llm_client.parse_verdict(reply) == expected


# ─────────────────────────────────────────────────────────────────────────────
# The prompts. Whether the comparison is fair depends on these holding.
# ─────────────────────────────────────────────────────────────────────────────
MISC = ["Long passwords are always strong", "MFA makes an account unhackable"]


def test_baseline_prompt_does_not_leak_the_misconception_list():
    """
    If the plain prompt mentioned specific misconceptions, it wouldn't be plain
    any more, and the whole comparison would stop meaning anything.
    """
    p = prompts.build_baseline_prompt("my password is 24 characters")
    for m in MISC:
        assert m.lower() not in p.lower()


def test_aware_prompt_contains_every_misconception():
    p = prompts.build_misconception_aware_prompt("my password is 24 characters", MISC)
    for m in MISC:
        assert m in p


def test_both_prompts_share_the_same_output_format():
    """The only difference between the two should be the misconception list."""
    a = prompts.build_baseline_prompt("x")
    b = prompts.build_misconception_aware_prompt("x", MISC)
    assert prompts.OUTPUT_FORMAT_INSTRUCTION in a
    assert prompts.OUTPUT_FORMAT_INSTRUCTION in b


def test_unknown_condition_is_rejected_loudly():
    with pytest.raises(ValueError):
        prompts.build_prompt("something_else", "x", MISC)


# ─────────────────────────────────────────────────────────────────────────────
# The TODO fallback machinery
# ─────────────────────────────────────────────────────────────────────────────
def test_pending_uses_your_value_when_you_have_filled_it_in():
    todo.reset()
    assert todo.pending("TODO 9z", "mine", lambda: "reference") == "mine"
    assert not todo.any_pending()


def test_pending_falls_back_and_records_when_you_have_not():
    todo.reset()
    assert todo.pending("TODO 9z", None, lambda: "reference") == "reference"
    assert todo.any_pending()
    todo.reset()


# ─────────────────────────────────────────────────────────────────────────────
# End-to-end check — the one CI really cares about.
# ─────────────────────────────────────────────────────────────────────────────
def test_full_pipeline_runs_on_a_fresh_clone(tmp_path, monkeypatch):
    """
    Runs the actual scripts the same way you would, with the fake model and the
    demo answers. This is what proves "clone it and it runs".
    """
    monkeypatch.setenv("MISCONCEPTION_PILOT_RESULTS", str(tmp_path))

    run = subprocess.run(
        [sys.executable, str(SRC / "run_experiment.py"), "--mock", "--sample"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "MOCK MODE" in run.stdout

    ana = subprocess.run(
        [sys.executable, str(SRC / "analyze.py")],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert ana.returncode == 0, ana.stdout + ana.stderr

    for f in ["predictions_baseline.csv", "predictions_misconception_aware.csv",
              "metrics.csv", "comparison.png", "confusion_matrices.png"]:
        assert (config.RESULTS_DIR / f).exists(), f"{f} was not produced"

    metrics = pd.read_csv(config.RESULTS_DIR / "metrics.csv")
    assert set(metrics["condition"]) == set(config.CONDITIONS)
    for col in ["accuracy", "precision", "recall", "f1"]:
        assert metrics[col].between(0, 1).all()
