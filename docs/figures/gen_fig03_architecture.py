"""Fig 3 (Slide 5) — VulGCL overall architecture: PDG → 3 branches → gated fusion.
Run: python docs/figures/gen_fig03_architecture.py
Output: docs/figures/fig03_architecture.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import (new_canvas, box, arrow, title, save,
                       C_IN, C_G, C_I, C_L, C_F, BG_G, BG_I, BG_L, BG_F, BG_N)

fig, ax = new_canvas(13, 6.6)

# ── Left: C function → Joern → PDG ────────────────────────────────────────────
box(ax, 0.25, 4.4, 2.2, 1.7, BG_N, C_IN, lw=1.5)
txt(ax, 1.35, 5.75, "C/C++ function", ha="center", fontsize=8.5,
        fontweight="bold", color=C_IN)
txt(ax, 1.35, 5.05, "memcpy(buf, s, l);", ha="center", va="center",
        fontfamily="monospace", fontsize=7, color="#C62828")
arrow(ax, 1.35, 4.4, 1.35, 4.0, col=C_IN)
box(ax, 0.25, 2.75, 2.2, 1.2, BG_N, C_IN, lw=1.5)
txt(ax, 1.35, 3.55, "Joern", ha="center", fontsize=9, fontweight="bold",
        color=C_IN)
txt(ax, 1.35, 3.15, "PDG extraction", ha="center", fontsize=7, color=C_IN)
arrow(ax, 1.35, 2.75, 1.35, 2.35, col=C_IN)
box(ax, 0.25, 1.5, 2.2, 0.8, "#FAFAFA", C_IN, lw=1.5)
txt(ax, 1.35, 1.9, "PDG", ha="center", va="center", fontsize=10,
        fontweight="bold", color=C_IN)

# ── Three branch rows ─────────────────────────────────────────────────────────
branches = [
    (4.9, 6.05, C_G, BG_G, "Graph branch", "type + degree → GAT ×2 → attention pool", "h_G"),
    (3.05, 4.55, C_I, BG_I, "Image branch", "centrality × embedding → 5-layer CNN", "h_I"),
    (1.2, 2.7, C_L, BG_L, "LLM branch", "top-10 PDG slice → CodeBERT (fine-tuned)", "h_L"),
]
bx0, bx1 = 2.95, 8.7
for y0, y1, ec, bg, name, desc, hsym in branches:
    box(ax, bx0, y0, bx1 - bx0, y1 - y0, bg, ec, lw=1.1, rad=0.16, zo=1)
    cy = (y0 + y1) / 2
    txt(ax, bx0 + 0.12, y1 - 0.28, name, ha="left", va="center", fontsize=8.6,
            fontweight="bold", color=ec)
    box(ax, bx0 + 0.35, cy - 0.42, 5.0, 0.84, ec, ec, lw=0, rad=0.1, zo=4)
    txt(ax, bx0 + 2.85, cy, desc, ha="center", va="center", fontsize=7.6,
            color="white", fontweight="bold")
    # PDG → branch
    arrow(ax, 2.5, 1.9, bx0 + 0.02, cy, col=ec, lw=1.4, ms=9, rad=0.05)
    # branch → h vector
    arrow(ax, bx0 + 5.4, cy, 9.05, cy, col=ec, lw=1.5, ms=10)
    txt(ax, 9.5, cy, f"{hsym}∈ℝ²⁵⁶", ha="center", va="center", fontsize=8,
            fontweight="bold", color=ec,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor=ec, lw=1.2))

# ── Gated fusion ──────────────────────────────────────────────────────────────
gx, gy, gw, gh = 10.2, 2.4, 1.35, 3.3
box(ax, gx, gy, gw, gh, BG_F, C_F, lw=2.0, rad=0.16, zo=5)
txt(ax, gx + gw / 2, gy + gh - 0.32, "Gated", ha="center", va="center",
        fontsize=9, fontweight="bold", color=C_F)
txt(ax, gx + gw / 2, gy + gh - 0.72, "fusion", ha="center", va="center",
        fontsize=9, fontweight="bold", color=C_F)
txt(ax, gx + gw / 2, gy + gh / 2 - 0.1, "softmax\ngate\nweights\n3 views",
        ha="center", va="center", fontsize=7, color=C_F, linespacing=1.5)
for _, _, ec, _, _, _, _ in branches:
    cy = None
for y0, y1, ec, *_ in branches:
    cy = (y0 + y1) / 2
    arrow(ax, 9.95, cy, gx + 0.02, gy + gh / 2, col=ec, lw=1.2, ms=8, rad=0.04)

# ── MLP + output ──────────────────────────────────────────────────────────────
mx, my, mw, mh = 11.85, 3.3, 0.95, 1.5
box(ax, mx, my, mw, mh, C_F, C_F, lw=1.6, rad=0.14, zo=5)
txt(ax, mx + mw / 2, my + mh / 2 + 0.18, "MLP", ha="center", va="center",
        fontsize=9, fontweight="bold", color="white")
txt(ax, mx + mw / 2, my + mh / 2 - 0.25, "→ P(vuln)", ha="center", va="center",
        fontsize=6.5, color="white")
arrow(ax, gx + gw, gy + gh / 2, mx - 0.02, my + mh / 2, col=C_F, lw=2.0, ms=12)

txt(ax, mx + mw / 2, my - 0.35, "Vulnerable", ha="center", va="center",
        fontsize=8.5, fontweight="bold", color="#C62828")
txt(ax, mx + mw / 2, my - 0.7, "/ Safe", ha="center", va="center",
        fontsize=8.5, fontweight="bold", color="#1B5E20")

title(ax, 6.5, 6.45,
      "VulGCL — three independent views of one PDG, gated into one decision",
      fs=11.5)

save(fig, os.path.join(os.path.dirname(__file__), "fig03_architecture.png"))
