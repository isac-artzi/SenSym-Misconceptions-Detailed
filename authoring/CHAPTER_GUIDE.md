# CHAPTER_GUIDE.md — how to author a page on this site

Read this fully, then read `docs/setup/ollama.html` as the reference implementation.
Match it exactly in structure. Deviating creates inconsistency across fourteen pages.

This site uses the **SenSym mentored-research house style**, shared with the other project
sites in this program (`SenSym-deterministic-chaos` and siblings). The component vocabulary
in `docs/assets/css/style.css` and the plotting half of `docs/assets/js/detect.js` are
identical across projects on purpose: a page authored for one renders in another unchanged.
Only the accent hue and the project-specific block at the end of each file differ.

## The project in one paragraph

"Wrong in a Particular Way" is a mentored research pilot for a motivated tenth-grade student
(Arshi Agrawal, BASIS Peoria, class of 2029). She has basic Python — loops and functions —
no statistics, no machine learning, and no prior research experience. The research question:
does giving a small local language model an explicit catalogue of known cybersecurity
misconceptions improve its ability to detect those misconceptions in student writing? Two
conditions, `baseline` and `misconception_aware`, differing only in the prompt. Forty
hand-authored responses, twenty containing a misconception and twenty not. Model
`llama3.2:3b` via Ollama, local, temperature 0. Outcome: a confusion matrix and the four
metrics computed from it, with **M — "this response contains a misconception" — as the
positive class**, and **recall as the headline metric**, because a missed misconception is
the error that actually costs something.

## Voice and level

- Write to a smart sixteen-year-old who has never met this material and will not be
  condescended to. Full sentences. No breeziness, no exclamation marks, no "let's dive in",
  no "don't worry".
- **Every abstract claim arrives attached to a number, a picture, or a concrete failure.**
  She builds intuition from artifacts, then formalises. A paragraph of definition with no
  worked instance is a paragraph she will skim.
- Prove things when the proof is genuinely within reach — arithmetic on a 2×2 table, a
  ratio, an algebraic rearrangement. Otherwise state the result, mark it
  `<span class="status cited">cited</span>`, and say what would be needed to establish it.
  **Never fake a proof and never invent a citation.**
- Use the epistemic labels honestly: `proved`, `cited`, `conjectured`, `observed`. Timing
  figures measured on nobody's machine are `observed` at best; say so.
- Cybersecurity examples must be **factually correct**. NIST SP 800-63B does recommend
  against scheduled password rotation. MFA is bypassable via SIM swap, push fatigue,
  session-token theft and real-time phishing proxies. Do not overstate an attack to make a
  point land.
- She is a beginner at research, not stupid. Explain *why* a methodological choice was made,
  not just what it is. The single most valuable thing this site teaches is the reasoning, and
  she will need to defend it out loud.
- British-ish spellings are used ("behaviour", "recognise", "labelling"). Be internally
  consistent with the reference page.
- Em-dashes sparingly.

## Honesty rules specific to this project (do not violate)

- The positive class is **M**. Precision, recall and F1 are all computed with respect to it.
  Say so wherever a metric appears; a metric without a stated positive class is meaningless.
- **Recall = TP / (TP + FN)** — of the misconceptions that were really there, what fraction
  did the model catch. **Precision = TP / (TP + FP)** — of the alarms it raised, what
  fraction were real. Never swap these. Never write "accuracy" when you mean one of them.
- A metric with a zero denominator is **undefined, not zero**. `G.metrics` returns `null`
  and `G.pct` prints "undefined". Preserve that distinction in prose.
- With n = 40 the confidence intervals are wide. Any page that reports a number must show or
  reference its interval. Use `G.wilson(k, n)` — the Wilson score interval — never the normal
  approximation, which runs past 1.0 at 38/40 and is therefore visibly wrong.
- The **majority-class baseline** is 50% here by construction (20 M, 20 C). An accuracy of
  50% is worth nothing. Any claim of the form "the model did well" must be relative to that
  floor, and the floor must be stated.
- Two runs at temperature 0 may still differ slightly. This is expected, not a bug, and it
  gets reported rather than hidden.
- The twelve items in `python/data/sample/` and everything produced by `--mock` are
  **demo data**. No number derived from them may be presented as a result. Say this on every
  page where a reader might be tempted.
- The model name in prose must match `MODEL_NAME` in `python/misconception/config.py`
  (`llama3.2:3b`) and the paths must match the real repository layout:
  `python/misconception/`, `python/tests/`, `python/data/`, `python/results/`.

## Exact page skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phase N · Short Title — Wrong in a Particular Way</title>
<link rel="stylesheet" href="../assets/vendor/katex/katex.min.css">
<link rel="stylesheet" href="../assets/css/style.css">
<script src="../assets/vendor/katex/katex.min.js"></script>
<script src="../assets/vendor/katex/auto-render.min.js"></script>
<script src="../assets/js/detect.js"></script>
</head>
<body>

<header class="site">
  <div class="wrap">
    <div class="crumbs"><a href="../index.html">Wrong in a Particular Way</a> · Phase N</div>
    <div class="badges"><span class="badge">Section name</span><span class="badge win">Win: ...</span></div>
    <h1 class="chapter-title">Chapter Title</h1>
    <p class="chapter-sub">One line saying what this page actually does.</p>
  </div>
</header>

<main class="wrap">
  <p class="lede">Two or three sentences: what she will be able to do when this is finished.</p>

  <div class="objectives">
    <h3>By the end of this phase you can</h3>
    <ul><li>...</li> ... 5–7 items ...</ul>
  </div>

  <h2>1 · Section</h2>
  ...

  <h2>N · Exercises</h2>
  ... 5–7 exercises, each with a full solution ...

  <h2>N+1 · Verification</h2>
  <div class="box verify"><span class="lbl">Before the check-in</span><ul>...</ul></div>

  <div class="box aside">
    <span class="lbl">Going deeper (optional)</span>
    ...
  </div>

  <div class="pager">
    <a href="prev.html">← Previous · title</a>
    <a href="next.html">Next · title →</a>
  </div>
</main>

<footer class="site">
  <div class="wrap">
    <strong>Wrong in a Particular Way</strong> · Phase N ·
    <a href="../index.html">index</a> ·
    <a href="../extras/glossary.html">glossary</a> ·
    <a href="../extras/unstuck.html">stuck?</a>
  </div>
</footer>
</body>
</html>
```

**Scripts go in `<head>`, blocking.** Inline `<script>` blocks in the body run during parsing
and need `G` to already exist. Do not move them to the end of the body.

All asset and sibling paths are `../` from `docs/setup/`, `docs/phases/` and `docs/extras/`.
The index is always `../index.html`.

## Box types

`<div class="box X"><span class="lbl">Label</span> ... </div>` where X is one of:
`definition`, `theorem`, `example`, `warning`, `win`, `python`, `verify`, `aside`.

Epistemic status chips: `<span class="status proved">proved</span>`, and likewise `cited`,
`conjectured`, `observed`.

Every page gets exactly one `<div class="box python">` naming the commands to run, in a
`.cmd` block, with paths relative to `python/`:

```
cd python
python3 misconception/run_experiment.py --mock --sample
python3 misconception/analyze.py
pytest ../  -q          # from the repo root: pytest -q
```

## Terminal blocks

```html
<div class="cmd"><pre><span class="p">$ </span>ollama list</pre></div>
<div class="out">NAME              SIZE
<b>llama3.2:3b</b>       2.0 GB</div>
```

`.cmd` gets a copy button automatically; the `<span class="p">` prompt is stripped from what
is copied. `.out` is for **expected output**, never for input — the visual distinction is
load-bearing. Inside `.out`, `<b>` renders green (good) and `<i>` renders red (bad).

## Math

KaTeX auto-render, `$...$` inline and `$$...$$` display. **Never write a bare `$` in prose**
— it is swallowed as a math delimiter. Metric definitions should be set as display math at
least once per page that uses them.

## Interactive labs — REQUIRED, 1 to 3 per page

```html
<div class="lab">
  <div class="lab-title">Lab · Name</div>
  <p class="lab-desc">What to try, and what to notice.</p>
  <canvas id="labN" height="300"></canvas>
  <div class="controls" id="labNctl"></div>
  <div class="readout" id="labNout"></div>
</div>

<script>
G.lab(function () {
  var st = G.controls('labNctl', [
    { k: 'fn', type: 'range', label: 'false negatives', min: 0, max: 20, step: 1, value: 4,
      fmt: function (v) { return String(v); } }
  ], draw);
  function draw() {
    var cv = G.canvas('labN'); if (!cv) return;      // re-measure inside draw, every time
    var fr = G.frame(cv.ctx, cv.w, cv.h,
      { xmin: 0, xmax: 1, ymin: 0, ymax: 1, margin: { left: 52, bottom: 42 } });
    fr.axes({ xlabel: 'x', ylabel: 'y', xticks: 5, yticks: 5 });
    fr.rect(0.1, 0, 0.4, 0.8, { fill: G.COL.accent, alpha: 0.2, stroke: G.COL.accent });
    G.say('labNout', 'a text readout that says what just happened');
  }
  draw();
});
</script>
```

**Rules for labs.** A canvas must never be blank — `check_pages.js` fails the page on that.
Always call `G.canvas(id)` *inside* `draw()`, never once outside; it re-measures on resize,
and a canvas sized outside the draw doubles in height on every slider move on a Retina
display. Seed all randomness with `G.rng(seed)`; never `Math.random`. Keep a draw under
~50 ms. The readout is not decoration: it should say in words what the picture just showed,
because that sentence is the thing she will remember.

Labs on this site should be about **the consequences of a choice** — what a different
threshold, split, or sample size does to a conclusion — not about animating a formula.

### detect.js API

Shared house engine (identical across SenSym project sites):

| Call | Does |
|---|---|
| `G.rng(seed)` | deterministic uniform generator |
| `G.canvas(id)` | `{c, ctx, w, h, dpr}`, DPR-scaled and cleared |
| `G.frame(ctx,w,h,{xmin,xmax,ymin,ymax,margin})` | coordinate frame |
| `fr.axes({xlabel,ylabel,xticks,yticks,xfmt,yfmt,grid,bg})` | box, grid, ticks, labels. `xticks: 0` suppresses that axis's ticks. |
| `fr.fn(f,{color,width,samples})` | plot y = f(x) |
| `fr.line(pts,{color,width,dash,alpha})` | polyline through `[[x,y],...]` |
| `fr.rect(x0,y0,x1,y1,{fill,alpha,stroke,width})` | filled/stroked rectangle in data coords |
| `fr.dots(pts,{color,size,alpha})` | fast scatter |
| `fr.dot(x,y,{color,r,ring})` | one marker |
| `fr.vline(x,{})` / `fr.hline(y,{})` | dashed reference lines |
| `fr.bars(counts,lo,hi,{color,alpha})` | histogram bars |
| `fr.text(x,y,s,{color,align,dx,dy})` | annotation in data coords |
| `fr.legend([[label,color],...],{left})` | legend |
| `G.controls(id, spec, onchange)` | builds controls, returns live state object |
| `G.say(id, text)` | write the readout |
| `G.fmt(v,d)` / `G.pad(s,n)` | number and string formatting |
| `G.COL` | `ink muted line wash accent accent2 amber green rose violet teal` |
| `G.lab(drawFn)` | run on DOM ready and on resize |

Project-specific:

| Call | Does |
|---|---|
| `G.metrics({tp,fn,fp,tn})` | `{n, acc, prec, rec, f1, spec, majority}`; undefined metrics are `null` |
| `G.wilson(k, n, z)` | Wilson score interval `[lo, hi]`, default 95% |
| `G.pct(v, d)` | percentage string, or `"undefined"` for `null` |
| `G.matrix(id, {tp,fn,fp,tn}, {fnNote})` | renders a real 2×2 `<table class="confusion">` into a host div |
| `G.SAMPLE` | the twelve demo responses, `{id, mis, truth, text}` |
| `G.MISCONCEPTIONS` | the three demo misconceptions, `{id, statement, why}` |
| `G.copyButtons()` / `G.osSwitch()` | run automatically on load |

Control spec types: `range` (min,max,step,value,fmt), `button` (text), `select`
(options `[[value,label],...]`, value), `check` (value). `onchange(state, key)` receives the
key that changed; buttons only fire the callback.

## Confusion matrices

Use `G.matrix()` into a plain `<div id="...">`. A matrix is a table; drawing one on a canvas
is showing off. Pair it with a `.metrics-row` of `.metric` tiles, marking the headline metric
`.metric.lead`.

## OS-specific content

Wrap in `<div class="os-only" data-os="mac">` / `data-os="win"`. Add exactly one
`<div class="os-bar">` per page that needs it, copied from `ollama.html`. `G.osSwitch()`
wires it up and the choice persists across pages. For inline switches use
`<span class="os-only" data-os="mac">`. Give the mac variant `class="os-only on"` so the page
is not blank before JavaScript runs.

## Exercises

5–7 per page, in a `<h2>N · Exercises</h2>` section. Every one gets a complete worked
solution in `<details>` — `check_pages.js` fails a page where any `.exercise` lacks one.

```html
<div class="exercise">
  <div class="ex-head">Exercise N.k <span class="stars">★★</span><span class="tag">by hand</span></div>
  <div class="ex-body"><p>...</p></div>
  <details><summary>Solution</summary><div class="solution"><p>...</p></div></details>
</div>
```

Stars: ★ routine, ★★ requires thought, ★★★ genuinely hard or open-ended.
Tags: `by hand`, `arithmetic`, `code`, `thinking`, `writing`, `notebook`, `research`.

Solutions must be complete and correct, show the working, and end with a sentence connecting
the result forward or backward in the project. A solution that only gives the answer is a
failed solution. Solutions are open by design: this is a textbook, not a test. Reading one
after a real attempt is expected and is not cheating; presenting one as your own at a
check-in is.

## Length

Roughly 1600–2600 words of prose per phase page, 1–3 labs, 5–7 exercises. Setup pages may be
shorter and carry fewer exercises but must still carry at least one lab and a `.box verify`.
Do not pad. She has about five hours a week and most of it should be spent writing data and
code, not reading.

## Verification

```bash
npm install playwright                     # once
node authoring/check_pages.js --all
```

Must print `[ ok ]` for every page. It fails on console errors, page errors, unrendered
`$math$`, blank canvases, canvases that change height when a slider moves, broken relative
links, and exercises without solutions. Broken links to pages that do not exist yet are
expected mid-build; nothing else is acceptable.

The checker needs a Chromium binary. It reads `PW_CHROME` if set.
