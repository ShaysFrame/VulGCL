"""
Generate Figure 1: VulGCL Architecture — Horizontal 3D-layer style
Output: docs/figures/fig1_architecture.png
Run from project root: python docs/figures/gen_architecture.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np

# ── Canvas ────────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 22, 9.0
C_BG     = "#F0F2F8"
C_GRAPH  = "#1565C0"
C_IMAGE  = "#2E7D32"
C_LLM    = "#6A1B9A"
C_FUSION = "#B71C1C"
C_INPUT  = "#37474F"
C_TITLE  = "#0D47A1"

L_GRAPH  = "#DBEAFE"
L_IMAGE  = "#DCFCE7"
L_LLM    = "#EDE9FE"
L_INPUT  = "#E2E8F0"

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")


# ── Helpers ───────────────────────────────────────────────────────────────────
def _dk(color, f):
    return tuple(max(0., min(1., c * f)) for c in mcolors.to_rgb(color))

def arrow(x1, y1, x2, y2, col="#555", lw=1.7, ms=12, rad=0.0, zo=12):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                mutation_scale=ms,
                                connectionstyle=f"arc3,rad={rad}"), zorder=zo)

def rbox(x, y, w, h, fc, ec, lw=1.5, zo=3, rad=0.12):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rad}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zo))

def txt(x, y, s, c="#1a1a1a", fs=8.5, fw="normal",
        ha="center", va="center", zo=15, it=False):
    ax.text(x, y, s, color=c, fontsize=fs, fontweight=fw,
            ha=ha, va=va, zorder=zo, style="italic" if it else "normal")


def box3d(x, y, w, h, color, dx=0.20, dy=0.13, zo=5,
          label=None, sub=None, lc="white", lfs=7.5):
    """
    3D perspective box: front face + right side face + top face.
    (x, y) = bottom-left of front face.
    dx/dy = depth direction (upper-right).
    """
    ec     = _dk(color, 0.45)
    right_c = _dk(color, 0.62)
    top_c   = _dk(color, 0.77)

    # Right face (parallelogram)
    ax.add_patch(mpatches.Polygon([
        [x+w,    y],
        [x+w+dx, y+dy],
        [x+w+dx, y+h+dy],
        [x+w,    y+h],
    ], closed=True, facecolor=right_c, edgecolor=ec, lw=0.65, zorder=zo))

    # Top face (parallelogram)
    ax.add_patch(mpatches.Polygon([
        [x,      y+h],
        [x+w,    y+h],
        [x+w+dx, y+h+dy],
        [x+dx,   y+h+dy],
    ], closed=True, facecolor=top_c, edgecolor=ec, lw=0.65, zorder=zo))

    # Front face
    ax.add_patch(mpatches.Polygon([
        [x,   y],
        [x+w, y],
        [x+w, y+h],
        [x,   y+h],
    ], closed=True, facecolor=color, edgecolor=ec, lw=1.05, zorder=zo+1))

    # Labels
    if label:
        ty = y + h/2 + (0.11 if sub else 0)
        ax.text(x+w/2, ty, label, ha="center", va="center",
                fontsize=lfs, color=lc, fontweight="bold", zorder=zo+2)
    if sub:
        ax.text(x+w/2, y+h/2-0.19, sub, ha="center", va="center",
                fontsize=lfs-1.3, color=lc, alpha=0.88, zorder=zo+2)


# ── Title strip ───────────────────────────────────────────────────────────────
ax.axhspan(8.35, 9.0, color="#E8EAF6", zorder=0)
ax.axhline(8.35, color="#9FA8DA", lw=1.3)
txt(FIG_W/2, 8.72,
    "VulGCL: Multimodal C/C++ Vulnerability Detection Framework",
    c=C_TITLE, fs=14.5, fw="bold")
txt(FIG_W/2, 8.46,
    "Graph (structural topology)  ·  Image (visual centrality pattern)  ·  "
    "LLM (semantic PDG slice)  →  Late fusion",
    c="#3949AB", fs=8.5, it=True)


# ═══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — Input + Joern + PDG
# ═══════════════════════════════════════════════════════════════════════════════
# C/C++ function box
rbox(0.2, 4.3, 1.9, 3.6, L_INPUT, C_INPUT, lw=1.8, zo=4)
txt(1.15, 7.55, "C / C++",    c=C_INPUT, fs=9.5, fw="bold")
txt(1.15, 7.22, "Function",   c=C_INPUT, fs=9.5, fw="bold")
code_lines = [
    "void foo(char *s,",
    "        int n) {",
    "  char buf[10];",
    "  int l=strlen(s);",
    "  memcpy(buf,s,l);",  # ← vulnerable
    "  return buf[n];",
    "}",
]
for i, line in enumerate(code_lines):
    col = "#C62828" if "memcpy" in line else "#546E7A"
    fw  = "bold"   if "memcpy" in line else "normal"
    ax.text(0.32, 6.82 - i*0.34, line, color=col, fontsize=5.6,
            fontfamily="monospace", va="center", fontweight=fw, zorder=6)

# Joern box
rbox(0.2, 1.9, 1.9, 2.05, L_INPUT, C_INPUT, lw=1.8, zo=4)
txt(1.15, 3.55, "Joern",           c=C_INPUT, fs=9.5, fw="bold")
txt(1.15, 3.22, "Static Analysis", c=C_INPUT, fs=7.5)
txt(1.15, 2.95, "PDG Extraction",  c=C_INPUT, fs=7.5)
txt(1.15, 2.65, ".sc → DOT",       c=C_INPUT, fs=7.0)
txt(1.15, 2.32, "Unique workspace", c=C_INPUT, fs=6.5)
arrow(1.15, 4.3, 1.15, 3.97, col=C_INPUT)

# PDG box
rbox(2.45, 2.8, 1.75, 2.2, L_INPUT, C_INPUT, lw=1.8, zo=4)
txt(3.33, 4.65, "PDG",         c=C_INPUT, fs=10, fw="bold")
txt(3.33, 4.32, "Program",     c=C_INPUT, fs=7.5)
txt(3.33, 4.06, "Dependency",  c=C_INPUT, fs=7.5)
txt(3.33, 3.80, "Graph",       c=C_INPUT, fs=7.5)

# Mini PDG graph inside box
node_pos = [(2.7,3.4),(3.1,3.4),(3.5,3.4),(2.9,3.05),(3.3,3.05),(3.1,2.72)]
for nx_, ny_ in node_pos:
    ax.add_patch(plt.Circle((nx_, ny_), 0.11, color=C_INPUT, zorder=7))
for s, t in [(0,3),(1,3),(1,4),(2,4),(3,5),(4,5)]:
    x1, y1 = node_pos[s]; x2, y2 = node_pos[t]
    ax.annotate("", xy=(x2, y2+0.11), xytext=(x1, y1-0.11),
                arrowprops=dict(arrowstyle="-|>", color=C_INPUT,
                                lw=0.7, mutation_scale=5), zorder=6)

arrow(2.12, 2.9, 2.42, 3.2, col=C_INPUT, lw=1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# BRANCH BACKGROUND STRIPS
# ═══════════════════════════════════════════════════════════════════════════════
BSTRIP_X0 = 4.4
BSTRIP_X1 = 15.8

branch_meta = [
    # y0,  y1,  light_bg,  branch_color, branch_name
    (5.65, 8.25, L_GRAPH, C_GRAPH, "Graph\nBranch"),
    (2.90, 5.40, L_IMAGE, C_IMAGE, "Image\nBranch"),
    (0.30, 2.65, L_LLM,   C_LLM,  "LLM\nBranch"),
]

for y0, y1, lbg, col, name in branch_meta:
    rbox(BSTRIP_X0, y0, BSTRIP_X1 - BSTRIP_X0, y1 - y0,
         lbg, col, lw=1.1, zo=1, rad=0.25)
    txt(BSTRIP_X0 - 0.65, (y0+y1)/2, name, c=col, fs=8.5, fw="bold")


# ═══════════════════════════════════════════════════════════════════════════════
# BRANCH 3D BOXES
# ═══════════════════════════════════════════════════════════════════════════════
# Each branch: 4 processing boxes, side by side, with 3D tilt effect
# Box dimensions: w=1.75, h=1.55, gap=0.35 between boxes

BW  = 1.75   # box width
BH  = 1.55   # box height
GAP = 0.38   # gap between boxes
DX  = 0.20   # 3D depth x
DY  = 0.13   # 3D depth y

# X positions for the 4 boxes in each branch
box_xs = [BSTRIP_X0 + 0.25 + i*(BW + GAP) for i in range(4)]
# => approx: 4.65, 6.78, 8.91, 11.04

# ── Graph Branch (y center = 6.95, box bottom = 6.175) ───────────────────────
GY = 5.65 + (8.25 - 5.65)/2 - BH/2   # vertically centered in strip
graph_boxes = [
    (C_GRAPH, "CodeBERT",    "node embed"),
    (_dk(C_GRAPH, 0.82), "GAT Layer 1", "8 heads"),
    (_dk(C_GRAPH, 0.67), "GAT Layer 2", "8 heads"),
    (_dk(C_GRAPH, 0.55), "Global\nMean Pool", "→ 256-dim"),
]
for i, (col, lbl, sub) in enumerate(graph_boxes):
    box3d(box_xs[i], GY, BW, BH, col, dx=DX, dy=DY, zo=5+i,
          label=lbl, sub=sub)
    if i < 3:
        arrow(box_xs[i]+BW+DX*0.4, GY+BH/2+DY*0.3,
              box_xs[i+1]-0.01, GY+BH/2,
              col=C_GRAPH, lw=1.4, ms=9)

# ── Image Branch (y center = 4.15, box bottom = 3.375) ───────────────────────
IY = 2.90 + (5.40 - 2.90)/2 - BH/2
image_boxes = [
    (C_IMAGE, "3-ch Image",   "100 × 100"),
    (_dk(C_IMAGE, 0.82), "Conv 1-2",    "ReLU + BN"),
    (_dk(C_IMAGE, 0.67), "Conv 3-5",    "ReLU + BN"),
    (_dk(C_IMAGE, 0.55), "Global\nAvg Pool", "→ 256-dim"),
]
for i, (col, lbl, sub) in enumerate(image_boxes):
    box3d(box_xs[i], IY, BW, BH, col, dx=DX, dy=DY, zo=5+i,
          label=lbl, sub=sub)
    if i < 3:
        arrow(box_xs[i]+BW+DX*0.4, IY+BH/2+DY*0.3,
              box_xs[i+1]-0.01, IY+BH/2,
              col=C_IMAGE, lw=1.4, ms=9)

# ── LLM Branch (y center = 1.475, box bottom = 0.70) ─────────────────────────
LY = 0.30 + (2.65 - 0.30)/2 - BH/2
llm_boxes = [
    (C_LLM, "PDG Slice",     "top-10 stmts"),
    (_dk(C_LLM, 0.82), "BPE Tokens",    "max 512"),
    (_dk(C_LLM, 0.67), "CodeBERT",      "RoBERTa-base"),
    (_dk(C_LLM, 0.55), "Linear\nProj.", "768 → 256"),
]
for i, (col, lbl, sub) in enumerate(llm_boxes):
    box3d(box_xs[i], LY, BW, BH, col, dx=DX, dy=DY, zo=5+i,
          label=lbl, sub=sub)
    if i < 3:
        arrow(box_xs[i]+BW+DX*0.4, LY+BH/2+DY*0.3,
              box_xs[i+1]-0.01, LY+BH/2,
              col=C_LLM, lw=1.4, ms=9)

# ── PDG → branch fork arrows ──────────────────────────────────────────────────
PDG_TIP = 4.22   # right edge of PDG box (approx 2.45+1.75+some)
for (y0, y1, col) in [
    (5.65, 8.25, C_GRAPH),
    (2.90, 5.40, C_IMAGE),
    (0.30, 2.65, C_LLM),
]:
    branch_y = (y0 + y1) / 2
    arrow(PDG_TIP, 3.9, box_xs[0] - 0.04, branch_y,
          col=col, lw=1.6, ms=11, rad=0.0)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT VECTORS + DIM TAGS
# ═══════════════════════════════════════════════════════════════════════════════
LAST_BOX_END = box_xs[3] + BW + DX + 0.05   # right edge of last 3D box
VEC_X  = LAST_BOX_END + 0.55
TAG_X  = VEC_X + 0.12

branch_ys = {
    "graph": (5.65 + 8.25) / 2,
    "image": (2.90 + 5.40) / 2,
    "llm":   (0.30 + 2.65) / 2,
}
vec_colors = {"graph": C_GRAPH, "image": C_IMAGE, "llm": C_LLM}
vec_labels = {"graph": "h_G ∈ ℝ²⁵⁶", "image": "h_I ∈ ℝ²⁵⁶", "llm": "h_L ∈ ℝ²⁵⁶"}

for branch, by in branch_ys.items():
    col = vec_colors[branch]
    arrow(box_xs[3]+BW+DX*0.4, by+BH/2-0.4,   # approximate center of last box
          VEC_X - 0.05, by,
          col=col, lw=1.5, ms=10)
    ax.text(TAG_X, by, vec_labels[branch],
            color=col, fontsize=8, fontweight="bold", ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                      edgecolor=col, linewidth=1.3), zorder=16)


# ═══════════════════════════════════════════════════════════════════════════════
# CONCATENATE BOX
# ═══════════════════════════════════════════════════════════════════════════════
CAT_X = TAG_X + 1.45
CAT_Y = 2.3
CAT_W = 1.55
CAT_H = 3.8

rbox(CAT_X, CAT_Y, CAT_W, CAT_H, "#FFEBEE", C_FUSION, lw=2.0, zo=4, rad=0.18)
txt(CAT_X + CAT_W/2, CAT_Y + CAT_H - 0.42, "Concat",    c=C_FUSION, fs=9.5, fw="bold")
txt(CAT_X + CAT_W/2, CAT_Y + CAT_H/2 + 0.05,
    "[h_G\n h_I\n h_L]", c=C_FUSION, fs=8.5, fw="bold")
txt(CAT_X + CAT_W/2, CAT_Y + 0.35, "∈ ℝ⁷⁶⁸", c=C_FUSION, fs=7.5)

for branch, by in branch_ys.items():
    col = vec_colors[branch]
    arrow(TAG_X + 1.35, by, CAT_X + 0.01, CAT_Y + CAT_H/2,
          col=col, lw=1.3, ms=9)


# ═══════════════════════════════════════════════════════════════════════════════
# MLP CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════
MLP_X = CAT_X + CAT_W + 0.7
MLP_Y = 3.2
MLP_W = 1.95
MLP_H = 2.5

box3d(MLP_X, MLP_Y, MLP_W, MLP_H, C_FUSION, dx=0.25, dy=0.16, zo=6,
      label="MLP", sub=None)
txt(MLP_X + MLP_W/2, MLP_Y + MLP_H/2 + 0.28, "MLP",       c="white", fs=10, fw="bold")
txt(MLP_X + MLP_W/2, MLP_Y + MLP_H/2 - 0.05, "768→256→1", c="white", fs=7.5)
txt(MLP_X + MLP_W/2, MLP_Y + MLP_H/2 - 0.38, "Sigmoid",   c="white", fs=7.0)

arrow(CAT_X + CAT_W, CAT_Y + CAT_H/2,
      MLP_X - 0.01, MLP_Y + MLP_H/2,
      col=C_FUSION, lw=2.2, ms=13)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT LABELS
# ═══════════════════════════════════════════════════════════════════════════════
OUT_X = MLP_X + MLP_W + DX + 0.55
MID_Y = MLP_Y + MLP_H/2

arrow(MLP_X + MLP_W + 0.25, MID_Y, OUT_X - 0.1, MID_Y + 1.0,
      col="#B71C1C", lw=1.8, ms=11)
arrow(MLP_X + MLP_W + 0.25, MID_Y, OUT_X - 0.1, MID_Y - 1.0,
      col="#1B5E20", lw=1.8, ms=11)

ax.text(OUT_X, MID_Y + 1.0, "Vulnerable",
        color="#B71C1C", fontsize=11, fontweight="bold", va="center", zorder=16)
ax.text(OUT_X, MID_Y - 1.0, "Safe",
        color="#1B5E20", fontsize=11, fontweight="bold", va="center", zorder=16)


# ── Save ──────────────────────────────────────────────────────────────────────
out = "docs/figures/fig1_architecture.png"
fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=C_BG)
print(f"Saved: {out}")
