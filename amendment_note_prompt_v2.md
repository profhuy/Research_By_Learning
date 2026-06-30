# Amendment Note - Prompt Clarification For Pilot Re-run

**Date:** 2026-06-30  
**Scope:** Pilot re-run only, before full experiment  
**Requested by:** Team RBL-4  

## Reason for amendment

The first pilot run completed successfully at the technical level:

- valid LLM output was produced for all 30 pilot issues
- output format and API logging were correct

However, agreement with human labels did not meet the approved threshold:

- `OB` Kappa = `1.0000`
- `EB` Kappa = `0.6528`
- `S2R` Kappa = `0.4000`
- Overall Kappa across `OB + EB + S2R` = `0.5822`

Pilot diagnosis showed a consistent error pattern:

- the model often treated implied expected behavior as explicit EB
- the model often treated short action mentions or code snippets as automatically sufficient S2R

This suggests a prompt-specification mismatch rather than a pipeline failure.

## What changes

We propose a clarification-only amendment to the prompt:

- keep the same topic
- keep the same model: `GPT-4o mini`
- keep the same metric: `Cohen's Kappa`
- keep the same threshold: `Kappa >= 0.70`
- keep the same four labels: `Sufficient`, `Ambiguous`, `Missing`, `Incorrect`
- tighten decision rules for `EB` and `S2R` so the model does not rely on implication

The revised prompt for the pilot re-run is stored in:

- `prompt_v2_candidate.md`

## What does NOT change

This amendment does **not** change:

- research direction
- dataset source
- model family
- temperature
- metric
- threshold
- label set

## Decision rule for the team

If the team approves this amendment:

1. archive the first pilot result as `pilot-v1`
2. rerun the same pilot sample with `prompt_v2_candidate.md`
3. compare Kappa values between prompt versions
4. proceed to full experiment only after the team documents which prompt version is adopted

If the team does not approve this amendment:

- keep the original prompt
- report the below-threshold pilot result honestly

## Short justification for report/proposal tracking

The amendment is necessary to align the operational prompt with the intended rubric, especially for explicit `EB` evidence and actionable `S2R` evidence. It is not a threshold change or model change.
