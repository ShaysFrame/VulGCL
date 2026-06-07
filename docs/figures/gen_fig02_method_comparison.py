"""Fig 2 (Slide 4) — What Current Tools Miss: capability matrix.
Run: python docs/figures/gen_fig02_method_comparison.py
Output: docs/figures/fig02_method_comparison.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import new_canvas, box, title, save, C_F, C_OK, C_BAD, C_IN, BG_F

# ── Editable data ─────────────────────────────────────────────────────────────
cols = ["Method", "Type", "Semantics", "Structure", "Patterns", "Devign F1"]
rows = [
    ("Flawfinder",        "Rule-based",  0, 0, 0, "~0.20"),
    ("LineVul (2022)",    "LLM",         1, 0, 0, "0.651"),
    ("Devign / IVDetect", "GNN",         0, 1, 0, "0.617"),
    ("VulCNN",            "CNN",         0, 0, 1, "~0.58"),
    ("VulGCL (Ours)",     "Multimodal",  1, 1, 1, "≥0.65"),
]

fig, ax = new_canvas(11.5, 5.2)
xcol = [0.6, 3.0, 5.0, 6.6, 8.2, 9.7]
colw = [2.4, 2.0, 1.6, 1.6, 1.5, 1.6]
ytop, rh = 4.35, 0.62

for j, c in enumerate(cols):
    txt(ax, xcol[j] + colw[j] / 2, ytop + 0.30, c, ha="center", va="center",
            fontsize=8.8, fontweight="bold", color=C_IN)

for i, r in enumerate(rows):
    y = ytop - (i + 1) * rh
    is_ours = "Ours" in r[0]
    if is_ours:
        box(ax, xcol[0] - 0.05, y - rh / 2 + 0.04, 11.0 - xcol[0], rh - 0.08,
            BG_F, C_F, lw=1.8, rad=0.08, zo=2)
    txt(ax, xcol[0] + 0.1, y, r[0], ha="left", va="center", fontsize=8.4,
            fontweight="bold" if is_ours else "normal",
            color=C_F if is_ours else "#263238")
    txt(ax, xcol[1] + colw[1] / 2, y, r[1], ha="center", va="center",
            fontsize=8, color="#455A64")
    for k, val in enumerate(r[2:5]):
        cx = xcol[2 + k] + colw[2 + k] / 2
        txt(ax, cx, y, "✓" if val else "✗", ha="center", va="center",
                fontsize=13 if val else 12, fontweight="bold" if val else "normal",
                color=C_OK if val else C_BAD, alpha=1 if val else 0.7)
    txt(ax, xcol[5] + colw[5] / 2, y, r[5], ha="center", va="center",
            fontsize=8.6, fontweight="bold" if is_ours else "normal",
            color=C_F if is_ours else "#263238")

ax.plot([xcol[0] - 0.05, 11.0], [ytop + 0.02, ytop + 0.02], color="#B0BEC5", lw=1)
title(ax, 5.8, 4.95,
      "Every existing tool sees only one dimension — VulGCL sees all three", fs=11)

save(fig, os.path.join(os.path.dirname(__file__), "fig02_method_comparison.png"))
