# Research plan — Wrong in a Particular Way

The governing document. The website teaches; this file decides. When the site and this
file disagree about scope, timing or a gate criterion, this file wins.

---

## 1 · The question

**Does giving a small language model an explicit catalogue of known misconceptions improve
its ability to detect those misconceptions in student writing?**

Domain: cybersecurity, specifically passwords and authentication. Chosen because
misunderstanding there has consequences that can be named — an account taken over, a
credential reused, a false sense of safety that removes a layer of defence.

Narrowed to **detection**. The larger question is whether misconception-aware tutoring
improves learning; that needs learners, a control group and time. Detection is the first
link in that chain and the only one measurable in a term: a tutor that cannot distinguish a
confused answer from a correct one cannot correct anything. If detection fails, nothing
downstream is worth building.

## 2 · The design

| | |
|---|---|
| Items | 40 hand-authored student responses, 20 containing a misconception (M), 20 not (C) |
| Misconceptions | 10, selected from the student's 32-item list, ~4 responses each |
| Model | `llama3.2:3b` via Ollama, local, temperature 0 |
| Conditions | `baseline` (generic grader prompt) vs `misconception_aware` (same prompt + the catalogue) |
| Design | Within-item: every response is judged under both conditions |
| Positive class | **M** — "this response contains a misconception" |
| Headline metric | **Recall.** A false negative is the consequential error. |
| Baseline to beat | Majority class, exactly 50% by construction |

The two conditions differ in the prompt and in nothing else. `python/tests/test_pipeline.py`
carries fairness assertions over this.

## 3 · Pre-registered prediction

Written before any real run, so that it can fail:

> Misconception-aware prompting will raise **recall** more than it raises **precision**,
> because naming the failure modes helps the model notice them rather than helping it avoid
> false alarms.

Outcomes that would count as the catalogue **not** helping, any of which is a publishable
pilot result and none of which is a failure of the project:

- recall unchanged within the confidence interval;
- recall up but precision down by at least as much (the model simply became twitchier);
- both conditions at ceiling, which means the dataset was too easy and measured nothing;
- unparseable rate so high under one condition that the comparison is not meaningful.

## 4 · Phases and gates

| Phase | Artifact | Gate criterion | Tag |
|---|---|---|---|
| Setup | Environment working | `check_setup.py` all `[OK]` except data; `--mock --sample` produces charts | `setup-complete` |
| 1 · Design | Understanding | Defends the positive class, the recall choice and the 50% floor out loud, unprompted | — |
| 2 · Code | Six TODOs closed | The green *"Nothing fell back — this run was entirely your code"* line, and `pytest -q` green | `code-complete` |
| **3 · Dataset** | 40 labelled responses | **See decision rule below** | `phase-3-complete` |
| 4 · Run | Two complete runs | Both runs committed with full provenance blocks; difference between them recorded | `run-complete` |
| 5 · Analysis | Write-up | An outsider reads it and can state what was found and what was not | `v1.0` |

Tag only when `pytest -q` is green, so a report can cite an exact repository state.

## 5 · Decision rules

**The dataset gate (Phase 3) — the one that matters.**

Before proceeding to Phase 4, all of the following must hold:

1. 40 items, 20 M and 20 C, every one attributable to exactly one of the ten misconceptions.
2. A second person has blind-labelled at least 20 of them.
3. Agreement with the second labeller is **at least 85%**.
4. At least 8 items are *hard* — an M that reads as reasonable, or a C that reads as
   overconfident. If every M contains "always" or "never", the dataset is a word detector.

- Agreement **below 70%**: the labels are the problem, not the model. Stop. Rewrite the
  ambiguous items or drop the misconception they belong to.
- Agreement **70–85%**: proceed only after resolving the disputed items by discussion, and
  report the pre-resolution figure in the write-up.
- **Ceiling in the mock check** (both conditions above 95% on a dry run over the real
  dataset with the fake model): the items are trivially separable. Rebuild the C items
  before spending a real run on them.

**Hardware.** If a single call takes more than 30 seconds, drop to `llama3.2:1b` and record
the reason. A weaker model that benefits more from the catalogue is an interesting result,
not a compromise.

**If Ollama cannot be installed at all.** Complete Phases 1–3 and all of Phase 2 in mock
mode, then borrow a machine for one afternoon for Phase 4. Do not let this block the
dataset work, which is where the value is.

**Run-to-run movement.** Under 3 items moving between two identical runs: expected, gets a
sentence in Methods. 4 or more: stop and investigate before analysing.

**Scope.** Nothing is added to the study until Phase 5 is drafted. Stretch goals below are
for after a complete result exists, not instead of one.

## 6 · Stretch goals, cheapest first

| | Goal | Cost | What it buys |
|---|---|---|---|
| S1 | A second model (`llama3.2:1b` or `mistral:7b`), same data, same prompts | One afternoon | Does the effect depend on model size? The cheapest real second result in the project. |
| S2 | A second labeller on all 40 items, with Cohen's kappa reported | A few hours of someone else's time | Turns a single-author dataset into a measured one |
| S3 | An ablation: catalogue with the *wrong* misconceptions | One run | Separates "the catalogue helped" from "any extra text helped" — the strongest control available at this scale |
| S4 | Naturally occurring student responses instead of hand-authored | Weeks, plus permissions | Removes the largest threat to external validity |
| S5 | More items, toward n = 150 | Weeks | The only thing that narrows the intervals |

S3 is the most scientifically valuable and is still one afternoon of compute. Consider it
before S4 or S5.

## 7 · Known limitations, to be stated in the write-up

- n = 40. Confidence intervals are roughly ±13 points on a proportion near 75%. This pilot
  can detect a large effect and cannot detect a small one, and the write-up must say so.
- One domain, one model, one prompt pair.
- Responses are hand-authored by the researcher, not collected from students, so they may
  carry authorial tells that no real corpus would.
- Single-author labelling unless S2 is done.
- Local models are not perfectly deterministic even at temperature 0.

## 8 · Mentor notes

The failure mode to watch for is Phase 3, not Phase 4. A student who is enjoying the coding
will rush the dataset, and a rushed dataset produces a ceiling effect that is invisible until
the analysis and unfixable without redoing the month. Spend a whole check-in on the dataset
before the real run, and read the items rather than accepting a count.

The second failure mode is the write-up overclaiming. The single most valuable sentence this
project can teach is "consistent with an effect of the size we hoped for, and also consistent
with no effect." Phase 5 is built around getting her to write it without flinching.
