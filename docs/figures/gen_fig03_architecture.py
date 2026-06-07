"""Fig 03 (Slide 5) — VulGCL overall architecture: three branches → gated fusion → MLP.
Run: python docs/figures/gen_fig03_architecture.py
Output: docs/figures/fig03_architecture.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt, new_canvas, box, arrow, title, save
from _figstyle import C_IN, C_G, C_I, C_L, C_F, BG_N, BG_G, BG_I, BG_L, BG_F

fig, ax = new_canvas(13, 6.2)

# ── Input: C/C++ function → Joern PDG ────────────────────────────────────────
box(ax, 3.4, 5.18, 6.2, 0.68, BG_N, C_IN, lw=1.8, rad=0.14, zo=4)
txt(ax, 6.5, 5.52, "Input: C/C++ function  →  Joern PDG",
        ha="center", va="center", fontsize=10.5, fontweight="bold", color=C_IN)

# fan-out arrows: PDG → three branches
for cx in [2.05, 6.5, 10.95]:
    arrow(ax, 6.5, 5.18, cx, 4.67, col="#90A4AE", lw=1.4, ms=9)

# ── Three branch cards ────────────────────────────────────────────────────────
cards = [
    (0.3,  2.05,  C_G, BG_G, "Graph Branch",
     "structural features", "type bucket + degree",
     "GAT × 2  +  attn pool"),
    (4.75, 6.5,   C_I, BG_I, "Image Branch",
     "3-channel 100×100 img", "centrality × CodeBERT",
     "3-layer CNN  +  AvgPool"),
    (9.2,  10.95, C_L, BG_L, "LLM Branch",
     "PDG betweenness slice", "focused ≤512 tokens",
     "CodeBERT  +  proj 768→256"),
]

for bx, cx, col, bg, header, sub1, sub2, sub3 in cards:
    # card background (extra height to avoid text/pill overlap)
    box(ax, bx, 2.3, 3.5, 2.35, bg, col, lw=1.8, rad=0.14, zo=3)
    # solid colored header
    box(ax, bx, 4.18, 3.5, 0.47, col, col, lw=0, rad=0.1, zo=4)
    txt(ax, cx, 4.415, header, ha="center", va="center",
            fontsize=9.5, fontweight="bold", color="white")
    # three content lines (spread across card body)
    txt(ax, cx, 3.82, sub1, ha="center", va="center", fontsize=8.2, color=col)
    txt(ax, cx, 3.38, sub2, ha="center", va="center", fontsize=7.8, color="#546E7A")
    txt(ax, cx, 2.98, sub3, ha="center", va="center", fontsize=7.8, color="#546E7A")
    # output-dimension pill — clear gap below sub3
    box(ax, cx - 1.1, 2.37, 2.2, 0.36, "white", col, lw=1.2, rad=0.08, zo=5)
    outname = {"Graph Branch": "h_G", "Image Branch": "h_I", "LLM Branch": "h_L"}[header]
    txt(ax, cx, 2.55, f"{outname}  ∈  ℝ²⁵⁶",
            ha="center", va="center", fontsize=8, fontweight="bold", color=col)

# fan-in arrows: branch bottoms → fusion (colored to match each branch)
branch_cols = [C_G, C_I, C_L]
for cx, col in zip([2.05, 6.5, 10.95], branch_cols):
    arrow(ax, cx, 2.3, 6.5, 2.05, col=col, lw=1.4, ms=9)

# ── Gated Fusion box ─────────────────────────────────────────────────────────
box(ax, 3.4, 1.2, 6.2, 0.84, BG_F, C_F, lw=2.2, rad=0.14, zo=4)
txt(ax, 6.5, 1.83, "Gated Fusion", ha="center", va="center",
        fontsize=10.5, fontweight="bold", color=C_F)
txt(ax, 6.5, 1.42, "learned softmax gate  ·  weighted sum  →  ℝ²⁵⁶",
        ha="center", va="center", fontsize=8, color=C_F)

arrow(ax, 6.5, 1.2, 6.5, 0.8, col=C_F, lw=2.0, ms=11)

# ── MLP + output ─────────────────────────────────────────────────────────────
box(ax, 4.2, 0.18, 4.6, 0.58, C_F, C_F, lw=0, rad=0.1, zo=4)
txt(ax, 6.5, 0.47, "MLP   256 → 128 → 1   →   P(vulnerable)",
        ha="center", va="center", fontsize=9, fontweight="bold", color="white")

title(ax, 6.5, 6.0,
      "VulGCL — three complementary views fused with a learned gate",
      fs=12)

save(fig, os.path.join(os.path.dirname(__file__), "fig03_architecture.png"))
