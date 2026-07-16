# Figures Folder

Save all final plots here.

## Minimum figure requirements

- figure title
- axis labels
- N annotation
- at least 300 DPI

---

## Figure 1 – Cohen's Kappa Distribution by Dimension (Main Metric)

**Filename:** `fig1_kappa_distribution.png`

**Caption:**  
Figure 1. Cohen's Kappa agreement between GPT-4o mini and developer consensus labels across three bug report dimensions: Observed Behavior (OB), Expected Behavior (EB), and Steps to Reproduce (S2R). Results are from the pilot experiment (N = 30). The dashed horizontal line marks the acceptance threshold (κ = 0.60). OB achieved perfect agreement (κ = 1.000); EB reached substantial agreement (κ = 0.695); S2R fell below the threshold (κ = 0.417).

**What to plot:**  
Bar chart with three bars (OB, EB, S2R), y-axis = Kappa value (0 to 1.0), dashed line at κ = 0.60. Annotate each bar with its exact Kappa value. Include N = 30 in the title or as a note.

---

## Figure 2 – LLM vs Human Agreement Comparison (Comparison Plot)

**Filename:** `fig2_llm_vs_human_comparison.png`

**Caption:**  
Figure 2. Comparison of Cohen's Kappa between human-human agreement and LLM-vs-developer agreement across OB, EB, and S2R dimensions (pilot, N = 30). Human-human agreement was perfect across all three dimensions (κ = 1.000). LLM-vs-developer agreement was high for OB (κ = 1.000) and moderate for EB (κ = 0.695), but substantially lower for S2R (κ = 0.417), indicating that GPT-4o mini's interpretation of sufficient reproduction steps diverges from developer judgment.

**What to plot:**  
Grouped bar chart with two bar groups per dimension (Human-Human vs LLM-Developer). Three dimension groups on x-axis (OB, EB, S2R). Y-axis = Kappa (0 to 1.0). Include N = 30 in the title or as a note.
