# Week 8 - Full Experiment

This document follows the Week 8 instructions after a valid pilot.

## 8.1 Full dataset annotation (DG)

DG must:

1. Annotate the full dataset into:
   - `data/full_ground_truth.csv`
2. Compute IAA on the full required double-label subset
3. Confirm the IAA threshold still satisfies the approved proposal

If IAA is below threshold:

- stop before running the LLM on the full set
- clarify the guideline
- re-label the conflicting subset first

## 8.2 Run LLM on the full dataset (LR)

LR must:

1. Run the same configuration used in the pilot
2. Write logs to:
   - `results/full_api_log.txt`
3. Write parsed outputs to:
   - `results/full_llm_output.csv`
4. Commit to GitHub after each large batch

### API issue handling

- Empty response -> mark `INVALID`, do not auto-fill labels
- Rate limit -> use retry with exponential backoff
- Response format changes unexpectedly -> report to PL immediately

## 8.3 Statistical analysis (MS)

Run:

- `results/full_analysis.ipynb`

MS must:

1. Compute all metrics on full output
2. Run the statistical test already chosen in the proposal
3. Report effect size
4. Write results into:
   - `results/summary.csv`
5. Conclude whether each RQ rejects or fails to reject H0

### Important rule

Do not change the statistical test after seeing the data just because one result looks better.

## 8.4 Figures (RW)

Save figures under:

- `figures/`

Each figure must have:

- title
- axis labels
- N annotation
- at least 300 DPI

At minimum prepare:

1. a distribution plot for the main metric
2. a comparison plot if there is a comparative RQ
