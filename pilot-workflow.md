# Pilot Workflow

## Step 1 - Huy checks the 7 gates

- Open `checklist.md`
- Do not start pilot until all critical blockers are known

## Step 2 - Hung prepares pilot data

- Fill `data/pilot_sample.csv`
- Use random selection from the approved repositories
- Record the random seed in `notes.md`
- Keep issue text raw; do not rewrite the reports

## Step 3 - Hung prepares ground truth

- Fill annotator 1 labels for all pilot rows
- Fill annotator 2 labels for at least 30% of rows
- Resolve disagreement and fill consensus columns
- Record IAA in `notes.md`

## Step 4 - Phuc runs LLM

- Use only `prompt_final.md`
- Use `GPT-4o mini`, `temperature = 0.0`
- Save parsed output into `results/pilot_llm_output.csv`
- Save per-call logs into `results/pilot_api_log.txt`

## Step 5 - Them analyzes pilot

- Compute Human-Human Kappa
- Compute LLM-vs-Developer Kappa
- Compute overall and per-dimension agreement
- Check label distribution
- Record findings in `notes.md`

## Step 6 - Huy decides next action

- If pipeline is stable -> continue to full experiment
- If only a small script bug exists -> fix same day
- If metric cannot be computed or pilot invalidates setup -> prepare amendment note
