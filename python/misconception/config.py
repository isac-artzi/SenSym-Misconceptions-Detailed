"""
config.py — every setting lives here.

WHY THIS FILE EXISTS
--------------------
You want one place where all the knobs are. When someone asks "which model did
you use, and at what temperature?" — and someone will, including you in three
months — the answer should be in ONE file, not scattered across five scripts.

Nothing here runs anything. It just holds values the other files import.
"""

from pathlib import Path

# --------------------------------------------------------------------------
# FOLDER LOCATIONS
# You shouldn't need to change these. They just figure out where things live
# relative to this file, so the project works no matter where you put it.
# --------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

MISCONCEPTIONS_FILE = DATA_DIR / "misconceptions.csv"
RESPONSES_FILE = DATA_DIR / "responses.csv"

# A small demo dataset so a freshly cloned repo runs before you've written
# anything. Used only with the --sample flag. NEVER report results from it.
SAMPLE_MISCONCEPTIONS = DATA_DIR / "sample" / "misconceptions.csv"
SAMPLE_RESPONSES = DATA_DIR / "sample" / "responses.csv"

RESULTS_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------------------------
# TODO 1 — CHOOSE YOUR MODEL
# --------------------------------------------------------------------------
# This is the model you'll run. Small and local, meaning it runs on your laptop,
# it's free, it needs no API key, and nothing you type gets sent to a company.
#
# Recommended starting point: "llama3.2:3b"
#   ("3b" = 3 billion parameters. Small and fast. Runs fine on a normal laptop.)
#
# Other options if you want to compare models later (that comparison makes a
# genuinely interesting extra result):
#   "llama3.2:1b"   - even smaller and faster, noticeably worse
#   "qwen2.5:3b"    - similar size, trained differently
#   "mistral:7b"    - bigger and better, wants ~8GB of free memory
#
# Leave this alone for now. Come back and try a second model only AFTER your
# first full run works end to end.
MODEL_NAME = "llama3.2:3b"

# Where Ollama listens. Don't change unless you know you need to.
OLLAMA_URL = "http://localhost:11434/api/generate"

# TEMPERATURE controls randomness in the model's output.
#   0.0 = as deterministic as possible (same input -> same output)
#   1.0 = creative and inconsistent
# You want 0.0 here, so you can rerun and get the same thing. If you leave it
# high, every run gives different numbers and you can't tell whether a change
# came from your prompt or from the model just being random.
TEMPERATURE = 0.0

# Cap on how long the model's reply can be. We only need a short answer, and a
# low cap keeps things fast.
MAX_TOKENS = 200

# How many seconds to wait for the model before giving up on one item.
TIMEOUT_SECONDS = 120


# --------------------------------------------------------------------------
# EXPERIMENT CONDITIONS
# --------------------------------------------------------------------------
# The two versions you're comparing. The ONLY difference is which prompt gets
# used — model, temperature and answers stay identical. That's what makes the
# comparison mean anything.
CONDITIONS = ["baseline", "misconception_aware"]

# The label strings used in your data. Keep these consistent everywhere.
LABEL_MISCONCEPTION = "M"
LABEL_CORRECT = "C"


# --------------------------------------------------------------------------
# A note on what counts as the "positive" class
# --------------------------------------------------------------------------
# Precision and recall are always measured against one category, called the
# POSITIVE class. Here that's "has a misconception" (M).
#
# That's a deliberate choice worth explaining when you write this up: spotting
# misconceptions is the whole point, and missing one is the mistake that
# actually costs something. So M is the positive class.
POSITIVE_LABEL = LABEL_MISCONCEPTION
