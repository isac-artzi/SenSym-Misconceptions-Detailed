"""
llm_client.py — the bit that actually talks to the model.

You shouldn't need to change anything here. It's in the project so you can read
it and see what's going on underneath. Skim it once; it's short.

WHAT'S ACTUALLY HAPPENING
-------------------------
Ollama runs a small web server on your own computer at localhost:11434.
"localhost" just means "this machine" — nothing leaves your laptop. We send it
a prompt over HTTP, it sends back text. That's the whole interaction. There's
no magic in it.
"""

import re
import requests

from config import (
    MODEL_NAME,
    OLLAMA_URL,
    TEMPERATURE,
    MAX_TOKENS,
    TIMEOUT_SECONDS,
    LABEL_MISCONCEPTION,
    LABEL_CORRECT,
)


class LLMError(RuntimeError):
    """Raised when we can't get a usable answer out of the model."""


def ask_llm(prompt: str) -> str:
    """
    Send one prompt to the local model and return its raw text reply.

    Raises LLMError with a friendly message if Ollama isn't running.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,           # get the whole answer at once, not word by word
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS,
        },
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise LLMError(
            "Could not reach Ollama at " + OLLAMA_URL + ".\n"
            "  -> Is Ollama running? Open a terminal and type:  ollama serve\n"
            "  -> Did you download the model?                   ollama pull " + MODEL_NAME
        )
    except requests.exceptions.Timeout:
        raise LLMError(
            f"The model took longer than {TIMEOUT_SECONDS}s to answer. "
            "Try a smaller model (llama3.2:1b) in config.py."
        )

    return r.json().get("response", "").strip()


def parse_verdict(raw_reply: str) -> str:
    """
    Pull the M/C verdict out of the model's reply.

    Small models don't always follow the format perfectly, so we try in order:
      1. Look for "VERDICT: M" / "VERDICT: C"   (the format we asked for)
      2. Look for a bare M or C on its own
      3. Fall back to keyword sniffing
      4. Give up and return "?" so it shows up as unparseable rather than
         silently guessing

    WHY IT RETURNS "?" INSTEAD OF GUESSING:
    A garbled reply is information. Quietly defaulting those to "C" would hide a
    real weakness of small models and make your numbers look better than they
    are. Say how often it happened when you write this up — it's an honest and
    fairly interesting number.
    """
    text = raw_reply.upper()

    m = re.search(r"VERDICT\s*[:\-]\s*\**\s*([MC])\b", text)
    if m:
        return m.group(1)

    m = re.search(r"\b([MC])\b", text)
    if m:
        return m.group(1)

    if "MISCONCEPTION" in text and "NO MISCONCEPTION" not in text:
        return LABEL_MISCONCEPTION
    if "CORRECT" in text and "INCORRECT" not in text:
        return LABEL_CORRECT

    return "?"


def parse_reason(raw_reply: str) -> str:
    """Pull out the one-sentence justification, if the model gave one."""
    m = re.search(r"REASON\s*[:\-]\s*(.+)", raw_reply, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip().split("\n")[0][:300]
    return raw_reply.replace("\n", " ")[:300]


# --------------------------------------------------------------------------
# MOCK MODE
# --------------------------------------------------------------------------
# A fake "model" that lets you test the whole pipeline without installing
# anything. It returns a plausible-looking answer instantly.
#
# USE THIS FIRST. Run everything in mock mode, confirm the plumbing works and
# charts come out, THEN switch on the real model. Debugging your code and your
# Ollama install at the same time is miserable.
#
# The fake model is deliberately imperfect — right about 70% of the time — so
# the confusion matrix has all four boxes filled in and you can see the analysis
# actually doing something.
#
# HEADS UP: the fake model IGNORES which prompt it got, so both conditions come
# out IDENTICAL in mock mode. That's expected, not a bug — there's no real model
# for the prompt to influence. Once you switch to the real one they'll diverge.
# --------------------------------------------------------------------------
def ask_llm_mock(prompt: str) -> str:
    """Fake model. Same output every time, no network, nothing to install."""
    # Extract the student response from the prompt so we can pretend to judge it
    m = re.search(r'STUDENT RESPONSE:\s*"(.*?)"', prompt, flags=re.DOTALL)
    text = (m.group(1) if m else prompt).lower()

    # Crude keyword rule — stands in for a model that's okay but flawed.
    wrong_signals = ["always", "never", "impossible", "guarantee", "completely",
                     "definitely", "can't be", "cannot be", "safe from"]
    score = sum(1 for w in wrong_signals if w in text)

    # Deterministic pseudo-noise so ~30% of items get flipped, giving us FPs/FNs
    noise = (len(text) * 7 + text.count("e") * 13) % 10

    verdict = LABEL_MISCONCEPTION if score > 0 else LABEL_CORRECT
    if noise < 3:
        verdict = LABEL_CORRECT if verdict == LABEL_MISCONCEPTION else LABEL_MISCONCEPTION

    return f"VERDICT: {verdict}\nREASON: (mock reply — no real model was used)"
