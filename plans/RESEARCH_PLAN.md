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
| Placebo | `decoy` — the same catalogue prompt, catalogue of physics misconceptions |

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
- unparseable rate so high under one condition that the comparison is not meaningful;
- the decoy condition performing as well as the misconception-aware one, which would mean
  any structured catalogue helps and the *content* of ours did nothing.

### 3.1 · The decoy condition, declared in advance

`misconception_aware` changes two things at once and it is easy not to notice: the model is
handed a catalogue, **and** the prompt becomes longer, more structured and more specific. If
B beats A we do not yet know which of those did it, and it is the first question anyone will
ask.

The `decoy` condition holds the second fixed and removes the first. Same framing sentence,
same numbered catalogue of ten documented misconceptions, same instruction, comparable
length — about **physics**, which cannot possibly help with a password answer. The catalogue
ships in `python/data/decoy_misconceptions.csv`; the student does not author it, because it
is the control and not the data.

| Result | What it means |
|---|---|
| aware > decoy ≈ baseline | The catalogue helped because of its **content**. The hoped-for result. |
| aware ≈ decoy > baseline | Any structured catalogue helped. A real finding, just a different one — and the one that would otherwise have been published by mistake. |
| decoy < baseline | The irrelevant catalogue actively confused the model, which is evidence it genuinely reads the list. |

**The decoy is a diagnostic, not a third arm.** The pre-registered comparison remains
baseline vs misconception_aware; the decoy exists to interpret that gap. State this in the
write-up — it is what keeps a multiple-comparisons objection off the table at n = 40.

**Declared here, before any run, deliberately.** Adding a placebo *after* seeing a
disappointing gap is the researcher-degrees-of-freedom problem the Phase 5 page warns about.
Declaring it now costs nothing and closes the hole permanently.

Running it is **optional**: `--decoy` on `run_experiment.py`, roughly five extra minutes of
compute. If time runs short, do not run it, and record in Limitations that it was planned and
not executed. That is honest and costs nothing.

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

The gate is built around one uncomfortable fact: **agreement is a U-shaped diagnostic, not a
floor.** A dataset where every M item contains "never" and every C item hedges will produce
near-perfect agreement between two labellers — and it is exactly the dataset that kills the
study, because a model with no help already separates it. A one-sided "≥ 85%" threshold would
score the most dangerous dataset highest. So the gate below is a band, and the binding
criterion is empirical rather than statistical.

*Primary gate — the ten-item probe.* **After writing the first ten items and before writing
the other thirty**, run them through the real model under both prompts:

```bash
cd python
python3 misconception/run_experiment.py --probe 10
```

Twenty calls, about two minutes. A **perfect score under both prompts is a stop**: the items
are separable without help, so the catalogue has nothing left to add and both conditions will
sit at the ceiling. Go and write harder items — an M that reads as reasonable and hedged, a C
that reads as overconfident — and probe again. Finding this now costs ten items instead of
forty. The probe prints no metrics on purpose; ten self-chosen items are not a sample and
nothing from it may be reported.

*Then, on the full set of 40, all of the following:*

1. 40 items, 20 M and 20 C, each attributable to exactly one of the ten misconceptions.
2. A second person has blind-labelled at least 20 of them, and for each has written **one
   sentence on what decided it**. That sentence is the point. "I looked for the word never"
   is a ceiling effect caught in a way no agreement statistic catches it.
3. Agreement lands in the band **70–90%**, and every disagreement has been discussed to a
   resolution. Report the pre-resolution figure in the write-up.
4. At least 8 items are genuinely *hard*.
5. A **keyword audit**: count how many M items and how many C items contain an absolute
   ("always", "never", "impossible", "guaranteed", "100%"). Lopsided counts are the commonest
   tell. Crude, but it works at n = 40, which is more than can be said for the alternatives.

Decision rule on agreement:

- **Below 70%** — the labels are the problem, not the model. Stop. Rewrite the ambiguous
  items or drop the misconception they belong to.
- **70–90%** — proceed once disagreements are resolved by discussion.
- **Above 90%** — treat as a **warning, not a pass**. Combined with a clean probe it is
  acceptable; combined with a perfect probe it means the items are too easy. Check the
  keyword audit before proceeding.

Report percentage agreement at the gate. Cohen's kappa goes in the write-up, not the gate:
at n = 20 its interval is wide enough to be decorative.

*Why the gate is human.* Two automated ceiling detectors were tried and both failed at this
sample size, which is worth recording so nobody rebuilds them. The mock model's keyword rule
looked ideal until its noise term turned out to be text-*length* based, not meaning based —
it scored 0.75 on both a deliberately keyword-separable set and a deliberately tell-free one.
A TF-IDF logistic regression under cross-validation ran at chance on twelve items and would
be barely better at forty. There is no statistical separability test worth trusting at n = 40.
The probe and the "what decided it" sentence carry the weight instead.

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
| ~~S3~~ | ~~Ablation with the wrong misconceptions~~ | — | **Promoted into the core design as the `decoy` condition — see §3.1.** It was too valuable and too cheap to leave as an optional extra, and declaring it only after seeing results would have been fishing. |
| S1 | A second model (`llama3.2:1b` or `mistral:7b`), same data, same prompts | One afternoon | Does the effect depend on model size? The cheapest real second result now that the decoy is core. |
| S2 | A second labeller on all 40 items, with Cohen's kappa reported | A few hours of someone else's time | Turns a single-author dataset into a measured one. Partly satisfied by the Phase 3 gate, which already requires 20 items blind-labelled. |
| S4 | Naturally occurring student responses instead of hand-authored | Weeks, plus permissions | Removes the largest threat to external validity |
| S5 | More items, toward n = 150 | Weeks | The only thing that narrows the intervals |

With the decoy promoted, S1 is now the cheapest remaining win. Do it only once Phase 5 is
drafted — nothing is added to the study until a complete result exists.

## 7 · Known limitations, to be stated in the write-up

- n = 40. Confidence intervals are roughly ±13 points on a proportion near 75%. This pilot
  can detect a large effect and cannot detect a small one, and the write-up must say so.
- One domain, one model, one prompt pair.
- Responses are hand-authored by the researcher, not collected from students, so they may
  carry authorial tells that no real corpus would.
- Single-author labelling beyond the 20 items blind-checked at the Phase 3 gate.
- Local models are not perfectly deterministic even at temperature 0.
- If the decoy condition was not run, say so explicitly: without it, a reader cannot tell
  whether the catalogue's content helped or whether any longer, more structured prompt would
  have done the same.
- The decoy controls for prompt length and structure but not for *topical relevance* — a
  physics catalogue is both irrelevant and off-domain. A stricter placebo would use ten true
  statements about passwords. Worth naming as a limitation rather than pretending otherwise.

## 8 · Mentor notes

The failure mode to watch for is Phase 3, not Phase 4. A student who is enjoying the coding
will rush the dataset, and a rushed dataset produces a ceiling effect that is invisible until
the analysis and unfixable without redoing the month. Spend a whole check-in on the dataset
before the real run, and **read the items rather than accepting a count** — the gate is
deliberately written so that no number alone can pass it.

The ten-item probe is the highest-leverage item in this document. It costs two minutes and it
is the only cheap way to discover a ceiling effect before the dataset is written. If only one
rule from §5 survives contact with reality, make it that one.

The second failure mode is the write-up overclaiming. The single most valuable sentence this
project can teach is "consistent with an effect of the size we hoped for, and also consistent
with no effect." Phase 5 is built around getting her to write it without flinching.
