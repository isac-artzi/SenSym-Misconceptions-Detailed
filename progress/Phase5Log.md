# Phase 5 — Analysis / Write-Up   (9/15/26 - 9/20/26)

**Hours this week (roughly):** 2

## What I worked out

* [proved] Phase 5 is focused on analyzing and writing up the results from the Phase 4 experiment rather than running another model experiment.
* [proved] The same 40 responses were used in both the baseline and misconception-aware conditions, so the results can be compared as paired responses.
* [proved] Wilson 95% confidence intervals are needed because the dataset is only 40 responses.
* [proved] The main comparison is baseline vs. misconception-aware. The decoy is treated as a diagnostic rather than a third main experimental arm.
* [observed] The misconception-aware condition did not improve overall detection in this pilot.
* [observed] Recall stayed at 95% in both conditions, but accuracy, precision, and F1 were lower for the misconception-aware condition.

## What I built / ran

* Ran the real Phase 4 experiment with the baseline and misconception-aware conditions.
* Ran the decoy condition as a diagnostic.
* Ran the analysis script and generated `metrics.csv`.
* Generated the confusion-matrix and comparison figures.
* Calculated Wilson 95% confidence intervals for accuracy, precision, and recall.
* Compared the same 40 responses across both main conditions using paired flips.
* Inspected the responses that changed between baseline and misconception-aware.
* Inspected the false negatives for both conditions.
* Checked the model reasoning for the flipped responses, including the cases where the model's reasoning and final prediction did not agree.
* Confirmed that the custom metric calculations matched scikit-learn.

## Numbers this week

* Dataset: 40 responses

  * 20 misconception
  * 20 correct
* Conditions: 2 main conditions + 1 diagnostic decoy
* Total main-condition model evaluations: 80
* Majority-class baseline: 50%
* Baseline accuracy: **95%**

  * Wilson 95% CI: **83.8–98.7%**
* Misconception-aware accuracy: **90%**

  * Wilson 95% CI: **76.9–95.8%**
* Baseline precision: **95%**

  * Wilson 95% CI: **76.3–99.3%**
* Misconception-aware precision: **86.4%**

  * Wilson 95% CI: **65.6–95.4%**
* Baseline recall: **95%**

  * Wilson 95% CI: **76.3–99.3%**
* Misconception-aware recall: **95%**

  * Wilson 95% CI: **76.3–99.3%**
* Baseline F1: **95%**
* Misconception-aware F1: **90.5%**
* Baseline false positives: **1**
* Misconception-aware false positives: **3**
* Baseline false negatives: **1**
* Misconception-aware false negatives: **1**
* Paired flips:

  * **b = 1:** baseline wrong → aware correct (S34)
  * **c = 3:** baseline correct → aware wrong (S04, S24, S37)
* Net paired change: **−2**
* Unparseable replies: **0**

## Checks

* Wilson confidence intervals calculated.
* Paired-flip analysis completed.
* False-negative inspection completed.
* Flipped responses inspected:

  * S04
  * S24
  * S34
  * S37
* Baseline FN: **S34**
* Aware FN: **S37**
* Scikit-learn cross-check: **MATCH**
* No fallback occurred.
* Decoy treated as a diagnostic, not a third main condition.
* Results saved to `metrics.csv`.
* Confusion matrices and comparison figures generated.
* Main result: the misconception-aware condition kept the same recall but increased false positives and lowered accuracy, precision, and F1.

## Where I'm stuck

* How to formulate this into a write up formally

## Wins

* Finished the actual experiment and analysis.
* Got real results instead of mock results.
* Calculated confidence intervals instead of only reporting the raw percentages.
* Compared the same responses across conditions instead of treating the two groups as independent.
* Found that the catalogue helped in one case (S34) but also caused several false positives and missed S37.
* Found a useful reasoning/prediction mismatch in S37 that may be worth discussing.
* Confirmed that all responses were parseable and that the metric calculations matched scikit-learn.

## Questions for the check-in

* Why might the misconception catalogue have caused more false positives?
* How should I interpret the fact that recall stayed at 95% but precision decreased?
* Should I investigate the reasoning/prediction mismatch in S37 further?
* What should the next experiment change: the catalogue, the prompt, the model, or the dataset?

## Tools used

Tools used: used ChatGPT to help interpret the experiment outputs, calculate/check confidence intervals, organize the paired-flip analysis, and document the results; did not use AI to generate, label, or alter the student response dataset.

