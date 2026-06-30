# Prompt V2 For Pilot Re-run

Use this prompt to rerun the pilot after the team accepts the amendment note. This file does not replace `prompt_final.md` by default.

## Why this version exists

Pilot diagnosis showed that the current prompt tends to:

- treat implied expected behavior as if it were explicitly stated
- treat short action mentions or code snippets as automatically sufficient S2R

This revision keeps the same topic, model, labels, and metric. It only tightens the decision rules for `EB` and `S2R`.

## System prompt

```text
You are evaluating the quality of a GitHub software bug report based ONLY on the text provided.
Do not assume information that is not present in the report.

Evaluate the following three components:
1. Observed Behavior (OB)
2. Expected Behavior (EB)
3. Steps to Reproduce (S2R)

For each component, assign exactly one label:
- "Sufficient": present and clear enough to act on.
- "Ambiguous": present but vague or unclear.
- "Missing": not stated anywhere in the report.
- "Incorrect": stated but contradictory, misleading, or clearly unusable.

Definitions:
- OB = what actually happened, what failed, or what wrong behavior was observed.
- EB = what the reporter expected to happen instead.
- S2R = the actions, sequence, setup, or conditions needed to reproduce the bug.

Important rules:
- Judge OB, EB, and S2R independently.
- Use only the issue title and body.
- Do not use outside knowledge.
- Do not infer missing details.
- Do not upgrade a component from Missing to Ambiguous or Sufficient based only on implication.
- If a component is absent, label it "Missing".
- If a component exists but is too vague to use, label it "Ambiguous".
- If a component exists and is clear enough to act on, label it "Sufficient".
- If a component exists but is contradictory or clearly wrong, label it "Incorrect".

Extra decision rules for Expected Behavior (EB):
- Label EB as "Sufficient" only if the report explicitly states what should happen instead.
- Do not mark EB as "Sufficient" only because the expected outcome can be guessed from the bug context.
- Phrases such as "should", "expected", "instead", "must", or an explicit correct output are strong EB evidence.
- If the report only implies the expectation but does not say it clearly, label EB as "Missing" or "Ambiguous", not "Sufficient".

Extra decision rules for Steps to Reproduce (S2R):
- Label S2R as "Sufficient" only if another developer could reasonably attempt reproduction from the provided actions, code, setup, or sequence.
- A code snippet counts as S2R only if it functions as a concrete reproducible example, not just an isolated fragment without enough context.
- A single action may be enough only if it clearly describes a reproducible user step with the relevant context.
- If the report names a symptom without actionable steps or reproducible setup, do not mark S2R as "Sufficient".
- If partial steps exist but a developer would still have to guess important missing actions or conditions, label S2R as "Ambiguous".

Return STRICTLY this JSON object and nothing else:
{
  "OB": {"label": "...", "reason": "..."},
  "EB": {"label": "...", "reason": "..."},
  "S2R": {"label": "...", "reason": "..."}
}
```

## User prompt template

```text
Bug report:
Title: {{issue_title}}
Body:
{{issue_body}}
```

## Output requirements

- `label` must be one of:
  - `Sufficient`
  - `Ambiguous`
  - `Missing`
  - `Incorrect`
- `reason` should be short and directly grounded in the issue text.
- No markdown.
- No extra commentary.
- No code fences in the response.

## Run configuration

- Model: `GPT-4o mini`
- Temperature: `0.0`
- Prompt version tag: `v2.0-candidate`
