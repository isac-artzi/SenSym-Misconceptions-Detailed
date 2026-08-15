"""
analyze.py — turns the raw output into a confusion matrix, four numbers, and charts.

WHAT THIS DOES
--------------
  reads   results/predictions_baseline.csv
          results/predictions_misconception_aware.csv
  writes  results/metrics.csv          <- the table for your write-up
          results/comparison.png       <- the chart for your write-up
          results/confusion_matrices.png

HOW TO RUN
----------
    python misconception/analyze.py
"""

import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")           # save to file instead of opening a window
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import config
import reference
import todo

M = config.LABEL_MISCONCEPTION   # "M" — the POSITIVE class
C = config.LABEL_CORRECT         # "C" — the NEGATIVE class


# ==========================================================================
# TODO 5 — Compute the confusion matrix by hand.
# ==========================================================================
# scikit-learn does this in one line, and you'll use it that way eventually.
# Do it by hand once first. If you can't write these four counts from scratch you
# don't really have the metrics yet, and I'm definitely going to ask.
#
# Reminder, with "has a misconception" as the positive class:
#
#                          | AI predicted M | AI predicted C |
#   ----------------------------------------------------------
#   truth = M (has miscon.)|       TP       |       FN       |
#   truth = C (is correct) |       FP       |       TN       |
#
#   TP = truth is M AND prediction is M   (caught a real misconception)
#   FN = truth is M AND prediction is C   (MISSED one — the costly mistake)
#   FP = truth is C AND prediction is M   (false alarm on a correct answer)
#   TN = truth is C AND prediction is C   (correctly left a right answer alone)
#
# Fill in the four lines marked FIX ME. Until you do, the worked version runs so
# everything still completes — you just get a warning at the end.
#
# Hint — this pattern counts rows where two conditions are both true:
#     n = len(scored[(scored["ground_truth"] == M) & (scored["prediction"] == M)])
# ==========================================================================
def compute_confusion(df: pd.DataFrame) -> dict:
    """Count TP, FP, FN, TN for one condition's results."""

    # Replies we couldn't read as a clear M or C. Count them and say so — don't
    # quietly bin them or score them as correct.
    unparseable = len(df[~df["prediction"].isin([M, C])])
    scored = df[df["prediction"].isin([M, C])]

    tp = None   # FIX ME  (TODO 5a)
    fn = None   # FIX ME  (TODO 5b)
    fp = None   # FIX ME  (TODO 5c)
    tn = None   # FIX ME  (TODO 5d)

    tp = todo.pending("TODO 5a", tp, reference.count, scored, "ground_truth", "prediction", M, M)
    fn = todo.pending("TODO 5b", fn, reference.count, scored, "ground_truth", "prediction", M, C)
    fp = todo.pending("TODO 5c", fp, reference.count, scored, "ground_truth", "prediction", C, M)
    tn = todo.pending("TODO 5d", tn, reference.count, scored, "ground_truth", "prediction", C, C)

    # Safety check: the four boxes must add up to the number of scored items.
    # If this fails, one of your four lines is wrong.
    total = tp + fn + fp + tn
    if total != len(scored):
        sys.exit(
            f"\nYour four counts add up to {total}, but there are {len(scored)} "
            "scored items.\n  -> One of the conditions in TODO 5 is wrong. "
            "Check that you used & (and) not | (or), and that each row lands in "
            "exactly one box."
        )

    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "unparseable": unparseable}


def compute_metrics(cm: dict) -> dict:
    """
    Turn the four counts into the four numbers.

    Written for you — but read the formulas and make sure you can say each one
    out loud in plain English (there's a table in docs/01_PROJECT_SUMMARY.md).

    Note the `if denominator else 0.0` guards. Dividing by zero crashes Python,
    and the denominator genuinely can be zero here — precision is undefined if
    the model never says M at all. Reporting 0.0 with a note is the safe move.
    """
    tp, fp, fn, tn = cm["TP"], cm["FP"], cm["FN"], cm["TN"]
    total = tp + fp + fn + tn

    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "accuracy": round(accuracy, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
    }


def cross_check_with_sklearn(df: pd.DataFrame, cm: dict, metrics: dict) -> None:
    """
    Check your hand-counted numbers against scikit-learn.

    Good habit in general: whenever you implement something yourself, check it
    against a library that's already trusted. If they disagree, it's almost
    always you.
    """
    try:
        from sklearn.metrics import confusion_matrix, precision_score, recall_score
    except ImportError:
        print("  (scikit-learn not installed — skipping cross-check)")
        return

    scored = df[df["prediction"].isin([M, C])]
    if len(scored) == 0:
        return

    # labels=[C, M] puts the negative class first, which is sklearn's convention —
    # the matrix it returns is [[TN, FP], [FN, TP]]
    sk = confusion_matrix(scored["ground_truth"], scored["prediction"], labels=[C, M])
    tn_sk, fp_sk, fn_sk, tp_sk = sk.ravel()

    ok = (tn_sk, fp_sk, fn_sk, tp_sk) == (cm["TN"], cm["FP"], cm["FN"], cm["TP"])
    print(f"  scikit-learn cross-check: {'MATCH ✓' if ok else 'MISMATCH ✗ — recheck TODO 5'}")

    if ok:
        p = precision_score(scored["ground_truth"], scored["prediction"],
                            pos_label=M, zero_division=0)
        r = recall_score(scored["ground_truth"], scored["prediction"],
                         pos_label=M, zero_division=0)
        print(f"  sklearn precision={p:.3f} recall={r:.3f} "
              f"(yours: {metrics['precision']:.3f} / {metrics['recall']:.3f})")


def plot_confusion_matrices(all_cms: dict, path: Path) -> None:
    """Draw one 2x2 grid per condition, side by side."""
    n = len(all_cms)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    if n == 1:
        axes = [axes]

    for ax, (cond, cm) in zip(axes, all_cms.items()):
        grid = [[cm["TP"], cm["FN"]],
                [cm["FP"], cm["TN"]]]
        ax.imshow(grid, cmap="Blues", vmin=0)

        labels = [["TP", "FN"], ["FP", "TN"]]
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{labels[i][j]}\n{grid[i][j]}",
                        ha="center", va="center", fontsize=14, color="black")

        ax.set_xticks([0, 1], ["predicted M", "predicted C"])
        ax.set_yticks([0, 1], ["actual M", "actual C"])
        ax.set_title(cond.replace("_", " "))

    fig.suptitle("Confusion matrices (positive class = has a misconception)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_comparison(rows: list, path: Path) -> None:
    """Grouped bar chart comparing the four numbers across both prompts."""
    metric_names = ["accuracy", "precision", "recall", "f1"]
    conditions = [r["condition"] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    width = 0.8 / max(len(conditions), 1)

    for k, r in enumerate(rows):
        xs = [i + k * width for i in range(len(metric_names))]
        ys = [r[m] for m in metric_names]
        bars = ax.bar(xs, ys, width=width, label=r["condition"].replace("_", " "))
        for b, y in zip(bars, ys):
            ax.text(b.get_x() + b.get_width() / 2, y + 0.02, f"{y:.2f}",
                    ha="center", fontsize=9)

    ax.set_xticks([i + width * (len(conditions) - 1) / 2 for i in range(len(metric_names))],
                  metric_names)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("score")
    ax.set_title("Spotting misconceptions: plain prompt vs. prompt with the list")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    rows = []
    all_cms = {}

    # The two pre-registered conditions are required. The decoy is analysed too
    # if it was run, and silently skipped if it wasn't — running the placebo is
    # optional (see DECOY_CONDITION in config.py).
    for condition in config.ALL_CONDITIONS:
        path = config.RESULTS_DIR / f"predictions_{condition}.csv"
        if not path.exists():
            if condition == config.DECOY_CONDITION:
                continue
            sys.exit(f"ERROR: {path} not found. Run  python misconception/run_experiment.py  first.")

        df = pd.read_csv(path)
        cm = compute_confusion(df)
        metrics = compute_metrics(cm)

        print(f"\n=== {condition} ===")
        print(f"  TP={cm['TP']}  FP={cm['FP']}  FN={cm['FN']}  TN={cm['TN']}"
              f"  (unparseable: {cm['unparseable']})")
        print(f"  accuracy={metrics['accuracy']}  precision={metrics['precision']}"
              f"  recall={metrics['recall']}  f1={metrics['f1']}")
        cross_check_with_sklearn(df, cm, metrics)

        all_cms[condition] = cm
        rows.append({"condition": condition, **cm, **metrics})

    out = pd.DataFrame(rows)
    out.to_csv(config.RESULTS_DIR / "metrics.csv", index=False)

    plot_confusion_matrices(all_cms, config.RESULTS_DIR / "confusion_matrices.png")
    plot_comparison(rows, config.RESULTS_DIR / "comparison.png")

    print(f"\nSaved -> {config.RESULTS_DIR / 'metrics.csv'}")
    print(f"Saved -> {config.RESULTS_DIR / 'confusion_matrices.png'}")
    print(f"Saved -> {config.RESULTS_DIR / 'comparison.png'}")

    # ======================================================================
    # TODO 6 — Work out what it means.
    # ======================================================================
    # A computer can produce numbers. Only you can say what they mean.
    # Open results/metrics.csv and results/comparison.png, then answer these in
    # a new file, docs/06_MY_FINDINGS.md:
    #
    #   1. Which prompt had higher RECALL? By how much?
    #   2. Which had higher PRECISION? Did one go up while the other went down?
    #      That trade-off is really common and worth talking about.
    #   3. Look at the FALSE NEGATIVES — the misconceptions it missed. Open the
    #      predictions CSV and actually read them. Anything in common? Subtler?
    #      Longer? All about one topic?
    #      *** This is usually the most interesting part. Don't skip it. ***
    #   4. Read the model_reason column for a few it got wrong. Was it wrong for
    #      a sensible reason or a nonsense one?
    #   5. With only 40 items, how sure can you really be? What would make you
    #      more sure?
    #
    # docs/05_WRITING_UP_RESULTS.md has help turning these into sentences.
    # ======================================================================
    todo.report()
    print("Now do TODO 6: open results/ and write up what you see. "
          "See docs/05_WRITING_UP_RESULTS.md")


if __name__ == "__main__":
    main()
