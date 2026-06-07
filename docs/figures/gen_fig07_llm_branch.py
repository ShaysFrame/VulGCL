"""Fig 7 (Slide 9) — LLM Branch: betweenness ranking → focused code slice → CodeBERT → h_L.
Run: python docs/figures/gen_fig07_llm_branch.py
Output: docs/figures/fig07_llm_branch.png
"""
import numpy as np
import matplotlib.patches as mpatches
from _figstyle import C_L, C_IN, C_BAD, BG_L
from _figstyle import txt, new_canvas, box, title, save
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

C_HDR = "#6A1B9A"

fig, ax = new_canvas(14, 9.0)
title(ax, 7.0, 8.38,
      "LLM Branch — betweenness-guided slice focuses CodeBERT on critical code", fs=12.5)

# ── LEFT: betweenness centrality bar chart ────────────────────────────────────
txt(ax, 2.0, 7.38, "PDG Nodes — Betweenness Centrality", ha="center",
    fontsize=10, fontweight="bold", color=C_L)
txt(ax, 2.0, 7.16, "higher score = more critical to information flow",
    ha="center", fontsize=7.5, color="#546E7A")

nodes_bc = [
    ("2: if (x>0&&x<20)",  0.62, True),
    ("3: buffer[x] = 0;",  0.41, True),
    ("5: printf(buf[0]);", 0.31, True),
    ("1: int buffer[10];", 0.20, False),
    ("4: }",               0.15, False),
    ("6: }",               0.08, False),
]
bar_x0 = 0.25
bar_maxw = 3.5
bar_y0 = 6.68
bar_h = 0.38
bar_gap = 0.12

for i, (lbl, score, top) in enumerate(nodes_bc):
    y = bar_y0 - i*(bar_h + bar_gap)
    w = score * bar_maxw
    col = C_L if top else "#CE93D8"
    box(ax, bar_x0, y, w, bar_h, col, col, lw=0, rad=0.04, zo=4)
    txt(ax, bar_x0 + w + 0.08, y + bar_h/2, f"{score:.2f}",
        ha="left", va="center", fontsize=7.5, color=col, fontweight="bold")
    txt(ax, bar_x0 - 0.05, y + bar_h/2, lbl,
        ha="right", va="center", fontfamily="monospace", fontsize=7.0, color="#212121")

# bracket annotation for top-3
brx = bar_x0 + bar_maxw + 0.7
brt = bar_y0 + bar_h
brb = bar_y0 - 2*(bar_h + bar_gap)
ax.plot([brx-1.32, brx-1.22, brx-1.22, brx-1.32], [brt, brt, brb, brb],
        color=C_L, lw=1.4, zorder=8)
txt(ax, brx-1.12, (brt+brb)/2, "top-10\nselected", ha="left", va="center",
    fontsize=7.2, color=C_L, fontweight="bold")

# ── CENTER: arrow ─────────────────────────────────────────────────────────────
pts = np.array([[4.55-0.35, 5.5],
                [5.15-0.35, 5.5],
                [5.15-0.35, 5.78],
                [5.7-0.35, 5.25],
                [5.15-0.35, 4.72],
                [5.15-0.35, 5.0],
                [4.55-0.35, 5.0]])
ax.fill(pts[:, 0], pts[:, 1], color=C_L, zorder=8, alpha=0.90)
txt(ax, 5.12-0.35, 5.25, "focus\nslice", ha="center", va="center",
    fontsize=7.0, fontweight="bold", color="white")

# ── CENTER-RIGHT: focused code slice (code block) ─────────────────────────────
txt(ax, 7.9, 7.38, "Focused Code Slice", ha="center",
    fontsize=10, fontweight="bold", color=C_L)
txt(ax, 7.9, 7.08, "top-10 nodes by betweenness centrality  ·  ≤ 512 BPE tokens",
    ha="center", fontsize=7.5, color="#546E7A")

# code editor box
box(ax, 5.85, 3.5, 4.1, 3.25, "#FAFAFA", "#90A4AE", lw=1.2, rad=0.1, zo=3)
box(ax, 5.85, 6.45, 4.1, 0.3, "#D7B8F5", "#90A4AE", lw=0, rad=0.08, zo=4)

code_slice = [
    ("void vulnerable_fn(int x) {", False),
    ("    int buffer[10];",          False),
    ("    if (x > 0 && x < 20) {",  False),
    ("        buffer[x] = 0;",      True),
    ("    }",                        False),
    ('    printf("%d", buffer[0]);', False),
    ("}",                            False),
]
for i, (line, vuln) in enumerate(code_slice):
    y = 6.18 - i*0.37
    if vuln:
        box(ax, 5.9, y-0.16, 3.95, 0.32, "#FFEBEE",
            "#FFCDD2", lw=0, rad=0.02, zo=4)
    txt(ax, 6.02, y, line, ha="left", va="center",
        fontfamily="monospace", fontsize=7.2,
        color=C_BAD if vuln else "#212121",
        fontweight="bold" if vuln else "normal")

txt(ax, 7.9, 3.28, "← critical path extracted from PDG betweenness ranking",
    ha="center", va="center", fontsize=6.8, color=C_L, style="italic")

# ── RIGHT: CodeBERT processing ────────────────────────────────────────────────
txt(ax, 11.5, 7.38, "CodeBERT Encoding", ha="center",
    fontsize=10, fontweight="bold", color=C_L)

# arrow from code → CodeBERT
ax.annotate("", xy=(10.2, 5.12), xytext=(9.98, 5.12),
            arrowprops=dict(arrowstyle="-|>", color=C_L, lw=1.8, mutation_scale=12))

# tokenization preview
box(ax, 10.25, 6.0, 3.3, 1.05, BG_L, C_L, lw=1.0, rad=0.08, zo=4)
txt(ax, 11.9, 6.82, "BPE Tokenization", ha="center", va="center",
    fontsize=7.5, fontweight="bold", color=C_L)
tokens = ["[CLS]", "int", "buffer", "[10]", "if",
          "x", ">", "0", "buffer", "[x]", "=", "0", "[SEP]"]
txt(ax, 11.9, 6.52, "  ".join(tokens[:7]),
    ha="center", va="center", fontfamily="monospace", fontsize=6.2, color="#4A148C")
txt(ax, 11.9, 6.34, "  ".join(tokens[7:]) + "  ...",
    ha="center", va="center", fontfamily="monospace", fontsize=6.2, color="#4A148C")

# CodeBERT box
box(ax, 10.25, 3.95, 3.3, 1.85, C_L, C_L, lw=0, rad=0.12, zo=4)
txt(ax, 11.9, 5.25, "CodeBERT", ha="center", va="center",
    fontsize=11, fontweight="bold", color="white")
txt(ax, 11.9, 4.75, "RoBERTa-base", ha="center", va="center",
    fontsize=8.0, color="white")
txt(ax, 11.9, 4.3,  "fine-tuned on code", ha="center", va="center",
    fontsize=7.5, color="white")

# [CLS] → projection → h_L
ax.annotate("", xy=(11.9, 3.78), xytext=(11.9, 3.95),
            arrowprops=dict(arrowstyle="-|>", color=C_L, lw=1.5, mutation_scale=11))
txt(ax, 11.9, 3.62, "[CLS] token  →  proj 768 → 256",
    ha="center", va="center", fontsize=7.2, color=C_L)

ax.annotate("", xy=(11.9, 3.12), xytext=(11.9, 3.44),
            arrowprops=dict(arrowstyle="-|>", color=C_L, lw=1.8, mutation_scale=13))
box(ax, 10.95, 2.38, 1.9, 0.72, BG_L, C_L, lw=1.8, rad=0.12, zo=5)
txt(ax, 11.9, 2.9, "h_L",     ha="center", va="center",
    fontsize=11, fontweight="bold", color=C_L)
txt(ax, 11.9, 2.5, "∈  ℝ²⁵⁶", ha="center", va="center", fontsize=8.5, color=C_L)

# ── BOTTOM: stats box ─────────────────────────────────────────────────────────
box(ax, 0.15, 0.12, 13.7, 0.62, BG_L, C_L, lw=1.2, rad=0.1, zo=3)
txt(ax, 7.0, 0.43, "Betweenness centrality ranks nodes by how often they lie on the shortest"
    " dependency path — these carry the most vulnerability signal.",
    ha="center", va="center", fontsize=7.8, color=C_L)

save(fig, os.path.join(os.path.dirname(__file__), "fig07_llm_branch.png"))
