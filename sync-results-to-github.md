# Sync Results To GitHub

Whether you run locally, on Colab, or on Kaggle, the final outputs must be committed back to GitHub.

## Required files to sync after pilot

- `results/pilot_llm_output.csv`
- `results/pilot_api_log.txt`

## Required files to sync after full experiment

- `results/full_llm_output.csv`
- `results/full_api_log.txt`
- `results/summary.csv`
- `figures/`

## Example commit commands

```bash
git add results/pilot_llm_output.csv results/pilot_api_log.txt
git commit -m "feat: add pilot experiment results"
git push
```

```bash
git add results/full_llm_output.csv results/full_api_log.txt results/summary.csv figures/
git commit -m "feat: add full experiment output and analysis"
git push
```

## Good commit message examples

- `feat: add pilot results (N=26)`
- `feat: add full experiment output and api log`
- `feat: add week8 figures and summary`

## Avoid vague commit messages

- `update`
- `final`
- `done`
