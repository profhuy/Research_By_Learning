# RBL-4 – Project Notes
**Maintained by:** Quân (RW)  
**Last updated:** 2026-07-07

---

## 1. Project Overview

- **Research topic:** Using GPT-4o mini as a quality gate to evaluate bug reports on GitHub OSS projects
- **Evaluation scope:** OB (Observed Behavior) / EB (Expected Behavior) / S2R (Steps to Reproduce)
- **Main metric:** Cohen's Kappa
- **Pass threshold:** Kappa ≥ 0.70 (per proposal); overall pass threshold ≥ 0.60 used in pilot review
- **Model used:** GPT-4o mini, temperature = 0.0

---

## 2. Team Roles

| Name | Role | Responsibility |
|---|---|---|
| Huy | PL – Project Lead | Repo setup, gate checks, final review |
| Hùng | DG – Data & Ground Truth | Pilot sample, full dataset, annotation, IAA |
| Phúc | LR – LLM Runner | API pipeline, pilot run, full run |
| Thêm | MS – Metrics & Statistics | Kappa computation, summary.csv |
| Quân | RW – Report Writer | notes.md, wording, captions, discussion |

---

## 3. Timeline & Deadlines

| Milestone | Target |
|---|---|
| Pilot run completed | Week 7 |
| Full experiment completed | Week 8 |
| notes.md + wording submitted to Huy | 2026-07-07 (today) |

---

## 4. Pilot – Key Decisions & Events

- **Pilot sample size:** N = 30 issues
- **Prompt version used:** v1.0 (`prompt_final.md`)
- **Model:** GPT-4o mini, temperature = 0.0
- **Pilot outcome:** Pipeline ran without errors; all 30 outputs parsed as VALID; metric computation successful → **Pilot PASSED**, proceed to full experiment.

### Pilot IAA (Human-Human)

| Dimension | Kappa | Decision |
|---|---|---|
| OB | 1.0000 | PASS |
| EB | 1.0000 | PASS |
| S2R | 1.0000 | PASS |
| Overall | 1.0000 | PASS |
| Raw agreement | 1.0000 | — |

### Pilot LLM-vs-Developer Agreement

| Dimension | Kappa | Decision |
|---|---|---|
| OB | 1.0000 | PASS |
| EB | 0.6951 | PASS |
| S2R | 0.4168 | **FAIL** |
| Overall | 0.6183 | PASS (marginal) |
| Raw agreement | 0.8444 | — |

### Pilot Notes

- S2R Kappa (0.4168) fell below the 0.60 threshold. This was flagged and reported to Huy before proceeding to the full experiment.
- Overall Kappa (0.6183) passed the ≥ 0.60 pilot gate but is below the proposal threshold of 0.70.
- No invalid outputs (0/30 INVALID).

---

## 5. Full Experiment – Key Decisions & Events

- **Full dataset size:** N = 250 issues
- **Prompt version used:** v3.0-candidate-s2r-relaxed ⚠️ (changed from v1.0 used in pilot — see note below)
- **Model:** GPT-4o mini, temperature = 0.0
- **INVALID outputs:** 0 / 250

### ⚠️ Prompt Version Change (Important)

The full experiment was run using `prompt_v3_candidate.md` (`v3.0-candidate-s2r-relaxed`) instead of `prompt_final.md` (`v1.0`) used in the pilot. This change was made to address the low S2R Kappa observed in the pilot. This constitutes a deviation from the original pilot configuration and must be reported as an amendment in the final write-up.

### Full Experiment IAA (Human-Human, double-labeled subset)

| Dimension | Double-labeled N | Kappa | Decision |
|---|---|---|---|
| OB | 75 | 1.0000 | PASS |
| EB | 75 | 1.0000 | PASS |
| S2R | 75 | 1.0000 | PASS |

---

## 6. Open Issues / Flags for Huy

- [ ] S2R Kappa in pilot (0.4168) is below threshold — needs to be discussed in limitations/discussion section.
- [ ] Prompt was changed from v1.0 to v3.0-candidate-s2r-relaxed between pilot and full run — amendment note may be needed.
- [ ] Overall LLM-Dev Kappa (0.6183) is below the proposal threshold of 0.70 — needs to be honestly reported.
