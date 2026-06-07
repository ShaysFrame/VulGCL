"""Fig 6 (Slide 8) — Image Branch: centrality scores → 3-channel pixel image → CNN → h_I.
Run: python docs/figures/gen_fig06_image_branch.py
Output: docs/figures/fig06_image_branch.png
"""
import numpy as np
import matplotlib.patches as mpatches
from _figstyle import C_I, C_IN, BG_I
from _figstyle import txt, new_canvas, box, title, save
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

C_HDR = "#2E7D32"

fig, ax = new_canvas(16, 9.0)
title(ax, 7.0, 8.50, "Image Branch — PDG centrality scores encoded as a visual signature", fs=12.5)

# ── LEFT: centrality score table ─────────────────────────────────────────────
txt(ax, 2.1, 7.38, "PDG Node Centrality Scores", ha="center",
    fontsize=10, fontweight="bold", color=C_I)
txt(ax, 2.1, 7.08, "3 metrics × N nodes  →  N × 3 matrix",
    ha="center", fontsize=7.5, color="#546E7A")

TX = 0.25
ROWY = 6.78
RH = 0.44
CWS_T = [1.85, 1.1, 1.1, 1.1]
hdrs_T = ["Node (statement)", "Degree", "Closeness", "Katz"]
trows = [
    ("1: int buffer[10];",  "0.00", "0.33", "0.20"),
    ("2: if (x>0&&x<20){",  "0.67", "0.58", "0.62"),
    ("3: buffer[x] = 0;",   "0.50", "0.48", "0.41"),
    ("4: }",                 "0.17", "0.28", "0.15"),
    ("5: printf(buf[0]);",   "0.33", "0.38", "0.31"),
]

hx = TX
for hdr, cw in zip(hdrs_T, CWS_T):
    box(ax, hx, ROWY-RH, cw, RH, C_HDR, C_HDR, lw=0, rad=0.0, zo=4)
    txt(ax, hx+cw/2, ROWY-RH/2, hdr, ha="center", va="center",
        fontsize=7.2, fontweight="bold", color="white")
    hx += cw

for ri, row in enumerate(trows):
    ry = ROWY - RH*(ri+2)
    bg = "#F2FBF2" if ri % 2 == 0 else "white"
    rx = TX
    for ci, (val, cw) in enumerate(zip(row, CWS_T)):
        box(ax, rx, ry, cw, RH, bg, "#C8E6C9", lw=0.6, rad=0.0, zo=4)
        txt(ax, rx+cw/2, ry+RH/2, val, ha="center", va="center", fontsize=7.2,
            fontfamily="monospace" if ci == 0 else "DejaVu Sans", color="#212121")
        rx += cw

box(ax, TX, ROWY-RH*(len(trows)+1), sum(CWS_T), RH*(len(trows)+1),
    "none", "#81C784", lw=1.2, rad=0.04, zo=5)

# ── CENTER ARROW ──────────────────────────────────────────────────────────────
pts = np.array([[4.4, 5.55], [5.0, 5.55], [5.0, 5.83], [5.55, 5.3],
                [5.0, 4.77], [5.0, 5.05], [4.4, 5.05]])
ax.fill(pts[:, 0], pts[:, 1], color=C_I, zorder=8, alpha=0.90)
txt(ax, 4.97, 5.3, "score\n×emb", ha="center", va="center",
    fontsize=7.0, fontweight="bold", color="white")

# ── CENTER: pixel image visualization ─────────────────────────────────────────
txt(ax, 7.75, 7.38, "3-Channel 100×100 Image", ha="center",
    fontsize=10, fontweight="bold", color=C_I)
txt(ax, 7.75, 7.08, "each row = centrality × CodeBERT embed (256-dim)",
    ha="center", fontsize=7.5, color="#546E7A")

rng = np.random.default_rng(seed=42)
# 3 channels simulating the centrality-weighted embedding structure
ch_data = [
    np.clip(rng.normal(0.5, 0.15, (10, 10)) +
            np.linspace(0, 0.4, 10).reshape(-1, 1), 0, 1),
    np.clip(rng.normal(0.4, 0.18, (10, 10)) +
            np.linspace(0, 0.3, 10).reshape(1, -1), 0, 1),
    np.clip(rng.normal(0.45, 0.12, (10, 10)), 0, 1),
]
cmaps = ["Greens", "Blues", "Purples"]
labels = ["Ch 1\n(degree)", "Ch 2\n(closeness)", "Ch 3\n(katz)"]
xs = [5.8, 7.1, 8.4]
for ch, cmap, lbl, xo in zip(ch_data, cmaps, labels, xs):
    ax.imshow(ch, extent=[xo, xo+1.15, 3.4, 6.7], cmap=cmap,
              alpha=0.88, zorder=3, aspect="auto")
    ax.add_patch(mpatches.Rectangle((xo, 3.4), 1.15, 3.3, fill=False,
                                    edgecolor=C_I, lw=1.3, zorder=6))
    txt(ax, xo+0.575, 3.15, lbl, ha="center", va="center",
        fontsize=7.0, color=C_I, fontweight="bold")

# row labels on left of image grid
row_lbls = ["buf[10]", "if(x>..", "buf[x]", "  }   ", "printf"]
for ri, rl in enumerate(row_lbls):
    y = 6.37 - ri*0.66
    txt(ax, 5.7, y, rl, ha="right", va="center",
        fontfamily="monospace", fontsize=5.8, color="#546E7A")

# bracket showing "100 nodes → top 100 by centrality"
txt(ax, 7.75, 2.72, "↑ 100 rows (nodes) × 100 cols (embed dims projected) × 3 channels",
    ha="center", va="center", fontsize=7.0, color="#37474F", style="italic")

# ── RIGHT: CNN ────────────────────────────────────────────────────────────────
txt(ax, 11.75, 7.38, "3-Layer CNN + AvgPool", ha="center",
    fontsize=10, fontweight="bold", color=C_I)

# arrow from image to CNN
ax.annotate("", xy=(9.75, 5.05), xytext=(9.62, 5.05),
            arrowprops=dict(arrowstyle="-|>", color=C_I, lw=1.8, mutation_scale=12))

# CNN layer stack (3 conv blocks)
cnn_layers = [
    # (9.85, 3.9, 1.8, 2.2,  "Conv + BN\n+ ReLU",    "#C8E6C9", C_I),
    (9.85, 3.9, 1.8, 2.2,  "",    "#C8E6C9", C_I),
    # (10.1, 3.7, 1.8, 2.2,  "Conv + BN\n+ ReLU",    "#A5D6A7", C_I),
    (10.1, 3.7, 1.8, 2.2,  "",    "#A5D6A7", C_I),
    (10.35, 3.5, 1.8, 2.2,  "Conv + BN\n+ ReLU",    "#81C784", C_I),
]
for x, y, w, h, lbl, fc, ec in cnn_layers:
    box(ax, x, y, w, h, fc, ec, lw=1.2, rad=0.08, zo=4)
    txt(ax, x+w/2, y+h/2, lbl, ha="center", va="center",
        fontsize=7.5, color="#1B5E20", fontweight="bold")

# AvgPool → h_I
ax.annotate("", xy=(12.4, 5.05), xytext=(12.25, 5.05),
            arrowprops=dict(arrowstyle="-|>", color=C_I, lw=1.8, mutation_scale=12))
txt(ax, 12.05, 5.3, "AvgPool", ha="center", va="center", fontsize=7.2, color=C_I)
box(ax, 12.45, 4.42, 1.35, 1.25, BG_I, C_I, lw=1.8, rad=0.12, zo=5)
txt(ax, 13.13, 5.22, "h_I",    ha="center", va="center",
    fontsize=11, fontweight="bold", color=C_I)
txt(ax, 13.13, 4.75, "∈  ℝ²⁵⁶", ha="center",
    va="center", fontsize=8.5, color=C_I)

# ── BOTTOM: encoding explanation ──────────────────────────────────────────────
box(ax, 0.15, 0.12, 13.7, 0.65, BG_I, C_I, lw=1.2, rad=0.1, zo=3)
txt(ax, 7.0, 0.45, "Pixel (i, j, c) = centrality_score_c(node i)  ×  CodeBERT_embed(node i)[j]"
    "   →   spatial pattern captures dependency topology",
    ha="center", va="center", fontsize=7.8, color=C_I)

save(fig, os.path.join(os.path.dirname(__file__), "fig06_image_branch.png"))
