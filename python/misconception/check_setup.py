"""
check_setup.py — run this FIRST.

It checks, one at a time, that everything you need is installed and working, and
tells you exactly what to do about anything that's missing.

    python misconception/check_setup.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

OK = "  [OK]   "
BAD = "  [FIX]  "
TODO = "  [TODO] "
problems = []
todos = []


def check(name, condition, fix_hint, soft=False):
    """
    soft=True marks something that is EXPECTED to be unfinished on a fresh
    clone (your data files, the local model). It's reported as a to-do rather
    than a broken environment, because nothing is actually wrong yet.
    """
    if condition:
        print(OK + name)
        return
    print((TODO if soft else BAD) + name)
    print("         -> " + fix_hint.replace("\n", "\n         -> "))
    (todos if soft else problems).append(name)


print("=" * 70)
print("SETUP CHECK")
print("=" * 70)

# --- 1. Python version ---
check(
    f"Python {sys.version_info.major}.{sys.version_info.minor} (need 3.9+)",
    sys.version_info >= (3, 9),
    "Install a newer Python from python.org",
)

# --- 2. Packages ---
for pkg, pipname in [("pandas", "pandas"),
                     ("requests", "requests"),
                     ("matplotlib", "matplotlib"),
                     ("sklearn", "scikit-learn")]:
    try:
        __import__(pkg)
        found = True
    except ImportError:
        found = False
    check(f"package: {pipname}", found, f"pip install {pipname}")

# --- 3. Data files ---
try:
    import config
    import pandas as pd

    for label, path, col in [("data/misconceptions.csv", config.MISCONCEPTIONS_FILE, "statement"),
                             ("data/responses.csv", config.RESPONSES_FILE, "response_text")]:
        if not path.exists():
            check(label, False, f"File is missing from {path.parent}")
            continue
        df = pd.read_csv(path)
        real = df[~df[col].astype(str).str.startswith("<")]
        check(
            f"{label} — {len(real)} real row(s)",
            len(real) > 0,
            "Still contains only the template placeholders — expected on a fresh "
            "clone.\nFill it in when you get to Phase 3 (see data/EXAMPLES.md).\n"
            "Meanwhile, run with --sample to use the demo dataset.",
            soft=True,
        )
except Exception as e:  # noqa: BLE001
    check("data files", False, f"Could not read them: {e}")

# --- 4. Ollama ---
try:
    import requests

    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    models = [m["name"] for m in r.json().get("models", [])]
    check("Ollama is running", True, "")

    import config
    have = any(m.startswith(config.MODEL_NAME.split(":")[0]) for m in models)
    check(
        f"model '{config.MODEL_NAME}' downloaded  (you have: {', '.join(models) or 'none'})",
        have,
        f"ollama pull {config.MODEL_NAME}",
        soft=True,
    )
except Exception:  # noqa: BLE001
    check(
        "Ollama is running",
        False,
        "Only needed for the REAL run — not for --mock. When you're ready:\n"
        "  install from https://ollama.com/download, then run\n"
        "  ollama serve        (leave this window open)\n"
        "and in a SECOND terminal:\n"
        "  ollama pull llama3.2:3b",
        soft=True,
    )

print("=" * 70)
if problems:
    print(f"✗ {len(problems)} thing(s) are genuinely broken (marked [FIX] above).")
    print("  Fix those before going further.")
else:
    print("✓ Your environment is working.")

if todos:
    print(f"\n{len(todos)} thing(s) not done yet (marked [TODO]) — all expected on")
    print("a fresh clone. Nothing is broken; they're just steps you haven't reached.")

print("\nYou can run the whole pipeline right now, with no model and no data:")
print("    python misconception/run_experiment.py --mock --sample")
print("    python misconception/analyze.py")
print("=" * 70)
