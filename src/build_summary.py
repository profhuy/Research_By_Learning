"""
build_summary.py - Sinh results/summary.csv cho pilot hoac full experiment.

Chay:
    python src/build_summary.py --mode full
    python src/build_summary.py --mode pilot

Nguyen tac:
- Khong bia so. Neu thieu data thi bao loi va dung.
- Threshold lay tu proposal (0.70), KHONG hardcode 0.60.
"""

import argparse
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

COMPONENTS = ["ob", "eb", "s2r"]
VALID_LABELS = {"Sufficient", "Ambiguous", "Missing", "Incorrect"}

# Threshold dang ky trong proposal RBL-3. Doi so nay = phai co amendment note.
KAPPA_THRESHOLD = 0.70
N_BOOTSTRAP = 5000
RANDOM_SEED = 42


def loadPairedData(mode):
    """Ghep LLM output voi developer consensus theo (repo, issue_id).

    Merge inner: chi giu issue co ca 2 phia. Issue nao LLM tra INVALID
    hoac thieu nhan se bi loai va dem vao n_invalid.
    """
    llm = pd.read_csv(f"results/{mode}_llm_output.csv")
    gt = pd.read_csv(f"data/{mode}_ground_truth.csv")

    llm = llm.dropna(subset=["repo", "issue_id"])
    gt = gt.dropna(subset=["repo", "issue_id"])
    if llm.empty or gt.empty:
        sys.exit(f"[STOP] File {mode} van con rong. Chua chay duoc summary.")

    merged = llm.merge(gt, on=["repo", "issue_id"], suffixes=("_llm", "_gt"))

    llmCols = [f"llm_{c}_label" for c in COMPONENTS]
    devCols = [f"consensus_{c}" for c in COMPONENTS]

    # Mot issue chi valid khi ca 6 nhan deu thuoc rubric.
    isValid = merged[llmCols + devCols].isin(VALID_LABELS).all(axis=1)
    nInvalid = int((~isValid).sum())
    return merged[isValid].reset_index(drop=True), nInvalid


def bootstrapKappaCi(devMatrix, llmMatrix, pooled):
    """Cluster bootstrap: resample theo ISSUE, khong resample theo tung nhan.

    Ly do: 3 nhan OB/EB/S2R cua cung 1 issue tuong quan voi nhau. Neu
    resample tung nhan roi le thi CI se hep gia tao (underestimate variance).
    """
    rng = np.random.default_rng(RANDOM_SEED)
    nIssues = devMatrix.shape[0]
    draws = []

    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, nIssues, nIssues)
        dev = devMatrix[idx]
        llm = llmMatrix[idx]
        if pooled:
            dev, llm = dev.ravel(), llm.ravel()
        else:
            dev, llm = dev[:, 0], llm[:, 0]
        # Resample co the sinh mau chi 1 nhan duy nhat -> kappa undefined.
        if len(set(dev)) < 2 and len(set(llm)) < 2:
            continue
        draws.append(cohen_kappa_score(dev, llm))

    if not draws:
        return np.nan, np.nan
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def kappaSafe(a, b):
    """Tra NaN thay vi 0.0 khi kappa undefined (ca 2 phia chi co 1 nhan).

    sklearn tra 0.0 trong truong hop nay - rat de bi doc nham la
    'khong dong thuan', trong khi thuc te la 'khong tinh duoc'.
    """
    if len(set(a)) < 2 and len(set(b)) < 2:
        return np.nan
    return float(cohen_kappa_score(a, b))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pilot", "full"], required=True)
    args = parser.parse_args()

    df, nInvalid = loadPairedData(args.mode)
    nIssues = len(df)

    devMatrix = df[[f"consensus_{c}" for c in COMPONENTS]].to_numpy()
    llmMatrix = df[[f"llm_{c}_label" for c in COMPONENTS]].to_numpy()

    rows = []

    # --- RQ1: overall kappa tren 90 cap (pooled) ---
    devFlat, llmFlat = devMatrix.ravel(), llmMatrix.ravel()
    kOverall = kappaSafe(devFlat, llmFlat)
    ciLo, ciHi = bootstrapKappaCi(devMatrix, llmMatrix, pooled=True)

    # Test 1 phia H0: kappa >= 0.70. Bac bo neu can tren CI < threshold.
    decision = "REJECT H0 (khong dat 0.70)" if ciHi < KAPPA_THRESHOLD \
        else "FAIL TO REJECT H0 (chua ket luan duoc)"

    rows.append({
        "rq_name": "RQ1",
        "metric_name": f"LLM-vs-Dev Overall Kappa (pooled, 95% CI [{ciLo:.3f}, {ciHi:.3f}])",
        "metric_value": round(kOverall, 3),
        "p_value": "bootstrap CI - xem cot metric_name",
        "effect_size": round(kOverall, 3),  # Kappa CHINH LA effect size
        "n_valid": nIssues * 3,
        "n_invalid": nInvalid * 3,
        "decision": decision,
    })

    rawAgreement = float((devFlat == llmFlat).mean())
    rows.append({
        "rq_name": "RQ1",
        "metric_name": "Raw agreement (LLM vs Dev)",
        "metric_value": round(rawAgreement, 3),
        "p_value": "n/a - thong ke mo ta",
        "effect_size": "n/a",
        "n_valid": nIssues * 3,
        "n_invalid": nInvalid * 3,
        "decision": "descriptive",
    })

    # --- RQ2: kappa tung component ---
    for i, comp in enumerate(COMPONENTS):
        k = kappaSafe(devMatrix[:, i], llmMatrix[:, i])
        lo, hi = bootstrapKappaCi(devMatrix[:, [i]], llmMatrix[:, [i]], pooled=False)
        rows.append({
            "rq_name": "RQ2",
            "metric_name": f"LLM-vs-Dev Kappa {comp.upper()} (95% CI [{lo:.3f}, {hi:.3f}])",
            "metric_value": round(k, 3) if not np.isnan(k) else "UNDEFINED",
            "p_value": "bootstrap CI - xem cot metric_name",
            "effect_size": round(k, 3) if not np.isnan(k) else "UNDEFINED",
            "n_valid": nIssues,
            "n_invalid": nInvalid,
            "decision": landisKoch(k),
        })

    # --- QC: human-human IAA tren phan double-labeled ---
    dl = df[df["double_labeled"].astype(str).str.lower().isin(["true", "yes", "1"])]
    for comp in COMPONENTS:
        if dl.empty:
            k, note = np.nan, "KHONG CO DONG DOUBLE-LABELED"
        else:
            k = kappaSafe(dl[f"annotator_1_{comp}"], dl[f"annotator_2_{comp}"])
            note = "FLAG - kiem tra contamination" if k == 1.0 else landisKoch(k)
        rows.append({
            "rq_name": "QC",
            "metric_name": f"Human-Human Kappa {comp.upper()}",
            "metric_value": round(k, 3) if not np.isnan(k) else "UNDEFINED",
            "p_value": "n/a",
            "effect_size": round(k, 3) if not np.isnan(k) else "UNDEFINED",
            "n_valid": len(dl),
            "n_invalid": 0,
            "decision": note,
        })

    # --- QC: ty le invalid, gate 20% trong pilot_analysis_plan.md ---
    totalIssues = nIssues + nInvalid
    invalidRate = nInvalid / totalIssues if totalIssues else 0.0
    rows.append({
        "rq_name": "QC",
        "metric_name": "Invalid output rate",
        "metric_value": round(invalidRate, 3),
        "p_value": "n/a",
        "effect_size": "n/a",
        "n_valid": nIssues,
        "n_invalid": nInvalid,
        "decision": "FLAG - vuot 20%" if invalidRate > 0.20 else "OK",
    })

    out = pd.DataFrame(rows)
    out.to_csv("results/summary.csv", index=False)
    print(out.to_string(index=False))
    print(f"\nDa ghi results/summary.csv ({len(out)} dong).")


def landisKoch(k):
    """Thang dien giai Landis & Koch (1977)."""
    if np.isnan(k):
        return "undefined"
    if k < 0.00:
        return "poor"
    if k < 0.21:
        return "slight"
    if k < 0.41:
        return "fair"
    if k < 0.61:
        return "moderate"
    if k < 0.81:
        return "substantial"
    return "almost perfect"


if __name__ == "__main__":
    main()
