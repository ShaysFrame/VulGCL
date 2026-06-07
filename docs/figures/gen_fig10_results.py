"""Fig 10 (Slide 12) — Results: F1 and AUC per model on the Devign test set.
Run: python docs/figures/gen_fig10_results.py
Output: docs/figures/fig10_results.png

EDIT the `results` dict below with the final numbers from
/mnt/data/experiments/results.json after the full run, then re-run this script.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import new_canvas, box, title, save, C_G, C_I, C_L, C_F
import numpy as np

# ── Editable results (model -> (F1, AUC)) — update after final run ────────────
results = {
    "Graph only": (0.6298, 0.5729, C_G),
    "Image only": (0.6253, 0.5723, C_I),
    "LLM only":   (0.6631, 0.6586, C_L),
    "VulGCL":     (0.6533, 0.6693, C_F),
}

fig, ax = new_canvas(11, 5.6)
names = list(results)
n = len(names)
xs = np.linspace(1.2, 9.0, n)
bw = 0.55
ybase, yscale = 1.0, 5.0   # y per 1.0 metric

for x, name in zip(xs, names):
    f1, auc, col = results[name]
    # F1 bar (solid) + AUC bar (hatched) side by side
    box(ax, x - bw, ybase, bw * 0.9, f1 * (yscale - ybase), col, col, lw=0,
        rad=0.04, zo=4)
    txt(ax, x - bw + bw * 0.45, ybase + f1 * (yscale - ybase) + 0.12,
            f"{f1:.3f}", ha="center", va="bottom", fontsize=7.6,
            fontweight="bold", color=col)
    ax.add_patch(__import__("matplotlib").patches.Rectangle(
        (x + 0.05, ybase), bw * 0.9, auc * (yscale - ybase), facecolor="none",
        edgecolor=col, lw=1.6, hatch="///", zorder=4))
    txt(ax, x + 0.05 + bw * 0.45, ybase + auc * (yscale - ybase) + 0.12,
            f"{auc:.3f}", ha="center", va="bottom", fontsize=7.6, color=col)
    txt(ax, x, ybase - 0.22, name, ha="center", va="top", fontsize=8.2,
            fontweight="bold" if name == "VulGCL" else "normal",
            color=col)

# legend
box(ax, 7.6, 4.4, 0.3, 0.3, C_G, C_G, lw=0, zo=5)
txt(ax, 8.0, 4.55, "F1 (solid)", ha="left", va="center", fontsize=8, color="#333")
ax.add_patch(__import__("matplotlib").patches.Rectangle(
    (7.6, 3.95), 0.3, 0.3, facecolor="none", edgecolor="#333", lw=1.5,
    hatch="///", zorder=5))
txt(ax, 8.0, 4.1, "AUC (hatched)", ha="left", va="center", fontsize=8,
        color="#333")

ax.plot([0.5, 9.6], [ybase, ybase], color="#B0BEC5", lw=1)
title(ax, 5.5, 5.35, "Results on the Devign test set — F1 and AUC by model",
      fs=11.5)

save(fig, os.path.join(os.path.dirname(__file__), "fig10_results.png"))
