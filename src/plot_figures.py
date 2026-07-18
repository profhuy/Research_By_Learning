"""
plot_figures.py - Ve figure cho paper (Them - MS)

Chay tu REPO ROOT:
    python src/plot_figures.py

Output:
    figures/fig_kappa_by_component.pdf  - Bar chart RQ2
    figures/fig_pipeline.pdf            - Flowchart pipeline
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

os.makedirs("figures", exist_ok=True)

# ─────────────────────────────────────────────
# Figure 1: Bar chart Kappa by component (RQ2)
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4.5))

components = ["OB", "EB", "S2R"]
kappa_vals = [None, 0.653, 0.400]   # OB undefined -> hien thi khac
ci_lo      = [None, 0.371, 0.148]
ci_hi      = [None, 0.902, 0.672]

colors = ["#b0c4de", "#4a90d9", "#e05c5c"]
x = np.arange(len(components))

for i, (comp, k, lo, hi, col) in enumerate(
        zip(components, kappa_vals, ci_lo, ci_hi, colors)):
    if k is None:
        # OB undefined - ve bar xam nhat voi chu UNDEFINED
        ax.bar(i, 0.05, color="#cccccc", edgecolor="#999", linewidth=0.8,
               zorder=3)
        ax.text(i, 0.08, "UNDEFINED\n(OB toàn\nSufficient)",
                ha="center", va="bottom", fontsize=7.5, color="#666",
                linespacing=1.4)
    else:
        ax.bar(i, k, color=col, edgecolor="white", linewidth=0.8, zorder=3)
        # CI error bar
        ax.errorbar(i, k, yerr=[[k - lo], [hi - k]],
                    fmt="none", color="#333", capsize=5, linewidth=1.2,
                    zorder=4)
        ax.text(i, k + (hi - k) + 0.04, f"κ = {k:.3f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

# Duong nguong 0.70
ax.axhline(0.70, color="#e05c5c", linestyle="--", linewidth=1.2,
           label="Ngưỡng đăng ký κ = 0.70", zorder=2)

# Vung Landis & Koch
ax.axhspan(0.60, 0.80, alpha=0.06, color="green",
           label="Vùng chấp nhận (0.60–0.80)")

ax.set_xticks(x)
ax.set_xticklabels(components, fontsize=11)
ax.set_ylabel("Cohen's Kappa (κ)", fontsize=10)
ax.set_ylim(0, 1.15)
ax.set_title("Kappa LLM-vs-Developer theo từng component (pilot, N=30)",
             fontsize=10, pad=10)
ax.legend(fontsize=8, loc="upper right")
ax.grid(axis="y", alpha=0.3, zorder=1)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig("figures/fig_kappa_by_component.pdf", bbox_inches="tight",
            dpi=150)
plt.savefig("figures/fig_kappa_by_component.png", bbox_inches="tight",
            dpi=150)
print("Saved: figures/fig_kappa_by_component.pdf")
plt.close()


# ─────────────────────────────────────────────
# Figure 2: Flowchart pipeline OB/EB/S2R -> Kappa
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis("off")


def box(ax, x, y, w, h, text, color="#dce8f7", fontsize=8.5,
        textcolor="#1a1a2e", radius=0.18):
    fancy = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle=f"round,pad=0.05,rounding_size={radius}",
                           facecolor=color, edgecolor="#7a9cbf",
                           linewidth=1.1, zorder=3)
    ax.add_patch(fancy)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=textcolor, zorder=4, multialignment="center",
            linespacing=1.4)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#4a6fa5",
                                lw=1.2, mutation_scale=12),
                zorder=2)


# Row 1: Input
box(ax, 5, 6.3, 5.5, 0.7,
    "30 GitHub bug reports\n(pandas, scikit-learn, VS Code)",
    color="#e8f0fb", fontsize=9)

# Row 2: 3 components
for i, (xi, comp, desc) in enumerate([
        (2.0, "OB", "Observed\nBehavior"),
        (5.0, "EB", "Expected\nBehavior"),
        (8.0, "S2R", "Steps to\nReproduce")]):
    box(ax, xi, 5.0, 2.2, 0.75, f"{comp}\n{desc}", color="#c8dff7")
    arrow(ax, 5, 5.95, xi, 5.38)

# Row 3: label pairs
for i, (xi, comp) in enumerate([(2.0, "OB"), (5.0, "EB"), (8.0, "S2R")]):
    box(ax, xi, 3.7, 2.4, 0.85,
        f"Cặp nhãn {comp}\n(Dev consensus, LLM)\nn = 30",
        color="#dce8f7", fontsize=7.5)
    arrow(ax, xi, 4.62, xi, 4.08)

# Row 4: 2 branches
# Nhanh trai: per-component kappa (RQ2)
box(ax, 2.0, 2.45, 2.6, 0.75,
    "Kappa từng component\n(RQ2: mạnh/yếu ở đâu?)",
    color="#fff3cd", fontsize=7.5, textcolor="#7d5a00")
arrow(ax, 2.0, 3.28, 2.0, 2.83)
arrow(ax, 5.0, 3.28, 2.0, 2.83)
arrow(ax, 8.0, 3.28, 2.0, 2.83)

# Nhanh phai: pool -> overall kappa (RQ1)
box(ax, 7.5, 2.45, 2.8, 0.75,
    "Pool 90 cặp nhãn\n→ Overall Kappa (RQ1)",
    color="#d4edda", fontsize=7.5, textcolor="#155724")
arrow(ax, 2.0, 3.28, 7.5, 2.83)
arrow(ax, 5.0, 3.28, 7.5, 2.83)
arrow(ax, 8.0, 3.28, 7.5, 2.83)

# Row 5: results
box(ax, 2.0, 1.25, 3.0, 0.9,
    "κ OB = UNDEFINED\nκ EB = 0.653\nκ S2R = 0.400",
    color="#fff8e1", fontsize=7.5)
arrow(ax, 2.0, 2.08, 2.0, 1.70)

box(ax, 7.5, 1.25, 3.0, 0.9,
    "κ Overall = 0.582\n95% CI [0.387, 0.740]\nNgưỡng: 0.70",
    color="#e8f5e9", fontsize=7.5)
arrow(ax, 7.5, 2.08, 7.5, 1.70)

# Row 6: conclusion
box(ax, 2.0, 0.35, 3.0, 0.65,
    "RQ2: S2R yếu nhất\n(Fair, κ = 0.400)",
    color="#ffe0b2", fontsize=7.5, textcolor="#7d3c00")
arrow(ax, 2.0, 0.80, 2.0, 0.68)

box(ax, 7.5, 0.35, 3.2, 0.65,
    "RQ1: Chưa kết luận\n(CI chứa 0.70, N=30 nhỏ)",
    color="#fce4ec", fontsize=7.5, textcolor="#7b0028")
arrow(ax, 7.5, 0.80, 7.5, 0.68)

# Label 2 nhanh
ax.text(2.0, 3.05, "Nhánh RQ2", ha="center", fontsize=7,
        color="#7d5a00", style="italic")
ax.text(7.5, 3.05, "Nhánh RQ1", ha="center", fontsize=7,
        color="#155724", style="italic")

ax.set_title(
    "Pipeline: OB / EB / S2R → Cohen's Kappa (pilot, N=30 issues)",
    fontsize=10, pad=6)

plt.tight_layout()
plt.savefig("figures/fig_pipeline.pdf", bbox_inches="tight", dpi=150)
plt.savefig("figures/fig_pipeline.png", bbox_inches="tight", dpi=150)
print("Saved: figures/fig_pipeline.pdf")
plt.close()

print("\nDone. 2 figures saved to figures/")
