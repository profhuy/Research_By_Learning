# RBL-4 Starter Pack

This starter pack is aligned with the approved `RBL-3` proposal direction:

- Topic: GPT-4o mini as a quality gate for GitHub OSS bug reports
- Scope: `OB / EB / S2R`
- Main metric: `Cohen's Kappa`
- Main threshold: `Kappa >= 0.70`
- Pilot in Week 7, full experiment in Week 8

## Folder structure

- `checklist.md`: 7 required gates before Week 7
- `notes.md`: seed, issues, pilot decisions, amendment notes
- `roles-and-handoff.md`: what to send each teammate
- `rubric-ob-eb-s2r.md`: final annotation rubric for `OB`, `EB`, `S2R`
- `prompt_final.md`: frozen prompt for pilot and full experiment
- `pilot-workflow.md`: exact Week 7 pilot flow
- `week8-full-experiment.md`: exact Week 8 full experiment flow
- `colab-kaggle-setup.md`: cloud-running instructions
- `sync-results-to-github.md`: required GitHub sync rules
- `issue-handling-rules.md`: what to do and what not to do when something goes wrong
- `messages-to-team.md`: ready-to-send task messages
- `data/pilot_sample.csv`: pilot sample template
- `data/pilot_ground_truth.csv`: annotation and consensus template
- `data/full_ground_truth.csv`: full annotation and consensus template
- `results/pilot_llm_output.csv`: LLM output template
- `results/pilot_api_log.txt`: API log placeholder
- `results/pilot_analysis_plan.md`: what MS must compute in pilot
- `results/full_llm_output.csv`: full LLM output template
- `results/full_api_log.txt`: full experiment API log placeholder
- `results/summary.csv`: final metric summary template
- `figures/README.md`: figure requirements

## Recommended order

1. Fill `checklist.md`
2. Finalize `notes.md`
3. Populate `data/pilot_sample.csv`
4. Let DG annotate `data/pilot_ground_truth.csv`
5. Let LR run GPT on the pilot and fill `results/pilot_llm_output.csv`
6. Let MS analyze pilot using `results/pilot_analysis_plan.md`

## Important rule

Do not change the proposal direction after seeing the data unless the team writes an amendment note first.
