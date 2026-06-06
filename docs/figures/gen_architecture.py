"""
Generate Figure 1: VulGCL Architecture Diagram
Output: docs/figures/fig1_architecture.png
Run: python docs/figures/gen_architecture.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Color palette ─────────────────────────────────────────────────────────────
C_BG      = "#FAFAFA"
C_GRAPH   = "#1565C0"
C_IMAGE   = "#2E7D32"
C_LLM     = "#6A1B9A"
C_FUSION  = "#B71C1C"
C_INPUT   = "#37474F"
C_LIGHT_G = "#BBDEFB"
C_LIGHT_I = "#C8E6C9"
C_LIGHT_L = "#E1BEE7"
C_LIGHT_F = "#FFCDD2"
C_LIGHT_IN= "#ECEFF1"

fig, ax = plt.subplots(figsize=(17, 8))
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)
ax.set_xlim(0, 17)
ax.set_ylim(0, 8)
ax.axis("off")

def box(x, y, w, h, face, edge, lw=2.0, radius=0.15, zorder=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0.0,rounding_size={radius}",
                                facecolor=face, edgecolor=edge,
                                linewidth=lw, zorder=zorder))

def lbl(x, y, txt, color="#212121", fs=9, weight="normal", ha="center", va="center"):
    ax.text(x, y, txt, color=color, fontsize=fs, fontweight=weight,
            ha=ha, va=va, zorder=6)

def arr(x1, y1, x2, y2, color="#555", lw=1.6, ms=12):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=ms), zorder=4)

def dim_tag(x, y, txt, col):
    ax.text(x, y, txt, color=col, fontsize=7.5, ha="center", va="center",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor=col, linewidth=1.3), zorder=7)

# ══════════════════════════════════════════════════════════════════════════════
# TITLE STRIP (top band, well separated from content)
# ══════════════════════════════════════════════════════════════════════════════
ax.axhspan(7.05, 8.0, color="#E3F2FD", zorder=0)
ax.text(8.5, 7.6, "VulGCL: Multimodal C/C++ Vulnerability Detection Framework",
        ha="center", va="center", fontsize=14, fontweight="bold", color="#0D47A1")
ax.text(8.5, 7.18,
        "Three independent views of each function fused via late concatenation  ·  "
        "Graph (structural)  +  Image (visual)  +  LLM (semantic)",
        ha="center", va="center", fontsize=8.5, color="#1565C0", style="italic")

# Divider
ax.axhline(7.05, color="#BBDEFB", lw=1.5)

# ══════════════════════════════════════════════════════════════════════════════
# INPUT COLUMN  (x: 0.2 – 2.2)
# ══════════════════════════════════════════════════════════════════════════════
# Input function box
box(0.2, 3.5, 2.0, 3.2, C_LIGHT_IN, C_INPUT)
lbl(1.2, 6.35, "C / C++",        color=C_INPUT, fs=10, weight="bold")
lbl(1.2, 6.0,  "Function",       color=C_INPUT, fs=10, weight="bold")
code = ["void foo(char *src,",
        "         int n) {",
        "  char buf[10];",
        "  int l = strlen(s);",
        "  memcpy(buf,src,l);",
        "  return buf[n];",
        "}"]
for i, line in enumerate(code):
    ax.text(0.32, 5.62 - i * 0.32, line, color="#546E7A",
            fontsize=5.8, fontfamily="monospace", va="center", zorder=6)

# Joern box
box(0.2, 1.2, 2.0, 1.9, C_LIGHT_IN, C_INPUT)
lbl(1.2, 2.75, "Joern",          color=C_INPUT, fs=10.5, weight="bold")
lbl(1.2, 2.4,  "Static Analysis", color=C_INPUT, fs=7.5)
lbl(1.2, 2.1,  "PDG Extraction",  color=C_INPUT, fs=7.5)
lbl(1.2, 1.75, ".sc file → DOT",  color=C_INPUT, fs=7)
arr(1.2, 3.5, 1.2, 3.12)

# ══════════════════════════════════════════════════════════════════════════════
# PDG BOX  (x: 2.6 – 4.6)
# ══════════════════════════════════════════════════════════════════════════════
box(2.6, 2.0, 2.0, 2.7, C_LIGHT_IN, C_INPUT)
lbl(3.6, 4.3,  "PDG",             color=C_INPUT, fs=11, weight="bold")
lbl(3.6, 3.95, "Program",         color=C_INPUT, fs=8)
lbl(3.6, 3.68, "Dependency",      color=C_INPUT, fs=8)
lbl(3.6, 3.41, "Graph",           color=C_INPUT, fs=8)

# Mini graph inside PDG box
npos = [(3.1, 3.1), (3.6, 3.1), (4.1, 3.1),
        (3.35, 2.6), (3.85, 2.6), (3.6, 2.2)]
for nx, ny in npos:
    ax.add_patch(plt.Circle((nx, ny), 0.13, color=C_INPUT, zorder=5))
for s, t in [(0,3),(1,3),(1,4),(2,4),(3,5),(4,5)]:
    x1, y1 = npos[s]; x2, y2 = npos[t]
    ax.annotate("", xy=(x2, y2+0.13), xytext=(x1, y1-0.13),
                arrowprops=dict(arrowstyle="-|>", color=C_INPUT,
                                lw=0.8, mutation_scale=5), zorder=4)

arr(2.2, 2.15, 2.57, 2.8, lw=1.5)

# ══════════════════════════════════════════════════════════════════════════════
# THREE BRANCHES  (x: 5.0 – 8.2)
# ══════════════════════════════════════════════════════════════════════════════
BW = 3.0
BX = 5.0

branches = [
    (4.7, C_LIGHT_G, C_GRAPH, "Graph Branch",
     ["PDG → PyG Data object",
      "Node features: CodeBERT embed.",
      "2-layer Graph Attention (GAT)",
      "Global mean pooling",
      "h_G  ∈  ℝ²⁵⁶"]),
    (2.7, C_LIGHT_I, C_IMAGE, "Image Branch",
     ["PDG nodes → 3-ch centrality img",
      "Channels: degree / closeness / Katz",
      "Resize to 100 × 100 (bilinear)",
      "5-layer CNN → GlobalAvgPool",
      "h_I  ∈  ℝ²⁵⁶"]),
    (0.7, C_LIGHT_L, C_LLM, "LLM Branch",
     ["Raw source code (max 512 tokens)",
      "BPE tokenizer → input_ids",
      "CodeBERT (RoBERTa-base, 768-dim)",
      "Linear projection 768 → 256",
      "h_L  ∈  ℝ²⁵⁶"]),
]

branch_mid_y = []
for (yb, fl, ed, title, subs) in branches:
    BH = 1.75
    box(BX, yb, BW, BH, fl, ed, lw=2.2)
    yc = yb + BH / 2
    branch_mid_y.append(yc)
    lbl(BX + BW/2, yb + BH - 0.25, title, color=ed, fs=10, weight="bold")
    for i, s in enumerate(subs):
        lbl(BX + BW/2, yb + BH - 0.6 - i * 0.24, s, color="#333", fs=7.2)
    # Arrow: PDG → branch
    ax.annotate("", xy=(BX, yc), xytext=(4.62, 3.0),
                arrowprops=dict(arrowstyle="-|>", color=ed, lw=1.4,
                                mutation_scale=11,
                                connectionstyle="arc3,rad=0.0"), zorder=4)

# ══════════════════════════════════════════════════════════════════════════════
# DIM TAGS  (x: ~9.4)
# ══════════════════════════════════════════════════════════════════════════════
TAG_X = 9.4
colors = [C_GRAPH, C_IMAGE, C_LLM]
tags   = ["h_G   256", "h_I   256", "h_L   256"]
for yc, col, tag in zip(branch_mid_y, colors, tags):
    arr(BX + BW, yc, TAG_X - 0.05, yc, color=col, lw=1.5)
    dim_tag(TAG_X + 0.25, yc, tag, col)

# ══════════════════════════════════════════════════════════════════════════════
# CONCAT BOX  (x: 10.2 – 12.8)
# ══════════════════════════════════════════════════════════════════════════════
CAT_X = 10.2; CAT_Y = 2.7; CAT_W = 2.7; CAT_H = 0.85
box(CAT_X, CAT_Y, CAT_W, CAT_H, C_LIGHT_F, C_FUSION, lw=2.2)
lbl(CAT_X + CAT_W/2, CAT_Y + CAT_H/2 + 0.15,
    "Concatenate", color=C_FUSION, fs=10, weight="bold")
lbl(CAT_X + CAT_W/2, CAT_Y + CAT_H/2 - 0.18,
    "[h_G ; h_I ; h_L]  ∈  ℝ⁷⁶⁸", color=C_FUSION, fs=7.5)

for yc, col in zip(branch_mid_y, colors):
    ax.annotate("", xy=(CAT_X, CAT_Y + CAT_H/2),
                xytext=(TAG_X + 0.5, yc),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.3,
                                mutation_scale=10,
                                connectionstyle="arc3,rad=0.0"), zorder=4)

# ══════════════════════════════════════════════════════════════════════════════
# MLP BOX  (x: 13.4 – 15.8)
# ══════════════════════════════════════════════════════════════════════════════
MLP_X = 13.4; MLP_Y = 2.7; MLP_W = 2.5; MLP_H = 0.85
box(MLP_X, MLP_Y, MLP_W, MLP_H, C_LIGHT_F, C_FUSION, lw=2.2)
lbl(MLP_X + MLP_W/2, MLP_Y + MLP_H/2 + 0.15,
    "MLP Classifier", color=C_FUSION, fs=10, weight="bold")
lbl(MLP_X + MLP_W/2, MLP_Y + MLP_H/2 - 0.18,
    "768 → 256 → 1  +  Sigmoid", color=C_FUSION, fs=7.5)

arr(CAT_X + CAT_W, CAT_Y + CAT_H/2,
    MLP_X,          MLP_Y + MLP_H/2, color=C_FUSION, lw=2.0, ms=13)

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT  (x: 16.2+)
# ══════════════════════════════════════════════════════════════════════════════
MID_Y = MLP_Y + MLP_H / 2
arr(MLP_X + MLP_W, MID_Y, 16.25, MID_Y + 0.65, color="#B71C1C", lw=1.5)
arr(MLP_X + MLP_W, MID_Y, 16.25, MID_Y - 0.65, color="#1B5E20", lw=1.5)
ax.text(16.28, MID_Y + 0.65, "Vulnerable",
        color="#B71C1C", fontsize=10, fontweight="bold", va="center")
ax.text(16.28, MID_Y - 0.65, "Safe",
        color="#1B5E20", fontsize=10, fontweight="bold", va="center")

# ── Save ──────────────────────────────────────────────────────────────────────
fig.savefig("docs/figures/fig1_architecture.png", dpi=180,
            bbox_inches="tight", facecolor=C_BG)
print("Saved: docs/figures/fig1_architecture.png")
