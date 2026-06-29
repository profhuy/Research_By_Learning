# Rubric For OB / EB / S2R Annotation

This rubric must be used consistently by both annotators and by the final LLM prompt.

## Core labels

Each component must receive exactly one label:

- `Sufficient`
- `Ambiguous`
- `Missing`
- `Incorrect`

## 1. Observed Behavior (OB)

### What OB means

`Observed Behavior` is the actual faulty behavior reported by the user. It should describe what happened, what went wrong, or what unexpected system output/state was seen.

### Label definitions for OB

- `Sufficient`
  - The report clearly states what actually happened.
  - A developer can understand the faulty behavior without guessing.
  - Example signals:
    - crash message is described
    - wrong output is described
    - UI/system behavior is described concretely

- `Ambiguous`
  - There is some description of the problem, but it is vague.
  - A developer would still need clarification.
  - Example signals:
    - “it does not work”
    - “wrong result”
    - “something is broken”

- `Missing`
  - No real faulty behavior is stated.
  - The report may only contain a title, a question, or expected behavior with no actual observed failure.

- `Incorrect`
  - The observed behavior is contradictory, misleading, or clearly unusable.
  - The text claims something that conflicts with the rest of the report.

## 2. Expected Behavior (EB)

### What EB means

`Expected Behavior` is what the reporter believes should have happened instead.

### Label definitions for EB

- `Sufficient`
  - The expected system behavior is explicitly stated and understandable.
  - A developer can compare expected vs actual behavior directly.

- `Ambiguous`
  - The expected behavior exists, but it is weak, vague, or only implied.
  - Example:
    - “it should work normally”
    - “it should be fixed”

- `Missing`
  - No expected behavior is stated anywhere in the report.

- `Incorrect`
  - The stated expectation is contradictory, technically invalid, or inconsistent with the issue context.

## 3. Steps to Reproduce (S2R)

### What S2R means

`Steps to Reproduce` are the actions, sequence, setup, or conditions needed to trigger the bug.

### Label definitions for S2R

- `Sufficient`
  - The report provides clear steps or conditions that a developer could reasonably follow.
  - Exact numbering is not required, but the reproduction path is understandable.

- `Ambiguous`
  - Some reproduction hint exists, but it is incomplete or unclear.
  - Example:
    - missing environment details
    - missing one or more key actions
    - sequence is implied but not explicit

- `Missing`
  - No usable reproduction step or condition is provided.

- `Incorrect`
  - The reproduction information is self-contradictory, obviously wrong, or unusable.

## Tie-breaking rules

Use these rules when annotators hesitate between labels:

1. If the component is not present at all -> `Missing`
2. If the component exists but is vague -> `Ambiguous`
3. If the component exists and is clear enough to act on -> `Sufficient`
4. If the component exists but is misleading, contradictory, or clearly wrong -> `Incorrect`

## Important annotation rules

- Judge each component independently.
- Do not reward domain knowledge that is not written in the issue text.
- Do not assume hidden context from linked pages unless the text itself includes the needed information.
- Do not use the eventual fix, comments, or external discussion when assigning the core label unless the proposal explicitly allows it.
- If unsure between `Ambiguous` and `Missing`, choose:
  - `Missing` when the component is absent
  - `Ambiguous` when some weak evidence exists

## Suggested examples

### OB examples

- `Sufficient`: “Running `groupby().sum()` on the attached dataframe raises `KeyError: sales`.”
- `Ambiguous`: “The output is wrong.”
- `Missing`: “Please help with this bug.”
- `Incorrect`: “The system crashes successfully and works fine at the same time.”

### EB examples

- `Sufficient`: “The command should return the grouped totals without raising an exception.”
- `Ambiguous`: “It should behave correctly.”
- `Missing`: no expectation described
- `Incorrect`: “The method should return random values every time” when the report context clearly expects deterministic output

### S2R examples

- `Sufficient`: “1. Open file X. 2. Run command Y. 3. Click Z. 4. Crash occurs.”
- `Ambiguous`: “Try running the same workflow as usual and it breaks.”
- `Missing`: no reproduction action or setup at all
- `Incorrect`: steps contradict the report context or refer to impossible actions
