"""Fig 8 (Slide 10) — Gated fusion of the three branch vectors → MLP → P(vuln).
Run: python docs/figures/gen_fig08_fusion.py
Output: docs/figures/fig08_fusion.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import (new_canvas, box, arrow, title, save,
                       C_G, C_I, C_L, C_F, BG_F)

fig, ax = new_canvas(12, 5.2)

# three branch vectors with learned gate weights
vecs = [(4.1, C_G, "h_G", "0.52"), (3.0, C_I, "h_I", "0.11"),
        (1.9, C_L, "h_L", "0.37")]
for y, c, sym, w in vecs:
    box(ax, 0.6, y - 0.32, 1.5, 0.64, c, c, lw=0, rad=0.1, zo=4)
    txt(ax, 1.35, y, f"{sym} ∈ ℝ²⁵⁶", ha="center", va="center", fontsize=8,
            fontweight="bold", color="white")
    txt(ax, 2.35, y, f"gate\n{w}", ha="center", va="center", fontsize=7,
            fontweight="bold", color=c)
    arrow(ax, 2.75, y, 3.95, 3.0, col=c, lw=1.6, ms=10, rad=0.04)

# gate box
box(ax, 2.2, 0.65, 0.95, 0.55, "white", C_F, lw=1.3, rad=0.08, zo=5)
txt(ax, 2.67, 0.92, "softmax\ngate", ha="center", va="center", fontsize=6.4,
        color=C_F, fontweight="bold")

# fusion
box(ax, 4.0, 2.2, 1.7, 1.6, BG_F, C_F, lw=2.0, rad=0.14, zo=5)
txt(ax, 4.85, 3.45, "Gated", ha="center", va="center", fontsize=9.5,
        fontweight="bold", color=C_F)
txt(ax, 4.85, 3.05, "weighted Σ", ha="center", va="center", fontsize=8,
        color=C_F)
txt(ax, 4.85, 2.6, "→ ℝ²⁵⁶", ha="center", va="center", fontsize=8, color=C_F)
arrow(ax, 5.7, 3.0, 6.7, 3.0, col=C_F, lw=2.0, ms=13)

# MLP
box(ax, 6.8, 2.25, 1.9, 1.5, C_F, C_F, lw=1.6, rad=0.14, zo=5)
txt(ax, 7.75, 3.2, "MLP", ha="center", va="center", fontsize=10,
        fontweight="bold", color="white")
txt(ax, 7.75, 2.75, "256 → 128 → 1\n+ Sigmoid", ha="center", va="center",
        fontsize=7, color="white")
arrow(ax, 8.7, 3.0, 9.6, 3.0, col=C_F, lw=2.0, ms=13)

# output bar
txt(ax, 10.6, 3.0, "P(vulnerable)", ha="center", va="center", fontsize=9,
        fontweight="bold", color=C_F)
box(ax, 9.8, 2.3, 1.6, 0.4, "#FFCDD2", C_F, lw=1.2, rad=0.05, zo=4)
box(ax, 9.8, 2.3, 1.6 * 0.78, 0.4, C_F, C_F, lw=0, rad=0.05, zo=5)
txt(ax, 10.6, 2.5, "0.78", ha="center", va="center", fontsize=7.5,
        fontweight="bold", color="white", zorder=6)

# aux losses note
txt(ax, 6.0, 1.4, "+ auxiliary per-branch losses (deep supervision) keep every "
        "branch individually discriminative", ha="center", va="center",
        fontsize=7.6, color="#546E7A", style="italic")

title(ax, 6.0, 4.85,
      "Fusion — a learned gate weights the three views, not a blind concat",
      fs=11.5)

save(fig, os.path.join(os.path.dirname(__file__), "fig08_fusion.png"))
