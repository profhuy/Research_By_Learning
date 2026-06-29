"""
compute_iaa.py
==============
Compute Inter-Annotator Agreement (Cohen's Kappa, linear weighted)
between two annotators for OB, EB, S2R dimensions.

Usage:
    python scripts/compute_iaa.py --input data/pilot_ground_truth.csv
    python scripts/compute_iaa.py --input data/full_ground_truth.csv
    python scripts/compute_iaa.py --test  (run on dummy data to verify gate E4)

Output:
    Prints IAA results to console and checks against threshold.

Requirements:
    pip install pandas scikit-learn
"""

import argparse
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("ERROR: 'pandas' not found. Install with: pip install pandas")
    sys.exit(1)

try:
    from sklearn.metrics import cohen_kappa_score
except ImportError:
    print("ERROR: 'scikit-learn' not found. Install with: pip install scikit-learn")
    sys.exit(1)


# ── Configuration ──────────────────────────────────────────────────────────────

DIMENSIONS = ["ob", "eb", "s2r"]
VALID_LABELS = {"Sufficient", "Ambiguous", "Missing", "Incorrect"}
IAA_THRESHOLD = 0.70
IAA_GOOD = 0.80


# ── Functions ──────────────────────────────────────────────────────────────────

def validate_labels(series: pd.Series, col_name: str) -> list[str]:
    """Check that all labels are valid. Return list of warnings."""
    warnings = []
    invalid = series.dropna().apply(lambda x: x.strip() if isinstance(x, str) else x)
    invalid_vals = set(invalid) - VALID_LABELS
    if invalid_vals:
        warnings.append(f"  WARNING: {col_name} has invalid labels: {invalid_vals}")
    return warnings


def compute_kappa(ann1: pd.Series, ann2: pd.Series, dimension: str) -> dict:
    """
    Compute Cohen's Kappa (linear weighted) for a single dimension.
    Returns dict with dimension, kappa, raw_agreement, n_pairs, status.
    """
    # Drop rows where either annotator has NaN
    mask = ann1.notna() & ann2.notna()
    a1 = ann1[mask].values
    a2 = ann2[mask].values
    n_pairs = len(a1)

    if n_pairs == 0:
        return {
            "dimension": dimension.upper(),
            "kappa": None,
            "raw_agreement": None,
            "n_pairs": 0,
            "status": "NO_DATA",
        }

    # Cohen's Kappa with linear weights (as specified in proposal)
    kappa = cohen_kappa_score(a1, a2, weights="linear")

    # Raw agreement
    raw_agree = (a1 == a2).sum() / n_pairs

    # Status
    if kappa >= IAA_GOOD:
        status = "GOOD"
    elif kappa >= IAA_THRESHOLD:
        status = "ACCEPTABLE"
    else:
        status = "BELOW_THRESHOLD"

    return {
        "dimension": dimension.upper(),
        "kappa": round(kappa, 4),
        "raw_agreement": round(raw_agree, 4),
        "n_pairs": n_pairs,
        "status": status,
    }


def run_on_file(filepath: str) -> bool:
    """
    Compute IAA from a ground truth CSV file.
    Returns True if all dimensions pass threshold, False otherwise.
    """
    print(f"\n{'='*60}")
    print(f"  Computing IAA: {filepath}")
    print(f"{'='*60}\n")

    df = pd.read_csv(filepath)
    print(f"  Total rows: {len(df)}")

    # Filter to double-labeled rows only
    if "double_labeled" in df.columns:
        dl = df[df["double_labeled"].astype(str).str.upper() == "TRUE"]
        print(f"  Double-labeled rows: {len(dl)}")
        pct = len(dl) / len(df) * 100 if len(df) > 0 else 0
        print(f"  Double-label rate: {pct:.1f}%")
        if pct < 30:
            print(f"  WARNING: Double-label rate < 30% (required by proposal)")
    else:
        dl = df
        print(f"  WARNING: No 'double_labeled' column found. Using all rows.")

    if len(dl) == 0:
        print("\n  ERROR: No double-labeled rows found. Cannot compute IAA.")
        return False

    # Validate labels
    all_warnings = []
    for dim in DIMENSIONS:
        col1 = f"annotator_1_{dim}"
        col2 = f"annotator_2_{dim}"
        if col1 in dl.columns:
            all_warnings.extend(validate_labels(dl[col1], col1))
        if col2 in dl.columns:
            all_warnings.extend(validate_labels(dl[col2], col2))

    if all_warnings:
        print("\n  Label Validation Warnings:")
        for w in all_warnings:
            print(w)

    # Compute Kappa for each dimension
    results = []
    all_pass = True

    print(f"\n  {'Dimension':<12} {'Kappa':<10} {'Raw Agree':<12} {'N Pairs':<10} {'Status'}")
    print(f"  {'-'*12} {'-'*10} {'-'*12} {'-'*10} {'-'*20}")

    for dim in DIMENSIONS:
        col1 = f"annotator_1_{dim}"
        col2 = f"annotator_2_{dim}"

        if col1 not in dl.columns or col2 not in dl.columns:
            print(f"  {dim.upper():<12} {'N/A':<10} {'N/A':<12} {'0':<10} COLUMNS_MISSING")
            all_pass = False
            continue

        result = compute_kappa(dl[col1], dl[col2], dim)
        results.append(result)

        kappa_str = f"{result['kappa']:.4f}" if result['kappa'] is not None else "N/A"
        agree_str = f"{result['raw_agreement']:.1%}" if result['raw_agreement'] is not None else "N/A"

        status_icon = "✅" if result["status"] == "GOOD" else "⚠️" if result["status"] == "ACCEPTABLE" else "❌"
        print(f"  {result['dimension']:<12} {kappa_str:<10} {agree_str:<12} {str(result['n_pairs']):<10} {status_icon} {result['status']}")

        if result["status"] == "BELOW_THRESHOLD":
            all_pass = False

    # Overall verdict
    print(f"\n  {'='*60}")
    if all_pass:
        print(f"  ✅ ALL DIMENSIONS PASS IAA THRESHOLD (Kappa >= {IAA_THRESHOLD})")
        print(f"  → Safe to proceed.")
    else:
        print(f"  ❌ ONE OR MORE DIMENSIONS BELOW THRESHOLD (Kappa < {IAA_THRESHOLD})")
        print(f"  → STOP. Clarify rubric and re-label conflicting cases.")
        print(f"  → Report to PL (Huy) before proceeding.")
    print(f"  {'='*60}")

    return all_pass


def run_test():
    """Run on dummy data to verify gate E4 (script works without errors)."""
    import numpy as np

    print("\n  Running gate E4 test with dummy data...")

    np.random.seed(42)
    n = 20
    labels = list(VALID_LABELS)

    data = {
        "repo": ["test"] * n,
        "issue_id": list(range(1, n + 1)),
        "issue_url": [f"https://github.com/test/test/issues/{i}" for i in range(1, n + 1)],
        "double_labeled": ["TRUE"] * n,
    }

    # Generate correlated dummy labels (high agreement)
    for dim in DIMENSIONS:
        base = np.random.choice(labels, n)
        # Annotator 2 agrees ~80% of the time
        ann2 = base.copy()
        flip_indices = np.random.choice(n, size=int(n * 0.2), replace=False)
        for idx in flip_indices:
            ann2[idx] = np.random.choice(labels)

        data[f"annotator_1_{dim}"] = base
        data[f"annotator_2_{dim}"] = ann2
        data[f"consensus_{dim}"] = base
        data["consensus_notes"] = [""] * n

    df = pd.DataFrame(data)

    # Save to temp location
    project_root = Path(__file__).parent.parent
    test_path = project_root / "data" / "test_dummy_ground_truth.csv"
    df.to_csv(test_path, index=False)
    print(f"  Saved dummy data to: {test_path}")

    result = run_on_file(str(test_path))

    # Clean up
    test_path.unlink(missing_ok=True)
    print(f"\n  Gate E4 {'PASSED' if True else 'FAILED'}: Script runs without errors.")
    print(f"  (Dummy data IAA result: {'PASS' if result else 'FAIL'} — this is expected for random data)")

    return True


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compute IAA for RBL-4 ground truth")
    parser.add_argument("--input", type=str, help="Path to ground truth CSV")
    parser.add_argument("--test", action="store_true", help="Run on dummy data (gate E4 check)")
    args = parser.parse_args()

    if args.test:
        run_test()
    elif args.input:
        success = run_on_file(args.input)
        sys.exit(0 if success else 1)
    else:
        print("Usage:")
        print("  python scripts/compute_iaa.py --test")
        print("  python scripts/compute_iaa.py --input data/pilot_ground_truth.csv")
        sys.exit(1)


if __name__ == "__main__":
    main()
