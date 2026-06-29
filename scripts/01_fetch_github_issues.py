"""
01_fetch_github_issues.py
=========================
Fetch bug reports from GitHub OSS repos, filter, and random sample.

Usage:
    python scripts/01_fetch_github_issues.py
    python scripts/01_fetch_github_issues.py --seed 42 --n 250 --pilot-pct 0.12
    python scripts/01_fetch_github_issues.py --token YOUR_GITHUB_TOKEN

Output:
    data/raw/all_issues.csv          — All fetched issues (raw, DO NOT modify)
    data/pilot_sample.csv            — Pilot subset (~12% of N)

Requirements:
    pip install requests pandas
"""

import argparse
import csv
import os
import random
import re
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package not found. Install with: pip install requests")
    exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: 'pandas' package not found. Install with: pip install pandas")
    exit(1)

# ── Configuration ──────────────────────────────────────────────────────────────

REPOS = [
    "pandas-dev/pandas",
    "scikit-learn/scikit-learn",
    "microsoft/vscode",
]

# Labels that indicate a bug report (case-insensitive partial match)
BUG_LABEL_PATTERNS = ["bug", "type:bug", "kind/bug", "type/bug"]

# Minimum word count in issue body
MIN_BODY_WORDS = 50

# GitHub API base
API_BASE = "https://api.github.com"

# Rate limit handling
REQUESTS_PER_BATCH = 30
BATCH_SLEEP_SECONDS = 2


# ── Helper Functions ───────────────────────────────────────────────────────────

def get_headers(token: str | None) -> dict:
    """Build request headers with optional auth token."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RBL4-DataCollector",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def is_bug_label(labels: list[dict]) -> bool:
    """Check if any label matches bug patterns."""
    for label in labels:
        name = label.get("name", "").lower()
        for pattern in BUG_LABEL_PATTERNS:
            if pattern in name:
                return True
    return False


def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def is_likely_english(text: str) -> bool:
    """Simple heuristic: check if text is mostly ASCII (English)."""
    if not text:
        return False
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    return (ascii_chars / len(text)) > 0.85


def fetch_issues_from_repo(repo: str, token: str | None, max_pages: int = 20) -> list[dict]:
    """
    Fetch bug-labeled issues from a GitHub repo.
    Uses pagination to get up to max_pages * 100 issues.
    """
    headers = get_headers(token)
    all_issues = []
    request_count = 0

    for page in range(1, max_pages + 1):
        url = f"{API_BASE}/repos/{repo}/issues"
        params = {
            "state": "all",
            "labels": "bug",
            "per_page": 100,
            "page": page,
            "sort": "created",
            "direction": "desc",
        }

        print(f"  Fetching {repo} page {page}...", end=" ")

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)

            # Handle rate limiting
            if resp.status_code == 403:
                reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
                wait = max(reset_time - int(time.time()), 60)
                print(f"\n  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                resp = requests.get(url, headers=headers, params=params, timeout=30)

            resp.raise_for_status()
            issues = resp.json()

            if not issues:
                print("no more issues.")
                break

            # Filter: must have body, not pull request
            valid = []
            for issue in issues:
                if issue.get("pull_request"):
                    continue
                if not issue.get("body"):
                    continue
                valid.append(issue)

            all_issues.extend(valid)
            print(f"got {len(valid)} valid issues (total: {len(all_issues)})")

            request_count += 1
            if request_count % REQUESTS_PER_BATCH == 0:
                time.sleep(BATCH_SLEEP_SECONDS)

        except requests.exceptions.RequestException as e:
            print(f"\n  Error fetching {repo} page {page}: {e}")
            break

    return all_issues


def process_issues(raw_issues: list[dict], repo: str) -> list[dict]:
    """Process raw GitHub API response into structured records."""
    processed = []
    for issue in raw_issues:
        body = issue.get("body", "") or ""
        title = issue.get("title", "") or ""

        # Filter: minimum body word count
        if count_words(body) < MIN_BODY_WORDS:
            continue

        # Filter: likely English
        if not is_likely_english(body):
            continue

        labels = issue.get("labels", [])
        label_names = ",".join(l.get("name", "") for l in labels)

        processed.append({
            "repo": repo.split("/")[-1],
            "issue_id": issue["number"],
            "issue_url": issue["html_url"],
            "title": title,
            "body": body,
            "created_at": issue.get("created_at", ""),
            "state": issue.get("state", ""),
            "labels": label_names,
        })

    return processed


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub bug reports for RBL-4")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--n", type=int, default=250, help="Total sample size (default: 250)")
    parser.add_argument("--pilot-pct", type=float, default=0.12, help="Pilot percentage (default: 0.12)")
    parser.add_argument("--token", type=str, default=None, help="GitHub personal access token")
    parser.add_argument("--max-pages", type=int, default=20, help="Max pages to fetch per repo")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be done")
    args = parser.parse_args()

    # Try to get token from environment if not provided
    token = args.token or os.environ.get("GITHUB_TOKEN")

    if not token:
        print("WARNING: No GitHub token provided.")
        print("  Unauthenticated requests are limited to 60/hour.")
        print("  Set GITHUB_TOKEN env var or use --token flag.")
        print()

    # Paths
    project_root = Path(__file__).parent.parent
    raw_dir = project_root / "data" / "raw"
    data_dir = project_root / "data"
    raw_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== RBL-4 GitHub Issue Fetcher ===")
    print(f"Seed: {args.seed}")
    print(f"Target N: {args.n}")
    print(f"Pilot %: {args.pilot_pct * 100:.0f}%")
    print(f"Repos: {', '.join(REPOS)}")
    print()

    if args.dry_run:
        print("[DRY RUN] Would fetch from repos and sample. Exiting.")
        return

    # ── Step 1: Fetch from all repos ──
    all_processed = []
    for repo in REPOS:
        print(f"\n── Fetching: {repo} ──")
        raw = fetch_issues_from_repo(repo, token, args.max_pages)
        processed = process_issues(raw, repo)
        print(f"  After filtering: {len(processed)} issues")
        all_processed.extend(processed)

    print(f"\n── Total issues after filtering: {len(all_processed)} ──")

    if len(all_processed) < args.n:
        print(f"WARNING: Only {len(all_processed)} issues available, less than target N={args.n}")
        print(f"  Will use all {len(all_processed)} issues.")
        args.n = len(all_processed)

    # ── Step 2: Remove duplicates ──
    seen = set()
    unique = []
    for issue in all_processed:
        key = (issue["repo"], issue["issue_id"])
        if key not in seen:
            seen.add(key)
            unique.append(issue)
    all_processed = unique
    print(f"  After dedup: {len(all_processed)} unique issues")

    # ── Step 3: Save raw data ──
    raw_df = pd.DataFrame(all_processed)
    raw_path = raw_dir / "all_issues.csv"
    raw_df.to_csv(raw_path, index=False, quoting=csv.QUOTE_ALL)
    print(f"\n  Saved raw data: {raw_path} ({len(raw_df)} rows)")

    # ── Step 4: Random sample N ──
    random.seed(args.seed)
    if len(all_processed) > args.n:
        sample = random.sample(all_processed, args.n)
    else:
        sample = all_processed
    print(f"  Sampled N={len(sample)} with seed={args.seed}")

    # ── Step 5: Random sample pilot ──
    pilot_size = max(1, int(len(sample) * args.pilot_pct))
    random.seed(args.seed)  # Reset seed for reproducibility
    pilot_indices = set(random.sample(range(len(sample)), pilot_size))

    pilot_issues = []
    for i, issue in enumerate(sample):
        issue_copy = issue.copy()
        if i in pilot_indices:
            issue_copy["selected_for_pilot"] = "TRUE"
            issue_copy["notes"] = ""
            pilot_issues.append(issue_copy)
        else:
            issue_copy["selected_for_pilot"] = "FALSE"
            issue_copy["notes"] = ""

    # ── Step 6: Save pilot sample ──
    pilot_df = pd.DataFrame(pilot_issues)

    # Sort by repo for readability
    pilot_df = pilot_df.sort_values(["repo", "issue_id"]).reset_index(drop=True)

    pilot_path = data_dir / "pilot_sample.csv"
    pilot_df.to_csv(pilot_path, index=False, quoting=csv.QUOTE_ALL)
    print(f"  Saved pilot sample: {pilot_path} ({len(pilot_df)} rows)")

    # ── Step 7: Print distribution ──
    print(f"\n── Pilot Distribution ──")
    for repo in pilot_df["repo"].unique():
        count = len(pilot_df[pilot_df["repo"] == repo])
        print(f"  {repo}: {count} issues")

    print(f"\n── Summary ──")
    print(f"  Total fetched & filtered: {len(all_processed)}")
    print(f"  Full sample N: {len(sample)}")
    print(f"  Pilot sample: {len(pilot_issues)}")
    print(f"  Seed: {args.seed}")
    print(f"\n  Remember to update notes.md with the seed and pilot size!")
    print(f"  Done!")


if __name__ == "__main__":
    main()
