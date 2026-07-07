# RBL-4 – Result Wording
**Author:** Quân (RW)  
**For use in:** final report / paper write-up

---

## Section 1 – Pilot Results

### 1.1 Inter-Annotator Agreement (Pilot)

To validate annotation consistency before running the LLM, two annotators independently labeled all 30 pilot issues across the three dimensions: Observed Behavior (OB), Expected Behavior (EB), and Steps to Reproduce (S2R). Cohen's Kappa was computed for each dimension.

Human-human agreement in the pilot was perfect across all three dimensions (κ = 1.000 for OB, EB, and S2R; raw agreement = 100%), indicating that the rubric was applied consistently and the annotation guidelines were clear and unambiguous.

### 1.2 LLM-vs-Developer Agreement (Pilot)

GPT-4o mini was run on the 30 pilot issues using the finalized prompt (v1.0) at temperature = 0.0. All 30 outputs were parsed successfully (0 INVALID). The LLM labels were then compared against the developer consensus labels using Cohen's Kappa.

Agreement results for the pilot are as follows:

| Dimension | Kappa | Interpretation |
|---|---|---|
| OB | 1.0000 | Perfect agreement |
| EB | 0.6951 | Substantial agreement |
| S2R | 0.4168 | Moderate agreement — below threshold |
| Overall | 0.6183 | Substantial agreement (marginal pass) |
| Raw agreement | 0.8444 | — |

The LLM achieved strong agreement with human annotators on OB and EB, but fell below the acceptance threshold (κ ≥ 0.60) on S2R (κ = 0.4168). This indicates that GPT-4o mini's interpretation of what constitutes sufficient steps to reproduce a bug does not consistently align with developer judgment under the v1.0 prompt. The overall Kappa (0.6183) passed the pilot gate but remained below the proposal threshold of 0.70.

Given that the pipeline ran correctly and the metric was computable, the pilot was considered structurally valid and the team proceeded to the full experiment. The S2R discrepancy was noted and the prompt was revised to address it (see Section 2).

---

## Section 2 – Full Experiment Results

### 2.1 Full Dataset Annotation and IAA

The full dataset comprised 250 issues. A double-labeled subset of 75 issues was used to compute inter-annotator agreement on the full set. Human-human Kappa was 1.000 for all three dimensions (OB, EB, S2R), confirming that annotation quality remained consistent at scale and that the rubric was applied reliably throughout the full labeling process.

### 2.2 Prompt Amendment Note

Between the pilot and the full experiment, the prompt was updated from v1.0 to v3.0-candidate-s2r-relaxed. This change was made in response to the low S2R Kappa observed in the pilot (κ = 0.4168), with the goal of better aligning the LLM's S2R interpretation with the rubric's intent. This amendment must be disclosed in the final report as a deviation from the original pilot configuration.

### 2.3 LLM Output on Full Dataset

GPT-4o mini (temperature = 0.0, prompt v3.0-candidate-s2r-relaxed) was run on all 250 issues. All 250 outputs were parsed successfully (0 INVALID), indicating that the pipeline remained stable at full scale.

---

## Section 3 – Limitations

1. **Prompt change between pilot and full experiment.** The prompt version used in the full experiment (v3.0-candidate-s2r-relaxed) differed from the one used in the pilot (v1.0). While this change was motivated by the observed S2R gap, it means the pilot and full experiment results are not directly comparable under identical conditions. This limits the validity of using the pilot as a calibration baseline for the full run.

2. **S2R Kappa below threshold in pilot.** The LLM-vs-developer Kappa for S2R in the pilot was 0.4168, which falls in the moderate range and is below both the 0.60 pilot gate and the 0.70 proposal threshold. This suggests that the definition of "sufficient" steps to reproduce a bug is difficult for the LLM to apply consistently, even with a structured rubric.

3. **Overall Kappa below proposal threshold.** The overall LLM-vs-developer Kappa in the pilot (0.6183) did not reach the proposed threshold of 0.70. While this passed the minimum pilot gate, it means the model's aggregate labeling performance does not fully meet the quality standard set in the original proposal.

4. **Single model and single prompt evaluated.** This study evaluates only GPT-4o mini at temperature = 0.0. Results may not generalize to other LLMs, other temperatures, or other prompt formulations.

5. **Dataset scope.** Issues were sampled from a small number of OSS repositories. The distribution of OB/EB/S2R quality in those repositories may not represent the broader population of GitHub bug reports.

---

## Section 4 – Discussion Notes

The results show that GPT-4o mini can reliably identify Observed Behavior (OB) components in bug reports (pilot κ = 1.000), and achieves substantial agreement on Expected Behavior (EB, κ = 0.695). This suggests the model has a consistent and accurate understanding of what constitutes a clearly stated observed failure and a well-articulated expectation.

However, the model struggles significantly with Steps to Reproduce (S2R). The pilot Kappa of 0.4168 on S2R indicates only moderate agreement, pointing to a fundamental gap between how the LLM interprets the sufficiency of reproduction steps and how developers judge the same content. This is consistent with prior findings in bug report quality research, where S2R is often the most variable and subjective dimension.

The decision to change the prompt between the pilot and the full experiment was a practical response to this gap, but it introduces a methodological caveat: the experiment is no longer running a single fixed configuration end-to-end. Future work should establish the prompt through a dedicated prompt engineering phase before any data is labeled, to avoid mid-experiment amendments.

The perfect human-human agreement (κ = 1.000) across both pilot and full annotation sets is a strong result for annotation reliability. It confirms that the rubric is well-defined and that the annotators applied it consistently. This removes annotation noise as a confounding factor when interpreting the LLM-vs-developer gap.

Overall, the findings suggest that GPT-4o mini is a viable automated quality gate for OB and EB assessment in GitHub bug reports, but requires further prompt refinement or rubric adjustment before it can be reliably used for S2R evaluation at the proposed quality threshold.
