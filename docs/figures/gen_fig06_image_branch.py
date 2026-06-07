"""Fig 6 (Slide 8) — Branch 2: Image (centrality × embedding → CNN).
Run: python docs/figures/gen_fig06_image_branch.py
Output: docs/figures/fig06_image_branch.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import new_canvas, box, arrow, title, save, C_I, BG_I
import numpy as np
import matplotlib.patches as mpatches

fig, ax = new_canvas(12, 4.8)
box(ax, 0.2, 0.3, 11.6, 3.6, BG_I, C_I, lw=1.2, rad=0.18, zo=1)
rng = np.random.default_rng(7)

txt(ax, 1.6, 3.5, "PDG nodes", ha="center", fontsize=9, fontweight="bold",
        color=C_I)
for i, v in enumerate(rng.uniform(0.2, 1.0, 6)):
    box(ax, 0.7 + i * 0.32, 1.7, 0.24, v * 1.1, C_I, C_I, lw=0, rad=0.03, zo=4)
txt(ax, 1.6, 1.4, "3 centrality metrics\n(degree·closeness·katz)", ha="center",
        va="center", fontsize=6.6, color="#37474F")
arrow(ax, 2.7, 2.1, 3.5, 2.1, col=C_I, lw=1.6, ms=10)

txt(ax, 4.7, 3.5, "3-ch image 100×100", ha="center", fontsize=8.5,
        fontweight="bold", color=C_I)
for ch, dx in enumerate([0.0, 0.18, 0.36]):
    ax.imshow(rng.random((10, 10)), extent=[3.7 + dx, 5.3 + dx, 1.2, 2.8],
              cmap="Greens", alpha=0.9, zorder=3 + ch, aspect="auto")
    ax.add_patch(mpatches.Rectangle((3.7 + dx, 1.2), 1.6, 1.6, fill=False,
                                    edgecolor=C_I, lw=1.2, zorder=6))
txt(ax, 4.85, 0.95, "score × CodeBERT embedding", ha="center", va="center",
        fontsize=6.6, color="#37474F")
arrow(ax, 5.9, 2.1, 6.6, 2.1, col=C_I, lw=1.6, ms=10)

for i, dx in enumerate([0.0, 0.22, 0.44]):
    box(ax, 6.7 + dx, 1.5 + i * 0.12, 1.5, 1.2 - i * 0.1, C_I, C_I, lw=0,
        rad=0.06, zo=4 + i)
txt(ax, 7.55, 3.0, "5-layer CNN", ha="center", fontsize=8.5, fontweight="bold",
        color=C_I)
txt(ax, 7.45, 1.25, "Conv·BN·ReLU\n→ AvgPool", ha="center", va="center",
        fontsize=6.6, color="white")
arrow(ax, 8.55, 2.1, 9.9, 2.1, col=C_I, lw=1.6, ms=10)
txt(ax, 10.75, 2.1, "h_I ∈ ℝ²⁵⁶", ha="center", va="center", fontsize=9,
        fontweight="bold", color=C_I,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=C_I,
                  lw=1.4))

title(ax, 6.0, 4.45,
      "Image branch — turns the PDG into a visual signature a CNN can classify",
      fs=11)

save(fig, os.path.join(os.path.dirname(__file__), "fig06_image_branch.png"))
