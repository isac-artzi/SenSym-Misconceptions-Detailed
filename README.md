# Wrong in a Particular Way

**Misconception-aware prompting and the detection of structured error in cybersecurity
learning.**

A mentored research pilot for a high-school student — an interactive site, a Python
laboratory, and a small, complete, falsifiable experiment, all in one repository.

---

## The research question, honestly stated

A wrong answer is not noise. Students are wrong in particular, repeatable, nameable ways,
and a teacher who knows the catalogue of those ways sees things a teacher without it does
not. This project asks whether the same is true of a language model.

**Does giving a small language model an explicit catalogue of known misconceptions improve
its ability to detect those misconceptions in student writing?**

The domain is cybersecurity — passwords and authentication — chosen because misunderstanding
there has consequences you can point at. The pilot narrows to the **detection** step, because
detection is a precondition for correction: a tutor that cannot tell a confused answer from a
correct one cannot possibly correct it.

Two conditions, identical in every respect but one. The `baseline` prompt asks a generic
grader whether a response contains a misconception. The `misconception_aware` prompt is the
same request with the catalogue of ten specific misconceptions pasted in. Same model, same
temperature, same forty responses. The only difference is what the model was told to look
for.

There is also a **pre-registered placebo**. `misconception_aware` changes two things at once
— the model gets a catalogue, *and* the prompt gets longer and more structured — so a third
`decoy` condition holds the second fixed and removes the first: the same catalogue prompt,
carrying ten documented misconceptions about **physics**. It cannot help with a password
answer. If the misconception-aware condition beats the decoy, the catalogue's *content* did
the work; if it merely ties it, any structured catalogue would have done, which is a
different finding and one that would otherwise have been published by mistake. Running it is
optional (`--decoy`, about five extra minutes); declaring it in advance is not.

> **Pre-registered prediction.** Misconception-aware prompting will raise *recall* more than
> *precision*, because naming the failure modes helps the model notice them, not helps it
> avoid false alarms.

That prediction is written down in advance so that it can fail. Four outcomes that would
count as "the catalogue did not help" are named in `plans/RESEARCH_PLAN.md`, and every one of
them is a publishable pilot result.

## Quickstart

1. Open the site: **https://isac-artzi.github.io/SenSym-Misconceptions-Detailed/**
   (identical to `docs/index.html` — works from any browser, no clone needed, and works
   offline from a clone too: no build step, no server).
2. Clone the repository to run the code and commit progress.
3. Prove it works before installing anything else:

   ```bash
   cd python
   python3 -m pip install -r ../requirements.txt
   python3 misconception/run_experiment.py --mock --sample
   python3 misconception/analyze.py
   ```

   That runs the whole pipeline with a **fake model** and **twelve demo responses** — no
   Ollama, no data of your own, no finished TODOs. Real charts appear in `python/results/`.
4. Then work the setup track: [Python and the repo](docs/setup/python.html) →
   [Ollama](docs/setup/ollama.html) → [Git](docs/setup/git.html).
5. Read [Using AI tools](docs/extras/ai-policy.html) once, properly, before Phase 3.

## Repository map

| Path | What lives there |
|---|---|
| `docs/` | The project website. Four setup pages (`setup/`), five phase chapters (`phases/`), four reference pages (`extras/`) — metrics playground, glossary, how to get unstuck, AI policy |
| `python/misconception/` | The pipeline: `config`, `prompts`, `llm_client`, `run_experiment`, `analyze`, plus the TODO/reference-fallback machinery |
| `python/tests/` | 27 tests, including a scikit-learn cross-check of every metric, prompt-fairness assertions, and a check that the placebo has not drifted from the condition it controls for |
| `python/data/` | The dataset — the scientific contribution, committed on purpose. `sample/` holds twelve demo items |
| `python/results/` | Generated output, git-ignored until a final run is committed deliberately |
| `plans/` | The governing research plan: gates, decision rules, stretch goals, known limitations |
| `progress/` | Progress logs (see `progress/TEMPLATE.md`) |
| `authoring/` | The chapter authoring contract and the headless page checker |
| `.github/` | CI, and the check-in issue template |

## The two things that make this repository unusual

**Unfinished TODOs never crash anything.** The pipeline ships as a skeleton with six TODOs.
Each one falls back to a worked reference implementation and prints a yellow warning naming
what is still fake; when all six are done you get a green line saying nothing fell back. So
a fresh clone runs end to end on day one, and **any crash is a real bug**, never "I haven't
got there yet." That distinction is what makes the repository teachable.

**Every metric is computed twice.** The tests compute each confusion count and metric by hand
*and* with scikit-learn, and assert they agree. "Verified" here means two independent
implementations agreeing, not one implementation looking plausible.

## Phases

| # | Phase | Artifact | Gate |
|---|---|---|---|
| — | Setup | Environment working | `check_setup.py` all `[OK]`; mock pipeline produces charts |
| 1 | Design | Understanding | Defends the positive class, the recall choice and the 50% floor out loud |
| 2 | Code | Six TODOs closed | The green "nothing fell back" line, `pytest -q` green |
| **3** | **Dataset** | **40 labelled responses** | **The ten-item probe is not perfect; blind agreement in the 70–90% band; ≥8 genuinely hard items** |
| 4 | Run | Two complete runs | Full provenance recorded; run-to-run difference stated |
| 5 | Analysis | Write-up | An outsider can state what was found and what was not |

Phase 3 is the gate that decides whether the project works. If the twenty M items and the
twenty C items are obviously different, both conditions score near 100%, the comparison
collapses, and a month of work measures nothing.

The cheapest defence against that is two minutes long. **After the first ten items and before
writing the other thirty**, run `python3 misconception/run_experiment.py --probe 10`. A
perfect score under both prompts is a *stop*, not a pass: the items are separable without
help, so the catalogue has nothing left to show. Finding that out now costs ten items instead
of forty.

Note what the gate does *not* do: it does not threshold on labeller agreement alone.
Agreement is U-shaped here — a dataset of "never" versus hedging produces near-perfect
agreement and is exactly the dataset that kills the study. Above 90% is a warning, not a
pass. The ceiling-effect simulator on
[the Phase 3 page](docs/phases/phase-3-dataset.html) makes the underlying problem visible;
`plans/RESEARCH_PLAN.md` §5 has the full rule and records the two automated ceiling detectors
that were tried and failed at this sample size.

Milestone commits are tagged (`setup-complete`, `code-complete`, `phase-3-complete`,
`run-complete`, `v1.0`) so the write-up can cite an exact state of the repository. Tag only
when `pytest -q` is fully green.

## The honesty rules

These are not decoration; they are the reason the result will be worth anything.

- The positive class is **M**. Every precision, recall and F1 on this site is with respect to
  it, and is stated as such.
- With n = 40 the intervals are wide. Every reported metric carries a **Wilson score
  interval**, never the normal approximation, which runs past 1.0 at 38/40 and is visibly
  wrong.
- The **majority-class baseline is exactly 50%** by construction. Any claim that the model
  "did well" is stated relative to that floor.
- Unparseable replies are counted and reported, never silently defaulted. `parse_verdict()`
  returns `?` rather than guess, on purpose.
- A metric with a zero denominator is **undefined, not zero**.
- Two runs at temperature 0 may differ slightly. That gets reported, not hidden.
- Nothing produced by `--mock` or `--sample` is ever presented as a result.

## For mentors

`plans/RESEARCH_PLAN.md` holds the gate criteria, the decision rules at each gate, the
stretch goals ranked by cost, and the known limitations to be stated in the write-up. The
failure mode to watch is Phase 3, not Phase 4.

`authoring/CHAPTER_GUIDE.md` is the page authoring contract: the exact skeleton, the box and
lab vocabulary, the `detect.js` API, and the honesty rules a new page must not violate. It
exists so that further pages — a Phase 6, a second domain — can be written to match
everything already here.

This site uses the **SenSym mentored-research house style**, shared with the other project
sites in this program. The component vocabulary in `docs/assets/css/style.css` and the
plotting half of `docs/assets/js/detect.js` are deliberately identical across projects: a page
authored for one renders in another unchanged. Only the accent hue and the project-specific
block at the end of each file differ.

Verify the whole site renders with:

```bash
npm install playwright          # once
node authoring/check_pages.js --all
```

It fails a page on console errors, unrendered `$math$`, blank canvases, canvases that resize
on redraw, broken relative links, and exercises without solutions. All 14 pages currently
pass.

GitHub Pages serves this site from `main` + `/docs`. There is no build step, so what renders
from a local clone is what Pages serves.

## Licence

MIT — see `LICENSE`.
