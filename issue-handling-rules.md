# Issue Handling Rules

These rules apply during pilot and full experiment.

## If results are lower than the threshold

Do not:

- change the threshold
- invent a new RQ
- cherry-pick a better subset

Do:

- report the real result
- explain likely reasons in the final report

## If the dataset has fewer valid samples than expected

Do not:

- add unverified data carelessly

Do:

- record the deviation
- inform the supervisor if the change is large
- write an amendment note if scope meaningfully changes

## If API returns unexpected format

Do not:

- silently delete the row
- guess labels manually

Do:

- log the case
- mark invalid rows explicitly
- count invalid rate separately

## If metric cannot be computed for some cases

Do not:

- replace missing values with zero without explanation

Do:

- mark the case as `INVALID`
- report how many invalid rows exist
- separate valid vs invalid counts in the summary
