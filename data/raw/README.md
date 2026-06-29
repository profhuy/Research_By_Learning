# Data Source Documentation

## Source
- **API**: GitHub REST API v3
- **Repositories**:
  - `pandas-dev/pandas` (License: BSD-3-Clause)
  - `scikit-learn/scikit-learn` (License: BSD-3-Clause)
  - `microsoft/vscode` (License: MIT)

## Collection Parameters
- **Filter**: Issues with label containing "bug"
- **Body minimum**: 50 words
- **Language**: English only
- **Date range**: 2023-01-01 to 2026-06-01
- **Download date**: ___
- **Random seed**: 42
- **Total fetched**: ___
- **Total after filter**: ___
- **Final sample N**: 250
- **Pilot subset**: ~30 (12% of N)

## Column Structure (all_issues.csv)
| Column | Type | Description |
|---|---|---|
| repo | string | Repository name |
| issue_id | int | GitHub issue number |
| issue_url | string | Full URL to the issue |
| title | string | Issue title |
| body | string | Issue body (raw markdown) |
| created_at | datetime | Issue creation date |
| state | string | open / closed |
| labels | string | Comma-separated label names |

## Important Notes
- Raw data files in this folder must NOT be modified after download
- All filtering and sampling is done by scripts/01_fetch_github_issues.py
- Re-running the script with the same seed will produce the same sample
