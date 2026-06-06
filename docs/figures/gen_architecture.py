"""
Generate Figure 1: VulGCL Architecture — clean flat IEEE-style
Output: docs/figures/fig1_architecture.png
Run from project root: python docs/figures/gen_architecture.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe

# ── Canvas ────────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 18, 7.6
plt.rcParams.update({
    "font.family":  "DejaVu Sans",
    "font.size":    9,
})

C_IN     = "#37474F"   # input / joern / pdg
C_G      = "#1565C0"   # graph branch
C_I      = "#2E7D32"   # image branch
C_L      = "#6A1B9A"   # llm branch
C_F      = "#B71C1C"   # fusion

BG_G     = "#E3F2FD"
BG_I     = "#E8F5E9"
BG_L     = "#F3E5F5"
BG_F     = "#FFEBEE"

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")


# ── Helpers ───────────────────────────────────────────────────────────────────
def box(x, y, w, h, fc, ec, lw=1.4, rad=0.15, zo=4):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={rad}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zo,
        clip_on=False))

def label(x, y, top, bot=None, tc="white", fs=8.5, zo=10):
    if bot:
        ax.text(x, y + 0.14, top, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=tc, zorder=zo)
        ax.text(x, y - 0.18, bot, ha="center", va="center",
                fontsize=fs - 1.5, color=tc, alpha=0.90, zorder=zo)
    else:
        ax.text(x, y, top, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=tc, zorder=zo)

def arr(x1, y1, x2, y2, col="#555", lw=1.6, ms=12, rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                mutation_scale=ms,
                                connectionstyle=f"arc3,rad={rad}"),
                zorder=12)


# ═══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — C/C++ Function, Joern, PDG
# ═══════════════════════════════════════════════════════════════════════════════
# C/C++ function box
box(0.15, 4.1,  2.0, 3.1, "#ECEFF1", C_IN, lw=1.6)
ax.text(1.15, 6.90, "C / C++ Function", ha="center", va="center",
        fontsize=9.5, fontweight="bold", color=C_IN, zorder=10)
code_lines = [
    "void foo(char *s, int n) {",
    "  char buf[10];",
    "  int  l = strlen(s);",
    "  memcpy(buf, s, l);",   # vulnerable
    "  return buf[n];",
    "}",
]
for i, line in enumerate(code_lines):
    col = "#C62828" if "memcpy" in line else "#455A64"
    bold = "bold" if "memcpy" in line else "normal"
    ax.text(0.30, 6.45 - i * 0.37, line,
            fontfamily="monospace", fontsize=6.0, color=col,
            fontweight=bold, va="center", zorder=10)

# Arrow C → Joern
arr(1.15, 4.10, 1.15, 3.60, col=C_IN)

# Joern box
box(0.15, 2.25, 2.0, 1.30, "#ECEFF1", C_IN, lw=1.6)
label(1.15, 3.03, "Joern", "Static Analysis", tc=C_IN, fs=9)
ax.text(1.15, 2.52, "PDG Extraction  ·  DOT output",
        ha="center", va="center", fontsize=6.8, color=C_IN, zorder=10)

# Arrow Joern → PDG
arr(1.15, 2.25, 1.15, 1.82, col=C_IN)

# PDG box
box(0.15, 0.85, 2.0, 0.95, "#ECEFF1", C_IN, lw=1.6)
label(1.15, 1.32, "PDG", tc=C_IN, fs=10)
ax.text(1.15, 1.05, "Program Dependency Graph",
        ha="center", va="center", fontsize=6.8, color=C_IN, zorder=10)


# ═══════════════════════════════════════════════════════════════════════════════
# THREE BRANCH BACKGROUNDS
# ═══════════════════════════════════════════════════════════════════════════════
BRANCH_X0 = 2.55
BRANCH_X1 = 14.30

branch_bg = [
    (5.10, 7.55, BG_G, C_G, "Graph\nBranch"),
    (2.60, 5.00, BG_I, C_I, "Image\nBranch"),
    (0.10, 2.50, BG_L, C_L, "LLM\nBranch"),
]
for y0, y1, bg, ec, name in branch_bg:
    box(BRANCH_X0, y0, BRANCH_X1 - BRANCH_X0, y1 - y0,
        bg, ec, lw=1.0, rad=0.22, zo=1)
    ax.text(BRANCH_X0 - 0.08, (y0 + y1) / 2, name,
            ha="right", va="center", fontsize=8.5, fontweight="bold",
            color=ec, zorder=10, linespacing=1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# PDG → BRANCH FORK ARROWS
# ═══════════════════════════════════════════════════════════════════════════════
PDG_TIP_X = 2.18
PDG_MID_Y = 1.33
branch_mid_ys = [
    (5.10 + 7.55) / 2,   # graph
    (2.60 + 5.00) / 2,   # image
    (0.10 + 2.50) / 2,   # llm
]
for (_, _, _, ec, _), bmy in zip(branch_bg, branch_mid_ys):
    arr(PDG_TIP_X, PDG_MID_Y, BRANCH_X0 + 0.05, bmy, col=ec, lw=1.5, ms=10)


# ═══════════════════════════════════════════════════════════════════════════════
# PROCESSING BOXES INSIDE EACH BRANCH
# ═══════════════════════════════════════════════════════════════════════════════
BW   = 1.92   # box width
BH   = 1.58   # box height
GAP  = 0.38   # horizontal gap

box_xs = [BRANCH_X0 + 0.32 + i * (BW + GAP) for i in range(4)]

def branch_row(y0, y1, color, items):
    """Draw 4 processing boxes in a branch strip + inter-box arrows."""
    cy = (y0 + y1) / 2
    by = cy - BH / 2
    for i, (top, bot) in enumerate(items):
        fc = color
        # gradient: darken each successive box slightly
        import matplotlib.colors as mc
        rgb = mc.to_rgb(color)
        fade = tuple(min(1.0, c + (1 - c) * i * 0.18) for c in rgb)
        box(box_xs[i], by, BW, BH, fade, color, lw=1.3, zo=4)
        label(box_xs[i] + BW / 2, by + BH / 2, top, bot, tc="white", fs=8.5)
        if i < 3:
            arr(box_xs[i] + BW + 0.02, by + BH / 2,
                box_xs[i + 1] - 0.04, by + BH / 2,
                col=color, lw=1.5, ms=9)
    return by + BH / 2   # return y center of last box

graph_items = [
    ("CodeBERT", "node embed"),
    ("GAT Layer 1", "4 heads"),
    ("GAT Layer 2", "4 heads"),
    ("Mean Pool", "→ 256-dim"),
]
image_items = [
    ("3-ch Image", "100 × 100"),
    ("Conv 1–2", "ReLU + BN"),
    ("Conv 3–5", "ReLU + BN"),
    ("Avg Pool", "→ 256-dim"),
]
llm_items = [
    ("PDG Slice", "top-10 stmts"),
    ("BPE Tokens", "max 512"),
    ("CodeBERT", "RoBERTa-base"),
    ("Linear", "768 → 256"),
]

gy = branch_row(5.10, 7.55, C_G, graph_items)
iy = branch_row(2.60, 5.00, C_I, image_items)
ly = branch_row(0.10, 2.50, C_L, llm_items)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT VECTOR LABELS
# ═══════════════════════════════════════════════════════════════════════════════
VEC_X = box_xs[3] + BW + 0.18

for col, vy, lbl in [
    (C_G, gy, "h_G ∈ ℝ²⁵⁶"),
    (C_I, iy, "h_I ∈ ℝ²⁵⁶"),
    (C_L, ly, "h_L ∈ ℝ²⁵⁶"),
]:
    # arrow from last branch box to vector label
    arr(box_xs[3] + BW + 0.02, vy, VEC_X + 0.12, vy, col=col, lw=1.4, ms=9)
    ax.text(VEC_X + 0.15, vy, lbl,
            ha="left", va="center", fontsize=8.5, fontweight="bold", color=col,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=col, linewidth=1.2),
            zorder=14)


# ═══════════════════════════════════════════════════════════════════════════════
# CONCAT BOX
# ═══════════════════════════════════════════════════════════════════════════════
CAT_X = VEC_X + 1.52
CAT_W = 1.42
CAT_Y = 1.80
CAT_H = 3.80

box(CAT_X, CAT_Y, CAT_W, CAT_H, BG_F, C_F, lw=2.0, rad=0.18, zo=5)
ax.text(CAT_X + CAT_W / 2, CAT_Y + CAT_H - 0.38,
        "Concat", ha="center", va="center",
        fontsize=10, fontweight="bold", color=C_F, zorder=12)
ax.text(CAT_X + CAT_W / 2, CAT_Y + CAT_H / 2 + 0.12,
        "[ h_G\n  h_I\n  h_L ]",
        ha="center", va="center", fontsize=9.5, color=C_F,
        fontweight="bold", linespacing=1.7, zorder=12)
ax.text(CAT_X + CAT_W / 2, CAT_Y + 0.30,
        "∈ ℝ⁷⁶⁸", ha="center", va="center",
        fontsize=8, color=C_F, zorder=12)

for col, vy in [(C_G, gy), (C_I, iy), (C_L, ly)]:
    arr(VEC_X + 1.45, vy, CAT_X + 0.02, CAT_Y + CAT_H / 2,
        col=col, lw=1.3, ms=9)


# ═══════════════════════════════════════════════════════════════════════════════
# MLP CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════
MLP_X = CAT_X + CAT_W + 0.55
MLP_W = 1.85
MLP_Y = 2.55
MLP_H = 2.35

box(MLP_X, MLP_Y, MLP_W, MLP_H, C_F, C_F, lw=1.8, rad=0.18, zo=5)
label(MLP_X + MLP_W / 2, MLP_Y + MLP_H / 2 + 0.20,
      "MLP", "768 → 256 → 1", tc="white", fs=10)
ax.text(MLP_X + MLP_W / 2, MLP_Y + 0.35,
        "Sigmoid", ha="center", va="center",
        fontsize=8, color="white", alpha=0.90, zorder=12)

arr(CAT_X + CAT_W + 0.02, CAT_Y + CAT_H / 2,
    MLP_X - 0.02, MLP_Y + MLP_H / 2,
    col=C_F, lw=2.0, ms=13)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT LABELS
# ═══════════════════════════════════════════════════════════════════════════════
OUT_X  = MLP_X + MLP_W + 0.22
MID_Y  = MLP_Y + MLP_H / 2

arr(MLP_X + MLP_W + 0.02, MID_Y,
    OUT_X + 0.12, MID_Y + 1.10, col="#C62828", lw=1.8, ms=11)
arr(MLP_X + MLP_W + 0.02, MID_Y,
    OUT_X + 0.12, MID_Y - 1.10, col="#1B5E20", lw=1.8, ms=11)

ax.text(OUT_X + 0.15, MID_Y + 1.10, "Vulnerable",
        ha="left", va="center", fontsize=11, fontweight="bold",
        color="#C62828", zorder=14)
ax.text(OUT_X + 0.15, MID_Y - 1.10, "Safe",
        ha="left", va="center", fontsize=11, fontweight="bold",
        color="#1B5E20", zorder=14)


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE TITLE
# ═══════════════════════════════════════════════════════════════════════════════
ax.text(FIG_W / 2, 7.40,
        "Fig. 1. VulGCL: Three-Branch Multimodal Vulnerability Detection Framework",
        ha="center", va="center", fontsize=10.5, fontweight="bold",
        color="#212121", zorder=16)


# ── Save ──────────────────────────────────────────────────────────────────────
out = "docs/figures/fig1_architecture.png"
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved: {out}")
