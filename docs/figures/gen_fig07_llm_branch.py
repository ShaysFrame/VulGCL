"""Fig 7 (Slide 9) — Branch 3: LLM (PDG-guided slice → CodeBERT).
Run: python docs/figures/gen_fig07_llm_branch.py
Output: docs/figures/fig07_llm_branch.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import new_canvas, box, arrow, title, save, C_L, C_BAD, BG_L

fig, ax = new_canvas(12, 4.8)
box(ax, 0.2, 0.3, 11.6, 3.6, BG_L, C_L, lw=1.2, rad=0.18, zo=1)

# 1. betweenness ranking → top-10 slice
txt(ax, 1.7, 3.5, "PDG nodes ranked", ha="center", fontsize=8.6,
        fontweight="bold", color=C_L)
ranks = [0.95, 0.82, 0.61, 0.40, 0.25, 0.12]
for i, v in enumerate(ranks):
    top = i < 3
    box(ax, 0.7, 2.9 - i * 0.26, v * 1.9, 0.2,
        C_L if top else "#CE93D8", C_L, lw=0, rad=0.03, zo=4)
txt(ax, 1.7, 1.15, "betweenness centrality\n→ keep top-10", ha="center",
        va="center", fontsize=6.8, color="#37474F")
arrow(ax, 2.9, 2.1, 3.6, 2.1, col=C_L, lw=1.6, ms=10)

# 2. slice text
box(ax, 3.7, 1.4, 2.7, 1.45, "white", C_L, lw=1.3, rad=0.08, zo=4)
txt(ax, 5.05, 2.62, "focused slice", ha="center", fontsize=7.6,
        fontweight="bold", color=C_L)
for i, ln in enumerate(["int l = strlen(s);", "memcpy(buf, s, l);",
                        "return buf[n];"]):
    txt(ax, 3.85, 2.25 - i * 0.32, ln, fontfamily="monospace", fontsize=6.4,
            color=C_BAD if "memcpy" in ln else "#4A148C", va="center")
txt(ax, 5.05, 1.2, "≤ 512 BPE tokens", ha="center", va="center", fontsize=6.6,
        color="#37474F")
arrow(ax, 6.45, 2.1, 7.2, 2.1, col=C_L, lw=1.6, ms=10)

# 3. CodeBERT
box(ax, 7.3, 1.5, 1.9, 1.35, C_L, C_L, lw=0, rad=0.12, zo=4)
txt(ax, 8.25, 2.4, "CodeBERT", ha="center", va="center", fontsize=8.4,
        fontweight="bold", color="white")
txt(ax, 8.25, 1.95, "RoBERTa-base\nfine-tuned", ha="center", va="center",
        fontsize=6.5, color="white")
arrow(ax, 9.25, 2.1, 9.95, 2.1, col=C_L, lw=1.6, ms=10)
txt(ax, 10.8, 2.1, "h_L ∈ ℝ²⁵⁶", ha="center", va="center", fontsize=9,
        fontweight="bold", color=C_L,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=C_L,
                  lw=1.4))

title(ax, 6.0, 4.45,
      "LLM branch — focuses CodeBERT on the most structurally critical code",
      fs=11)

save(fig, os.path.join(os.path.dirname(__file__), "fig07_llm_branch.png"))
