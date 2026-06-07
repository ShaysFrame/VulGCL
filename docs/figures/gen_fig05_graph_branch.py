"""Fig 5 (Slide 7) — Branch 1: Graph (GAT over the PDG).
Run: python docs/figures/gen_fig05_graph_branch.py
Output: docs/figures/fig05_graph_branch.png

NOTE: edit `node_feature_label` to match the graph-branch design you ship —
structural (type + degree, decorrelated) or CodeBERT node embeddings.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import new_canvas, box, arrow, title, save, C_G, BG_G
import matplotlib.patches as mpatches

node_feature_label = "node features:\ntype + degree (structural)"

fig, ax = new_canvas(12, 4.8)
box(ax, 0.2, 0.3, 11.6, 3.6, BG_G, C_G, lw=1.2, rad=0.18, zo=1)

cx, cy = 1.9, 2.2
pts = [(cx + math.cos(a), cy + math.sin(a)) for a in [0.4, 1.7, 3.0, 4.2, 5.4]]
for a, b in [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4), (0, 4)]:
    arrow(ax, pts[a][0], pts[a][1], pts[b][0], pts[b][1], col=C_G, lw=1.4,
          ms=8, rad=0.15)
for (x, y) in pts:
    ax.add_patch(mpatches.Circle((x, y), 0.26, facecolor="white", edgecolor=C_G,
                                 lw=1.8, zorder=6))
txt(ax, cx, 3.5, "PDG", ha="center", fontsize=9, fontweight="bold", color=C_G)
txt(ax, cx, 0.6, node_feature_label, ha="center", va="center", fontsize=6.8,
        color="#37474F")

steps = [(4.3, "PyG\nGraph", "edge_index +\nnode features"),
         (6.4, "GAT ×2", "4-head attention\nover dependencies"),
         (8.5, "Attention\nPool", "weight nodes\n→ weighted sum")]
prev = 2.95
for x, top, bot in steps:
    box(ax, x - 0.85, 1.5, 1.7, 1.35, C_G, C_G, lw=0, rad=0.12, zo=4)
    txt(ax, x, 2.4, top, ha="center", va="center", fontsize=8.2,
            fontweight="bold", color="white")
    txt(ax, x, 1.85, bot, ha="center", va="center", fontsize=6.4, color="white")
    arrow(ax, prev, 2.2, x - 0.9, 2.2, col=C_G, lw=1.6, ms=10)
    prev = x + 0.9

arrow(ax, prev, 2.2, 10.1, 2.2, col=C_G, lw=1.6, ms=10)
txt(ax, 10.95, 2.2, "h_G ∈ ℝ²⁵⁶", ha="center", va="center", fontsize=9,
        fontweight="bold", color=C_G,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=C_G,
                  lw=1.4))

title(ax, 6.0, 4.45,
      "Graph branch — learns vulnerability patterns from PDG structure", fs=11)

save(fig, os.path.join(os.path.dirname(__file__), "fig05_graph_branch.png"))
