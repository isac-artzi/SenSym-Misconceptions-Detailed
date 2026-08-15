"""
prompts.py — this is the actual experiment.

WHY THIS IS THE MOST IMPORTANT FILE
-----------------------------------
The thing you deliberately change is THE PROMPT. Everything else stays the same.
So these two functions basically are the experiment.

  "baseline"            -> a plain grader. What a normal AI chatbot gives you.
  "misconception_aware" -> the same grader, handed your list of known
                           misconceptions to check against.

If B beats A, that's the result: giving it the list helps.

READ THIS TWICE
---------------
The two prompts have to be as similar as possible EXCEPT for the misconception
list. Same output format, same tone, same instructions. If you make prompt B
longer, clearer, better organised AND give it the list, then when B wins you
won't know which change did it. There's a word for that — confounded — and it
means the result doesn't tell you anything. Change one thing.
"""

from typing import List


# --------------------------------------------------------------------------
# Shared output instruction.
# Both prompts end with this, so the model replies in the same format either
# way and the code that reads its reply works identically. Part of keeping the
# comparison fair.
# --------------------------------------------------------------------------
OUTPUT_FORMAT_INSTRUCTION = """
Answer using exactly this format and nothing else:

VERDICT: <M or C>
REASON: <one short sentence>

Use M if the response contains a misconception (a confident but incorrect
belief). Use C if the response is correct.
""".strip()


def build_baseline_prompt(response_text: str) -> str:
    """
    CONDITION A — the plain one.

    A plain "is this right or wrong?" grader with NO idea what misconceptions
    exist. This stands in for what you'd get from a normal AI chatbot today.

    Args:
        response_text: one answer from data/responses.csv

    Returns:
        The full prompt to send to the model.

    ----------------------------------------------------------------------
    TODO 2 — Read this prompt over.
    ----------------------------------------------------------------------
    It's written for you as a working starting point. Your job:
      (a) Read it out loud. Does it clearly ask for what you want?
      (b) Check it does NOT accidentally hint at any specific misconception. If
          it does, the "plain" version is secretly not plain, and the comparison
          stops meaning anything.
      (c) Leave OUTPUT_FORMAT_INSTRUCTION exactly as it is.
    Once you're happy with it, delete this TODO block.
    """
    return f"""You are evaluating a student's answer about computer security.

Read the student's response below and decide whether it is correct or whether it
contains an incorrect belief.

STUDENT RESPONSE:
"{response_text}"

{OUTPUT_FORMAT_INSTRUCTION}"""


def build_misconception_aware_prompt(
    response_text: str,
    misconception_list: List[str],
) -> str:
    """
    CONDITION B — the one with the list.

    Identical to the plain one EXCEPT the model gets handed your list of known
    misconceptions and is told to check the answer against them.

    Args:
        response_text:      one answer from data/responses.csv
        misconception_list: the statements from data/misconceptions.csv

    Returns:
        The full prompt to send to the model.

    ----------------------------------------------------------------------
    TODO 3 — Build the misconception block.
    ----------------------------------------------------------------------
    `numbered_list` below is built for you. Read it and make sure you know what
    it produces — print it if you're not sure.

    Then think about one choice, and write down your answer, because I'm going
    to ask:

        Should the model see ALL 10 misconceptions every time, or only the one
        that answer is about?  (And what would that change about what your
        numbers actually mean?)

    Showing all 10 is closer to reality — a real system doesn't know in advance
    which misconception someone has. Showing only the relevant one makes it
    artificially easy and inflates the numbers. The code below shows all 10. Be
    ready to say why that's the right call.
    """
    # Turn ["A", "B"] into "1. A\n2. B" — an easy-to-read numbered list.
    numbered_list = "\n".join(
        f"{i}. {m}" for i, m in enumerate(misconception_list, start=1)
    )

    return _catalogue_prompt(response_text, numbered_list,
                             "passwords and authentication")


def build_decoy_prompt(
    response_text: str,
    decoy_list: List[str],
) -> str:
    """
    CONDITION D — the placebo.

    Structurally identical to condition B: same framing sentence, same numbered
    catalogue, same instruction, same output format, comparable length. The one
    thing that differs is the SUBJECT of the catalogue — these are documented
    physics misconceptions, which cannot possibly help with a password answer.

    WHY THIS EXISTS
    ---------------
    Condition B changes two things at once, and it is easy not to notice:
      (1) the model is handed a catalogue of misconceptions, and
      (2) the prompt gets longer, more structured and more specific.
    If B beats A you do not yet know which of those did it.

    D holds (2) fixed and removes (1). So:
      B > D ≈ A   the catalogue helped because of what is IN it.
      B ≈ D > A   any structured catalogue helped. A real finding, just a
                  different one — and the one you would have published by
                  mistake without this condition.
      D < A       the irrelevant catalogue actively hurt, which is evidence the
                  model is genuinely reading the list rather than ignoring it.

    You do not write the decoy list. It ships in data/decoy_misconceptions.csv
    because it is the control, not the data.

    Note the framing sentence names physics rather than passwords. That is
    deliberate: a catalogue introduced as being about passwords while listing
    facts about falling objects would be incoherent, and incoherence is its own
    confound. The mismatch between the catalogue's subject and the student's
    answer is the point of the condition, not a flaw in it.
    """
    numbered_list = "\n".join(
        f"{i}. {m}" for i, m in enumerate(decoy_list, start=1)
    )
    return _catalogue_prompt(response_text, numbered_list,
                             "physics and mechanics")


def _catalogue_prompt(response_text: str, numbered_list: str, domain: str) -> str:
    """
    The shared body of conditions B and D.

    Both catalogue conditions are built from this one function, so they cannot
    drift apart as you edit. If you change the wording, both change together and
    the comparison stays fair by construction rather than by your remembering to
    make the same edit twice. Keeping the fairness in the code rather than in
    your head is the whole trick.
    """
    return f"""You are evaluating a student's answer about computer security.

The following are documented misconceptions that students commonly hold about
{domain}:

{numbered_list}

Read the student's response below. Decide whether it reflects any of the
misconceptions listed above, or whether it is correct.

STUDENT RESPONSE:
"{response_text}"

{OUTPUT_FORMAT_INSTRUCTION}"""


# --------------------------------------------------------------------------
# Dispatcher — picks the right prompt builder for a condition name.
# You don't need to change this.
# --------------------------------------------------------------------------
def build_prompt(condition: str, response_text: str, misconception_list: List[str]) -> str:
    """
    `misconception_list` is whichever catalogue that condition should see —
    run_experiment.py hands the decoy list in when the condition is 'decoy'.
    That keeps this function ignorant of which file the list came from, which is
    what lets the fairness tests compare the two catalogue prompts directly.
    """
    if condition == "baseline":
        return build_baseline_prompt(response_text)
    if condition == "misconception_aware":
        return build_misconception_aware_prompt(response_text, misconception_list)
    if condition == "decoy":
        return build_decoy_prompt(response_text, misconception_list)
    raise ValueError(
        f"Unknown condition: {condition!r}. "
        "Expected 'baseline', 'misconception_aware' or 'decoy'."
    )


# --------------------------------------------------------------------------
# EXTRA IDEA (only once everything else works)
# --------------------------------------------------------------------------
# A third prompt would make this noticeably more interesting. Two options:
#
#   "chain_of_thought" — ask the model to reason step by step BEFORE giving its
#       verdict. Known to help on reasoning tasks. Lets you ask: is the
#       misconception list better than just telling it to think harder?
#
#   "few_shot" — show it 2 worked examples (one M, one C) before the real item.
#       Careful: use examples that are NOT among your 40, or you're feeding it
#       the answers.
#
# To add one: write a build_X_prompt() function here, add "X" to CONDITIONS in
# config.py, and add a branch to build_prompt() above. That's it.
