# Phase 4 — The real run, twice   (9/07/26 - )

**Hours this week (roughly):** 2

## What I worked out

- [proved] The Phase 4 experiment compares two conditions: a baseline condition and a misconception-aware condition.
- [proved] The frozen dataset contains 40 responses: 20 misconception responses and 20 correct responses.
- [proved] Each condition will evaluate all 40 responses, for 80 total model evaluations.
- [observed] The local model being used is `llama3.2:3b`.

## What I built / ran

- Completed and froze the Phase 3 dataset at git tag `phase-3-complete`.
- Verified that `check_setup.py` reports 10 real misconception rows and 40 real response rows.
- Verified that `MODEL_NAME` exactly matches the model shown by `ollama list`: `llama3.2:3b`.
- Ran the mock experiment successfully.
- The mock run produced the green confirmation:
  `✓ Nothing fell back — this run was entirely your code.`
- Prepared the computer for the real run: plugged in, sleep disabled, browser closed.
- Started the real Phase 4 experiment using both the baseline and misconception-aware conditions.
- The real run's provenance and results will be recorded after completion.

## Numbers this week

- Dataset: 40 responses
  - 20 misconception
  - 20 correct
- Conditions: 2
- Total planned model evaluations: 80
- Majority-class baseline: 50%
- Real experimental metrics: **pending completion of the run**
- Baseline: TP=19, FP=1, FN=1, TN=19; accuracy=0.95, precision=0.95, recall=0.95, F1=0.95.
- Misconception-aware: TP=19, FP=3, FN=1, TN=17; accuracy=0.90, precision=0.864, recall=0.95, F1=0.905.
- Decoy: TP=4, FP=4, FN=2, TN=2; accuracy=0.50, precision=0.50, recall=0.667, F1=0.571.
- Majority-class baseline: 50%.
- Unparseable replies: 0 for all three conditions.
- Scikit-learn cross-check: MATCH for all three conditions.

## Checks

- `check_setup.py` passed:
  - Python version requirement
  - required packages
  - 40 response rows
  - 10 misconception rows
  - Ollama running
  - `llama3.2:3b` downloaded
- `ollama list` confirmed the exact model name: `llama3.2:3b`.
- Mock run confirmed that none of the TODO implementations fell back to the worked versions.
- Dataset was committed and the working tree was clean.
- Git tag `phase-3-complete` was created.
- Real-run results have not yet been analyzed.
-  Both baseline and misconception-aware conditions completed successfully.
- All 80 planned experimental evaluations completed.
- No unparseable replies occurred.
- Scikit-learn cross-check matched the custom metric calculations for all conditions.
- The final run again confirmed: "Nothing fell back — this run was entirely your code."
- Results were saved to `metrics.csv`.
- Confusion-matrix and comparison figures were generated.

## Where I'm stuck

- Not currently stuck. The real experiment is running.

## Wins

- Successfully completed the dataset preparation and froze the dataset before running the experiment.
- Got the full setup check to pass.
- Successfully ran the mock experiment with no fallback to the worked implementations.
- Got the experiment ready for the real run.

## Questions for the check-in

- 

## Tools used

Tools used: used ChatGPT to help troubleshoot terminal commands, interpret setup/check outputs, and document the experimental workflow; did not use AI to generate, label, or alter the student response dataset.
