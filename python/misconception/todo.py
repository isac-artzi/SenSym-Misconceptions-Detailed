"""
todo.py — the bit that lets everything RUN before you've finished it.

WHY THIS EXISTS
---------------
There's a tension in a project set up for learning:

  * If unfinished TODOs crash the program, you can't run anything until they're
    all done — so you never see what the finished thing looks like, and you
    can't tell "my code is wrong" apart from "my setup is wrong."
  * If the TODOs come pre-filled, you don't learn anything.

So this does both. Every TODO has a worked version hiding behind it. Until you
fill the TODO in, that runs instead, everything completes end to end, and you
get a loud yellow warning saying exactly what isn't yours yet. The moment you
write your own version, it takes over and the warning goes away.

    clone -> everything runs -> you see the finished shape
    -> you replace the worked versions one at a time
    -> the warnings disappear one at a time

Nothing here is a TODO. You never need to edit this file.
"""

import sys

# Which TODOs fell back to the worked version on this run.
_fired: list = []

# Where each TODO lives, so the warning can point you at the right spot.
LOCATIONS = {
    "TODO 2":  ("misconception/prompts.py", "build_baseline_prompt()",
                "read the plain prompt over and delete the TODO block"),
    "TODO 3":  ("misconception/prompts.py", "build_misconception_aware_prompt()",
                "answer the 'all 10 vs. just the relevant one' question"),
    "TODO 4a": ("misconception/run_experiment.py", "run_condition()",
                "build the prompt with build_prompt(...)"),
    "TODO 4b": ("misconception/run_experiment.py", "run_condition()",
                "send the prompt with ask(...)"),
    "TODO 5a": ("misconception/analyze.py", "compute_confusion()", "count the True Positives"),
    "TODO 5b": ("misconception/analyze.py", "compute_confusion()", "count the False Negatives"),
    "TODO 5c": ("misconception/analyze.py", "compute_confusion()", "count the False Positives"),
    "TODO 5d": ("misconception/analyze.py", "compute_confusion()", "count the True Negatives"),
}


def pending(todo_id: str, value, fallback, *args, **kwargs):
    """
    Return `value` if you've filled the TODO in; otherwise run the worked
    version and make a note that it happened.

    Args:
        todo_id:  e.g. "TODO 4a"
        value:    what your code produced. `None` means "not done yet".
        fallback: the worked version to call instead.

    Returns:
        Either your value or the worked result.
    """
    if value is not None:
        return value
    if todo_id not in _fired:
        _fired.append(todo_id)
    return fallback(*args, **kwargs)


def any_pending() -> bool:
    return bool(_fired)


def report(stream=sys.stdout) -> None:
    """Print the end-of-run summary of which TODOs are still using worked code."""
    if not _fired:
        print("\n\033[32m✓ Nothing fell back — this run was entirely your code.\033[0m",
              file=stream)
        return

    print("\n" + "\033[33m" + "─" * 72, file=stream)
    print(f"⚠  {len(_fired)} TODO(s) not done — the worked versions were used.",
          file=stream)
    print("   The numbers above are real, but they aren't YOUR code's numbers yet.",
          file=stream)
    print("─" * 72 + "\033[0m", file=stream)
    for t in _fired:
        where = LOCATIONS.get(t)
        if where:
            f, fn, what = where
            print(f"   {t:<8} {f} · {fn}\n            → {what}", file=stream)
        else:
            print(f"   {t}", file=stream)
    print("\n   Work through them in order — see docs/03_TODO_CHECKLIST.md.\n", file=stream)


def reset() -> None:
    """Only used by the tests."""
    _fired.clear()
