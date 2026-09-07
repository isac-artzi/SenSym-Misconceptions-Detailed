# Phase 2 — Six TODOs, on fake data   (9/01/26 - 9/04/26)

**Hours this week (roughly):** 10 

## What I worked out

- [proved] The Reference Fallback mechanism and how it means a crash is a real bug.
- [proved] Which 6 TODOs the program can track.
- [proved] Why mock mode removes one source of failure.
- [proved] Everything `--mock` and `--sample` produce is demo data.
- [proved] The purpose of each TODO and how the completed pieces fit together into the overall evaluation pipeline.
- [proved] Why fake/mock data should not be treated as experimental results.
- [observed] Running the completed code through the terminal confirmed that the TODOs were connected correctly and that the program could run using the mock setup.

## What I built / ran

- Completed all 6 TODOs in the Phase 2 code.
- Ran the program through the terminal using the mock/demo setup.
- Verified that the completed code could run without relying on real model responses.
- Used `--mock` and `--sample` to test the pipeline with demo data rather than treating those outputs as research results.

## Numbers this week

- No experimental metrics were computed this week because the runs used fake/demo data.
- No TP / FN / FP / TN results are being reported from the mock or sample runs.
- The 50% majority-class baseline remains the planned comparison point for the actual experiment.

## Checks

- Verified that all 6 TODOs were completed and passed.
- Ran the completed program through the terminal using the mock setup.
- Confirmed that the mock/sample runs produced demo data and were not being treated as real experimental results.
- Checked that the program ran without needing real model responses during this phase.
- Diagnosed and fixed code issues that appeared while completing the TODOs.

## Where I'm stuck

- I can show X: I can show the code I have written/filled in and the terminal with the running mock model.
- I need Y: I need to fill in my CSV file with the actual data/responses needed for the experiment.
- The gap is Z: The gap is in determining the formatting and nature of the responses I need to fill in so that the CSV matches what the experiment expects.

## Wins

- All 6 TODOs passed, all code was written, and everything was set up through the terminal.
- I was able to run the completed program using mock/demo data.
- I learned how the Reference Fallback mechanism works and why a crash should be treated as a real bug rather than silently replaced with a fallback result.
- I was able to identify and troubleshoot issues in my own code setup.

## Questions for the check-in

- None as of this stage.

## Tools used

Tools used: Asked Codex why my filled-in code was failing; did not use it to write code.
