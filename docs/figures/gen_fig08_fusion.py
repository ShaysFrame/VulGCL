"""Fig 8 (Slide 10) — Gated fusion: three branch vectors → softmax gate → MLP → P(vuln).
Run: python docs/figures/gen_fig08_fusion.py
Output: docs/figures/fig08_fusion.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt, new_canvas, box, title, save
from _figstyle import C_G, C_I, C_L, C_F, BG_G, BG_I, BG_L, BG_F, C_IN
import matplotlib.patches as mpatches
import numpy as np

fig, ax = new_canvas(14, 8.0)
title(ax, 7.0, 7.78,
      "Gated Fusion — a learned softmax gate combines three complementary views", fs=12.5)

# ── LEFT: three branch output vectors ─────────────────────────────────────────
txt(ax, 1.6, 7.38, "Branch Output Vectors", ha="center",
        fontsize=10, fontweight="bold", color=C_IN)
txt(ax, 1.6, 7.08, "each branch → 256-dim embedding",
        ha="center", fontsize=7.5, color="#546E7A")

branch_info = [
    ("h_G", "Graph Branch",  C_G, BG_G, 6.3,
     ["structural", "type+degree"]),
    ("h_I", "Image Branch",  C_I, BG_I, 5.0,
     ["visual", "centrality"]),
    ("h_L", "LLM Branch",    C_L, BG_L, 3.7,
     ["semantic", "code slice"]),
]

for sym, lbl, col, bg, cy, hints in branch_info:
    box(ax, 0.2, cy-0.48, 3.0, 0.95, bg, col, lw=1.8, rad=0.12, zo=4)
    txt(ax, 0.5, cy+0.2, sym, ha="left", va="center",
            fontsize=12, fontweight="bold", color=col)
    txt(ax, 0.5, cy-0.15, lbl, ha="left", va="center", fontsize=8, color=col)
    txt(ax, 2.7, cy+0.1, hints[0], ha="right", va="center", fontsize=7, color=col)
    txt(ax, 2.7, cy-0.2, hints[1], ha="right", va="center", fontsize=7, color="#546E7A")
    txt(ax, 3.38, cy, "∈  ℝ²⁵⁶", ha="left", va="center", fontsize=7.5, color=col)

# convergence arrows from branch vectors to gate box
for cy, col in zip([6.3, 5.0, 3.7], [C_G, C_I, C_L]):
    ax.annotate("", xy=(5.45, 5.0), xytext=(3.62, cy),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5,
                                mutation_scale=11,
                                connectionstyle="arc3,rad=0.0"))

# ── CENTER: softmax gate ──────────────────────────────────────────────────────
txt(ax, 7.0, 7.38, "Learned Softmax Gate", ha="center",
        fontsize=10, fontweight="bold", color=C_F)
txt(ax, 7.0, 7.08, "w = softmax( Linear( concat(h_G, h_I, h_L) ) )",
        ha="center", fontsize=7.5, color="#546E7A")

# gate box
box(ax, 5.5, 4.35, 2.0, 1.28, BG_F, C_F, lw=2.0, rad=0.14, zo=4)
txt(ax, 6.5, 5.2,  "Gate", ha="center", va="center",
        fontsize=10, fontweight="bold", color=C_F)
txt(ax, 6.5, 4.78, "Linear(768→3)\n+ softmax", ha="center", va="center",
        fontsize=7.5, color=C_F)

# gate weights as stacked horizontal bar
bar_y = 3.95
bar_x = 5.5
bar_h = 0.55
total_w = 2.0

weights = [("G", 0.52, C_G), ("I", 0.11, C_I), ("L", 0.37, C_L)]
cx = bar_x
for sym, w, col in weights:
    bw = w * total_w
    box(ax, cx, bar_y - bar_h, bw, bar_h, col, col, lw=0, rad=0.0, zo=5)
    if bw > 0.25:
        txt(ax, cx+bw/2, bar_y-bar_h/2, f"{int(w*100)}%",
                ha="center", va="center", fontsize=8, fontweight="bold", color="white")
    cx += bw

txt(ax, 4.85, bar_y - bar_h/2, "gate →", ha="right", va="center",
        fontsize=7.5, color=C_F, fontweight="bold")
txt(ax, 5.5, bar_y - bar_h - 0.2,  "Graph 52%", ha="left",  fontsize=7, color=C_G)
txt(ax, 6.2, bar_y - bar_h - 0.2,  "LLM 37%",   ha="left",  fontsize=7, color=C_L)
txt(ax, 7.1, bar_y - bar_h - 0.2,  "Img 11%",   ha="right", fontsize=7, color=C_I)

# weighted sum box
ax.annotate("", xy=(8.3, 5.0), xytext=(7.52, 5.0),
            arrowprops=dict(arrowstyle="-|>", color=C_F, lw=1.8, mutation_scale=12))
box(ax, 8.35, 4.35, 2.1, 1.28, BG_F, C_F, lw=2.0, rad=0.14, zo=4)
txt(ax, 9.4, 5.2,  "Weighted", ha="center", va="center",
        fontsize=9.5, fontweight="bold", color=C_F)
txt(ax, 9.4, 4.76, "Σ  w_k · h_k\n→  ℝ²⁵⁶",  ha="center", va="center",
        fontsize=8, color=C_F)

# ── RIGHT: MLP + output ───────────────────────────────────────────────────────
txt(ax, 12.0, 7.38, "MLP Classifier + Output", ha="center",
        fontsize=10, fontweight="bold", color=C_F)

ax.annotate("", xy=(10.85, 5.0), xytext=(10.47, 5.0),
            arrowprops=dict(arrowstyle="-|>", color=C_F, lw=1.8, mutation_scale=12))

# MLP box
box(ax, 10.9, 4.22, 2.3, 1.58, C_F, C_F, lw=0, rad=0.14, zo=4)
txt(ax, 12.05, 5.3,  "MLP",          ha="center", va="center",
        fontsize=11, fontweight="bold", color="white")
txt(ax, 12.05, 4.85, "256 → 128 → 1", ha="center", va="center", fontsize=8, color="white")
txt(ax, 12.05, 4.48, "+ Sigmoid",      ha="center", va="center", fontsize=8, color="white")

# output probability bar
ax.annotate("", xy=(13.4, 5.0), xytext=(13.22, 5.0),
            arrowprops=dict(arrowstyle="-|>", color=C_F, lw=1.8, mutation_scale=12))

txt(ax, 13.65, 5.65, "P(vuln)", ha="center", va="center",
        fontsize=9.5, fontweight="bold", color=C_F)
# background bar
box(ax, 13.2, 4.85, 0.88, 0.3, "#FFCDD2", C_F, lw=1.2, rad=0.04, zo=5)
# filled portion = 0.78
box(ax, 13.2, 4.85, 0.88*0.78, 0.3, C_F, C_F, lw=0, rad=0.04, zo=6)
txt(ax, 13.64, 5.0, "0.78", ha="center", va="center",
        fontsize=8.5, fontweight="bold", color="white", zorder=7)

# threshold decision
box(ax, 13.12, 4.45, 1.06, 0.32, "#FFEBEE", C_F, lw=1.0, rad=0.06, zo=5)
txt(ax, 13.65, 4.61, "0.78 > 0.29\n→ VULNERABLE",
        ha="center", va="center", fontsize=6.5, color=C_F, fontweight="bold")

# ── BOTTOM: auxiliary loss note ───────────────────────────────────────────────
box(ax, 0.15, 0.12, 13.7, 0.65, BG_F, C_F, lw=1.2, rad=0.1, zo=3)
txt(ax, 7.0, 0.45,
    "Auxiliary per-branch losses (weight=0.3) during training force each branch to"
    " remain individually discriminative — prevents the dominant branch from suppressing the others.",
    ha="center", va="center", fontsize=7.5, color=C_F)

save(fig, os.path.join(os.path.dirname(__file__), "fig08_fusion.png"))
