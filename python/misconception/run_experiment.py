"""
run_experiment.py — runs the model over every answer, with both prompts.

WHAT THIS DOES
--------------
  for each condition (baseline, misconception_aware):
      for each of your 40 answers:
          build the prompt
          ask the model
          write down what it said

It saves the raw output to results/predictions_<condition>.csv and then STOPS.
It doesn't work out any numbers — that's analyze.py's job. Keeping "collect the
data" and "look at the data" in separate files is worth doing: you can redo the
analysis without waiting for the model again, and the raw output is always
sitting on disk if you need it.

HOW TO RUN
----------
    python misconception/run_experiment.py --mock     <- fake model, instant, do this first
    python misconception/run_experiment.py            <- the real thing
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

import config
import reference
import todo
from prompts import build_prompt
from llm_client import ask_llm, ask_llm_mock, parse_verdict, parse_reason, LLMError


def load_misconceptions(path=None) -> list:
    """Read data/misconceptions.csv and return the list of misconception statements."""
    path = path or config.MISCONCEPTIONS_FILE
    if not path.exists():
        sys.exit(f"ERROR: {path} not found.")

    df = pd.read_csv(path)

    # Drop the template placeholder rows so you get a clear error if you forgot
    # to fill the file in, instead of silently running on example data.
    df = df[~df["statement"].astype(str).str.startswith("<")]

    if len(df) == 0:
        sys.exit(
            "ERROR: data/misconceptions.csv has no real rows yet.\n"
            "  -> Fill in your 10 chosen misconceptions (see TODO A in "
            "docs/03_TODO_CHECKLIST.md),\n"
            "     or run with --sample to use the demo answers in data/sample/."
        )
    return df["statement"].tolist()


def load_responses(path=None) -> pd.DataFrame:
    """
    Read data/responses.csv — your 40 hand-written, hand-labeled answers.

    Also sanity-checks the file, because one typo'd label quietly ruins a whole
    run and you'd never notice.
    """
    path = path or config.RESPONSES_FILE
    if not path.exists():
        sys.exit(f"ERROR: {path} not found.")

    df = pd.read_csv(path)
    df = df[~df["response_text"].astype(str).str.startswith("<")]

    if len(df) == 0:
        sys.exit(
            "ERROR: data/responses.csv has no real rows yet.\n"
            "  -> Write your 40 answers (see TODO B in "
            "docs/03_TODO_CHECKLIST.md),\n"
            "     or run with --sample to use the demo answers in data/sample/."
        )

    # ---- sanity checks: catch typos before you waste a run ----
    valid = {config.LABEL_MISCONCEPTION, config.LABEL_CORRECT}
    bad = df[~df["ground_truth"].isin(valid)]
    if len(bad) > 0:
        sys.exit(
            f"ERROR: {len(bad)} row(s) have a ground_truth that isn't 'M' or 'C'.\n"
            f"  First offender is response_id {bad.iloc[0]['response_id']!r} "
            f"with value {bad.iloc[0]['ground_truth']!r}.\n"
            "  -> Check for lowercase letters or stray spaces."
        )

    if df["response_id"].duplicated().any():
        dupes = df[df["response_id"].duplicated()]["response_id"].tolist()
        sys.exit(f"ERROR: duplicate response_id values: {dupes}")

    n_m = (df["ground_truth"] == config.LABEL_MISCONCEPTION).sum()
    n_c = (df["ground_truth"] == config.LABEL_CORRECT).sum()
    print(f"Loaded {len(df)} answers  ({n_m} misconception, {n_c} correct)")

    # Roughly even numbers make accuracy mean something. If it's badly lopsided,
    # a model that always says "M" could score 80% and look great while being
    # completely useless.
    if n_m == 0 or n_c == 0:
        sys.exit("ERROR: you need BOTH M and C answers to build a confusion matrix.")
    if abs(n_m - n_c) > 0.3 * len(df):
        print("  ! Heads up: your M and C counts are quite uneven. Aim for roughly 50/50.")

    return df


def run_condition(condition: str, responses: pd.DataFrame,
                  misconceptions: list, use_mock: bool) -> pd.DataFrame:
    """
    Run every answer through the model once, with one of the two prompts.

    ----------------------------------------------------------------------
    TODO 4 — Complete the loop body.
    ----------------------------------------------------------------------
    The structure is written for you. Find the two lines marked `# >>> YOU:`
    below and fill them in. They are one line each.

    Until you do, the worked version runs instead so everything still works end
    to end — you just get a warning at the end saying which TODOs aren't yours
    yet. Nothing crashes.

    Hint 1: you already imported a function called `build_prompt`. Look at its
            definition in prompts.py to see what arguments it wants.
    Hint 2: `ask` (defined just below) is the function that sends a prompt to
            the model. Give it the prompt, get back raw text.
    ----------------------------------------------------------------------
    """
    ask = ask_llm_mock if use_mock else ask_llm
    rows = []

    print(f"\n--- Condition: {condition} ---")
    start = time.time()

    for i, item in responses.iterrows():
        # >>> YOU (TODO 4a): build the prompt for this item.
        # Replace `None` with a call to build_prompt(...).
        prompt = None  # <-- FIX ME
        prompt = todo.pending("TODO 4a", prompt, reference.build_prompt,
                              condition, item["response_text"], misconceptions)

        # >>> YOU (TODO 4b): send the prompt to the model and store the reply.
        # Replace `None` with a call to ask(...).
        raw_reply = None  # <-- FIX ME
        raw_reply = todo.pending("TODO 4b", raw_reply, reference.ask_model, ask, prompt)

        # --- everything below is done for you ---
        verdict = parse_verdict(raw_reply)
        reason = parse_reason(raw_reply)

        rows.append({
            "response_id": item["response_id"],
            "misconception_id": item.get("misconception_id", ""),
            "response_text": item["response_text"],
            "ground_truth": item["ground_truth"],
            "prediction": verdict,
            "model_reason": reason,
            "raw_reply": raw_reply.replace("\n", " | "),
            "condition": condition,
        })

        # Live progress, so you can tell it hasn't frozen.
        mark = "." if verdict == item["ground_truth"] else "X"
        print(mark, end="", flush=True)

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s ({elapsed / max(len(responses), 1):.1f}s per item)")

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Run the misconception-detection experiment.")
    parser.add_argument("--mock", action="store_true",
                        help="Use a fake model. Nothing to install. Try this first.")
    parser.add_argument("--sample", action="store_true",
                        help="Use the demo answers in data/sample/ instead of your own. "
                             "Lets a fresh clone run before you've written anything.")
    parser.add_argument("--decoy", action="store_true",
                        help="Also run the pre-registered placebo condition: the same "
                             "catalogue prompt, but with a catalogue of PHYSICS "
                             "misconceptions. Answers 'did the catalogue help, or did "
                             "any longer prompt help?'. Adds ~50%% to the run time. "
                             "See DECOY_CONDITION in config.py.")
    parser.add_argument("--probe", type=int, metavar="N", default=None,
                        help="Run on only the first N responses. Use --probe 10 on your "
                             "first ten items, BEFORE writing the other thirty: if the "
                             "model scores 10/10 under both prompts your items are too "
                             "easy, and you want to find that out now. See the Phase 3 "
                             "page.")
    args = parser.parse_args()

    if args.mock:
        print("*** MOCK MODE — these numbers are FAKE. Never report them. ***")
    else:
        print(f"Using model: {config.MODEL_NAME} at temperature {config.TEMPERATURE}")

    if args.sample:
        print("*** SAMPLE DATA — 12 demo answers, NOT yours. ***")
        mis_path, resp_path = config.SAMPLE_MISCONCEPTIONS, config.SAMPLE_RESPONSES
    else:
        mis_path, resp_path = config.MISCONCEPTIONS_FILE, config.RESPONSES_FILE

    misconceptions = load_misconceptions(mis_path)
    responses = load_responses(resp_path)
    print(f"Loaded {len(misconceptions)} misconceptions")

    conditions = list(config.CONDITIONS)
    decoys = None
    if args.decoy:
        decoys = load_misconceptions(config.DECOY_MISCONCEPTIONS_FILE)
        conditions.append(config.DECOY_CONDITION)
        print(f"Loaded {len(decoys)} decoy misconceptions (placebo condition ON)")

        # The placebo only controls for prompt length if the two catalogues are
        # comparable in length. Print both so you can see it rather than assume
        # it — and so you can say so in Methods.
        real_len = sum(len(m) for m in misconceptions)
        decoy_len = sum(len(d) for d in decoys)
        ratio = decoy_len / real_len if real_len else 0
        print(f"  catalogue size: yours {real_len} chars / {len(misconceptions)} items, "
              f"decoy {decoy_len} chars / {len(decoys)} items  (decoy is {ratio:.2f}x)")
        if not 0.7 <= ratio <= 1.4:
            print("  ! The two catalogues differ noticeably in length, so the decoy is")
            print("    not cleanly controlling for prompt length. Either even them up or")
            print("    say so in Limitations. (Expected while your file is still short.)")

    if args.probe is not None:
        n = max(1, args.probe)
        responses = responses.head(n)
        print(f"\n*** PROBE MODE — first {len(responses)} responses only. ***")
        print("    This is the early-warning check, not a result. You are looking for")
        print("    a score that is NOT perfect. See the Phase 3 page.")

    for condition in conditions:
        # The decoy condition sees the decoy catalogue; everything else sees
        # yours. build_prompt() doesn't know or care which file a list came from.
        catalogue = decoys if condition == config.DECOY_CONDITION else misconceptions
        try:
            df = run_condition(condition, responses, catalogue, args.mock)
        except LLMError as e:
            sys.exit(f"\nLLM ERROR:\n{e}")

        out = config.RESULTS_DIR / f"predictions_{condition}.csv"
        df.to_csv(out, index=False)
        print(f"Saved -> {out}")

    todo.report()

    if args.probe is not None:
        _probe_verdict(conditions, len(responses))
        return

    print("All conditions complete. Next step:  python misconception/analyze.py")


def _probe_verdict(conditions, n):
    """
    The early-warning check from Phase 3.

    You run this on your FIRST TEN items, before writing the other thirty. A
    perfect score here is bad news, not good news: it means a model with no help
    already separates your M items from your C items, so there is no room left
    for the misconception catalogue to show any effect. That is the ceiling
    effect, and finding it now costs you ten items instead of forty.

    This deliberately prints no metrics. It is a go / no-go signal on the
    dataset, and turning it into a number invites you to report it, which you
    must not do — ten items chosen by you is not a result.
    """
    print("\n" + "=" * 70)
    print("PROBE RESULT")
    print("=" * 70)
    perfect = []
    for condition in conditions:
        path = config.RESULTS_DIR / f"predictions_{condition}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        hits = int((df["prediction"] == df["ground_truth"]).sum())
        print(f"  {condition:22s} {hits}/{len(df)} correct")
        if hits == len(df):
            perfect.append(condition)

    if len(perfect) >= 2:
        print("\n  ⚠  PERFECT UNDER MORE THAN ONE PROMPT.")
        print("     Your items are separable without any help, so the catalogue has")
        print("     nothing left to add and both conditions will sit at the ceiling.")
        print("     STOP. Go and write harder items before you write the other thirty:")
        print("       - an M that reads as reasonable and hedged")
        print("       - a C that reads as overconfident")
        print("     Then run this probe again.")
    elif perfect:
        print(f"\n  Perfect under {perfect[0]} only. Not fatal, but thin. Aim for at")
        print("  least two or three items that SOMETHING gets wrong.")
    else:
        print("\n  ✓ Nothing is perfect. There is room for the catalogue to show an")
        print("    effect. Carry on writing the remaining items in this style.")
    print("\n  These numbers are a dataset check, NOT a result. Never report them:")
    print(f"  {n} items chosen by you is not a sample.")
    print("=" * 70)


if __name__ == "__main__":
    main()
