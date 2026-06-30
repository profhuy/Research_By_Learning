"""
RBL-4 Metrics & Statistics (Them - MS).

Reads:
  - data/<mode>_ground_truth.csv   (annotator_1_*, annotator_2_*, consensus_*)
  - results/<mode>_llm_output.csv  (llm_*_label, raw_json_status)

Computes:
  - Human-Human Cohen's Kappa (annotator_1 vs annotator_2), per component + overall
  - LLM-vs-Developer Cohen's Kappa (llm_*_label vs consensus_*), per component + overall
  - Raw agreement for both
  - Label distribution (consensus vs LLM)
  - N valid / N invalid (raw_json_status != VALID is excluded from LLM-vs-Dev)

Writes:
  - results/summary.csv            (matches existing repo header exactly)
  - results/pilot_analysis_plan.md (appends a "Computed results" section)

Run from the REPO ROOT:
  python src/compute_metrics.py --mode pilot
  python src/compute_metrics.py --mode full
"""

import argparse
import csv
import os
from collections import Counter

ALLOWED_LABELS = ["Sufficient", "Ambiguous", "Missing", "Incorrect"]
COMPONENTS = ("OB", "EB", "S2R")

# Accepted range for Kappa under the current team decision (not a hard >=0.70 cutoff).
RANGE_MIN = 0.6
RANGE_MAX = 0.8


def cohen_kappa(pairs):
    """pairs: list of (label_a, label_b) tuples, both non-empty."""
    pairs = [(a, b) for a, b in pairs if a and b]
    n = len(pairs)
    if n == 0:
        return None
    agree = sum(1 for a, b in pairs if a == b)
    po = agree / n
    count_a = Counter(a for a, _ in pairs)
    count_b = Counter(b for _, b in pairs)
    pe = sum((count_a.get(l, 0) / n) * (count_b.get(l, 0) / n) for l in ALLOWED_LABELS)
    if pe == 1:
        return 1.0 if po == 1 else 0.0
    return (po - pe) / (1 - pe)


def raw_agreement(pairs):
    pairs = [(a, b) for a, b in pairs if a and b]
    if not pairs:
        return None
    return sum(1 for a, b in pairs if a == b) / len(pairs)


def interpret(k):
    if k is None:
        return "N/A"
    if k < 0:
        return "No agreement"
    if k < 0.2:
        return "Slight"
    if k < 0.4:
        return "Fair"
    if k < 0.6:
        return "Moderate"
    if k < 0.8:
        return "Substantial"
    return "Almost perfect"


def decide(k):
    if k is None:
        return "N/A"
    if RANGE_MIN <= k <= RANGE_MAX:
        return "PASS (within 0.6-0.8)"
    if k > RANGE_MAX:
        return "FLAG (> 0.8, check for leakage / too-easy rubric)"
    return "FAIL (< 0.6)"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    args = ap.parse_args()

    gt_path = f"data/{args.mode}_ground_truth.csv"
    llm_path = f"results/{args.mode}_llm_output.csv"
    summary_path = "results/summary.csv"
    plan_path = "results/pilot_analysis_plan.md"

    gt_rows = read_csv(gt_path)
    llm_rows = read_csv(llm_path)
    llm_by_id = {r["issue_id"]: r for r in llm_rows}

    # --- Human-Human pairs per component ---
    hh_pairs = {c: [] for c in COMPONENTS}
    for r in gt_rows:
        hh_pairs["OB"].append((r["annotator_1_ob"], r["annotator_2_ob"]))
        hh_pairs["EB"].append((r["annotator_1_eb"], r["annotator_2_eb"]))
        hh_pairs["S2R"].append((r["annotator_1_s2r"], r["annotator_2_s2r"]))

    hh_overall_pairs = hh_pairs["OB"] + hh_pairs["EB"] + hh_pairs["S2R"]

    # --- LLM vs Developer consensus pairs per component ---
    ld_pairs = {c: [] for c in COMPONENTS}
    n_invalid = 0
    n_valid = 0
    consensus_dist = Counter()
    llm_dist = Counter()

    for r in gt_rows:
        issue_id = r["issue_id"]
        llm_row = llm_by_id.get(issue_id)
        if llm_row is None or llm_row.get("raw_json_status") != "VALID":
            n_invalid += 1
            continue
        n_valid += 1
        pairs = [
            ("OB", r["consensus_ob"], llm_row.get("llm_ob_label", "")),
            ("EB", r["consensus_eb"], llm_row.get("llm_eb_label", "")),
            ("S2R", r["consensus_s2r"], llm_row.get("llm_s2r_label", "")),
        ]
        for comp, cons, llm in pairs:
            ld_pairs[comp].append((cons, llm))
            if cons:
                consensus_dist[cons] += 1
            if llm:
                llm_dist[llm] += 1

    ld_overall_pairs = ld_pairs["OB"] + ld_pairs["EB"] + ld_pairs["S2R"]

    # --- Compute kappas ---
    hh_kappa = {c: cohen_kappa(hh_pairs[c]) for c in COMPONENTS}
    hh_kappa_overall = cohen_kappa(hh_overall_pairs)
    hh_raw = raw_agreement(hh_overall_pairs)

    ld_kappa = {c: cohen_kappa(ld_pairs[c]) for c in COMPONENTS}
    ld_kappa_overall = cohen_kappa(ld_overall_pairs)
    ld_raw = raw_agreement(ld_overall_pairs)

    # --- Print to console ---
    print(f"=== RBL-4 Metrics ({args.mode}) ===")
    print(f"N ground-truth rows: {len(gt_rows)}")
    print(f"N valid (LLM VALID + matched): {n_valid}")
    print(f"N invalid / skipped: {n_invalid}\n")

    print("-- Human-Human Kappa --")
    for c in COMPONENTS:
        k = hh_kappa[c]
        print(f"  {c}: {k:.3f} ({interpret(k)}) -> {decide(k)}" if k is not None else f"  {c}: N/A")
    print(f"  Overall: {hh_kappa_overall:.3f} ({interpret(hh_kappa_overall)}) -> {decide(hh_kappa_overall)}")
    print(f"  Raw agreement: {hh_raw:.3f}\n" if hh_raw is not None else "  Raw agreement: N/A\n")

    print("-- LLM vs Developer Kappa --")
    for c in COMPONENTS:
        k = ld_kappa[c]
        print(f"  {c}: {k:.3f} ({interpret(k)}) -> {decide(k)}" if k is not None else f"  {c}: N/A")
    print(f"  Overall: {ld_kappa_overall:.3f} ({interpret(ld_kappa_overall)}) -> {decide(ld_kappa_overall)}")
    print(f"  Raw agreement: {ld_raw:.3f}\n" if ld_raw is not None else "  Raw agreement: N/A\n")

    print("-- Label distribution (consensus) --")
    for l in ALLOWED_LABELS:
        print(f"  {l}: {consensus_dist.get(l, 0)}")
    print("-- Label distribution (LLM) --")
    for l in ALLOWED_LABELS:
        print(f"  {l}: {llm_dist.get(l, 0)}")

    # --- Write results/summary.csv (matches existing header exactly) ---
    summary_rows = [
        ("ms-hh-kappa-overall", "human_human_kappa_overall", hh_kappa_overall, "", "", n_valid, n_invalid, decide(hh_kappa_overall)),
        ("ms-hh-kappa-ob", "human_human_kappa_ob", hh_kappa["OB"], "", "", n_valid, n_invalid, decide(hh_kappa["OB"])),
        ("ms-hh-kappa-eb", "human_human_kappa_eb", hh_kappa["EB"], "", "", n_valid, n_invalid, decide(hh_kappa["EB"])),
        ("ms-hh-kappa-s2r", "human_human_kappa_s2r", hh_kappa["S2R"], "", "", n_valid, n_invalid, decide(hh_kappa["S2R"])),
        ("ms-hh-raw-agreement", "human_human_raw_agreement", hh_raw, "", "", n_valid, n_invalid, ""),
        ("ms-llm-dev-kappa-overall", "llm_dev_kappa_overall", ld_kappa_overall, "", "", n_valid, n_invalid, decide(ld_kappa_overall)),
        ("ms-llm-dev-kappa-ob", "llm_dev_kappa_ob", ld_kappa["OB"], "", "", n_valid, n_invalid, decide(ld_kappa["OB"])),
        ("ms-llm-dev-kappa-eb", "llm_dev_kappa_eb", ld_kappa["EB"], "", "", n_valid, n_invalid, decide(ld_kappa["EB"])),
        ("ms-llm-dev-kappa-s2r", "llm_dev_kappa_s2r", ld_kappa["S2R"], "", "", n_valid, n_invalid, decide(ld_kappa["S2R"])),
        ("ms-llm-dev-raw-agreement", "llm_dev_raw_agreement", ld_raw, "", "", n_valid, n_invalid, ""),
    ]

    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rq_name", "metric_name", "metric_value", "p_value", "effect_size", "n_valid", "n_invalid", "decision"])
        for rq, metric, value, p, eff, nv, ni, dec in summary_rows:
            val_str = f"{value:.4f}" if isinstance(value, float) else value
            w.writerow([rq, metric, val_str, p, eff, nv, ni, dec])

    # --- Append computed section to pilot_analysis_plan.md ---
    with open(plan_path, "a", encoding="utf-8") as f:
        f.write("\n\n## Computed results (auto-generated by src/compute_metrics.py)\n\n")
        f.write(f"Mode: `{args.mode}` | N valid: {n_valid} | N invalid: {n_invalid}\n\n")
        f.write("### Human-Human Kappa\n\n")
        f.write("| Component | Kappa | Interpretation | Decision |\n|---|---|---|---|\n")
        for c in COMPONENTS:
            k = hh_kappa[c]
            if k is not None:
                f.write(f"| {c} | {k:.3f} | {interpret(k)} | {decide(k)} |\n")
            else:
                f.write(f"| {c} | N/A | N/A | N/A |\n")
        f.write(f"| **Overall** | {hh_kappa_overall:.3f} | {interpret(hh_kappa_overall)} | {decide(hh_kappa_overall)} |\n")
        f.write(f"\nRaw agreement: {hh_raw:.3f}\n\n" if hh_raw is not None else "\nRaw agreement: N/A\n\n")

        f.write("### LLM-vs-Developer Kappa\n\n")
        f.write("| Component | Kappa | Interpretation | Decision |\n|---|---|---|---|\n")
        for c in COMPONENTS:
            k = ld_kappa[c]
            if k is not None:
                f.write(f"| {c} | {k:.3f} | {interpret(k)} | {decide(k)} |\n")
            else:
                f.write(f"| {c} | N/A | N/A | N/A |\n")
        f.write(f"| **Overall** | {ld_kappa_overall:.3f} | {interpret(ld_kappa_overall)} | {decide(ld_kappa_overall)} |\n")
        f.write(f"\nRaw agreement: {ld_raw:.3f}\n\n" if ld_raw is not None else "\nRaw agreement: N/A\n\n")

        f.write("### Label distribution\n\n")
        f.write("| Label | Consensus | LLM |\n|---|---|---|\n")
        for l in ALLOWED_LABELS:
            f.write(f"| {l} | {consensus_dist.get(l, 0)} | {llm_dist.get(l, 0)} |\n")

    print(f"\nWrote {summary_path}")
    print(f"Appended computed results to {plan_path}")


if __name__ == "__main__":
    main()