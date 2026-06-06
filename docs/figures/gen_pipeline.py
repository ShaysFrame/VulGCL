"""
Generate Figure 2: PDG Extraction & Branch Pipeline
Output: docs/figures/fig2_pipeline.png
Run: python docs/figures/gen_pipeline.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

C_BG    = "#FAFAFA"
C_DARK  = "#37474F"
C_BLUE  = "#1565C0"
C_GREEN = "#2E7D32"
C_PURP  = "#6A1B9A"
C_GRAY  = "#78909C"
C_LBLU  = "#BBDEFB"
C_LGRN  = "#C8E6C9"
C_LPUR  = "#E1BEE7"
C_LGRY  = "#ECEFF1"

fig, axes = plt.subplots(1, 3, figsize=(15, 6.5))
fig.patch.set_facecolor(C_BG)
fig.suptitle("VulGCL — Data Preprocessing Pipeline",
             fontsize=13, fontweight="bold", color="#212121", y=1.01)

# ──────────────────────────────────────────────────────────────────────────────
# Panel A — PDG Extraction (Joern)
# ──────────────────────────────────────────────────────────────────────────────
ax = axes[0]
ax.set_facecolor(C_BG)
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.axis("off")
ax.set_title("(a)  PDG Extraction via Joern", fontsize=10, fontweight="bold",
             color=C_DARK, pad=8)

# Source code box
src_patch = FancyBboxPatch((0.3, 5.8), 9.4, 3.8,
                            boxstyle="round,pad=0,rounding_size=0.2",
                            facecolor=C_LGRY, edgecolor=C_DARK, linewidth=1.8)
ax.add_patch(src_patch)
ax.text(0.7, 9.3, "C Function (Source Code)", fontsize=8.5, fontweight="bold",
        color=C_DARK)

code = [
    ("1", "void bufferOverflow(char *src, int n) {"),
    ("2", "    char buf[10];"),
    ("3", "    int len = strlen(src);"),
    ("4", "    if (n > 0)"),
    ("5", "        memcpy(buf, src, len);   // ← vuln"),
    ("6", "    return;"),
    ("7", "}"),
]
highlight_line = 4  # 0-indexed → line 5
for i, (num, code_text) in enumerate(code):
    ypos = 8.95 - i * 0.43
    if i == highlight_line:
        ax.add_patch(FancyBboxPatch((0.35, ypos - 0.18), 9.3, 0.36,
                                    boxstyle="square,pad=0",
                                    facecolor="#FFCCBC", edgecolor="none"))
    ax.text(0.55, ypos, num, fontsize=6.5, color=C_GRAY,
            fontfamily="monospace", ha="right")
    ax.text(0.65, ypos, code_text, fontsize=6.5, color="#212121",
            fontfamily="monospace")

# Arrow
ax.annotate("", xy=(5.0, 4.7), xytext=(5.0, 5.75),
            arrowprops=dict(arrowstyle="-|>", color=C_DARK, lw=1.8,
                            mutation_scale=14))
ax.text(5.0, 5.25, "Joern\n(static analysis)", ha="center", fontsize=8,
        color=C_DARK, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                  edgecolor=C_DARK, linewidth=1))

# PDG graph
pdg_patch = FancyBboxPatch((0.3, 0.3), 9.4, 4.1,
                            boxstyle="round,pad=0,rounding_size=0.2",
                            facecolor=C_LGRY, edgecolor=C_DARK, linewidth=1.8)
ax.add_patch(pdg_patch)
ax.text(0.7, 4.15, "Program Dependency Graph (PDG)", fontsize=8.5,
        fontweight="bold", color=C_DARK)

# PDG nodes layout
node_info = [
    (2.0, 3.4, "char buf[10]"),
    (5.0, 3.4, "int len = strlen(src)"),
    (8.0, 3.4, "if (n > 0)"),
    (3.5, 2.1, "memcpy(buf,src,len)"),
    (6.5, 2.1, "return"),
    (5.0, 0.95, "bufferOverflow(...)"),
]
node_r = 0.42
pdg_edges = [(0,3),(1,3),(1,4),(2,3),(2,4),(5,0),(5,1),(5,2)]
node_colors = [C_LBLU]*3 + [C_LBLU]*2 + ["#FFCCBC"]

for (x, y, txt), col in zip(node_info, node_colors):
    ax.add_patch(plt.Circle((x, y), node_r, color=col,
                            linewidth=1.5, edgecolor=C_DARK, zorder=3))
    ax.text(x, y, txt, ha="center", va="center", fontsize=5.5,
            color=C_DARK, zorder=4, wrap=True)

edge_labels = ["data", "data", "ctrl", "ctrl", "ctrl", "ctrl", "ctrl", "ctrl"]
for (s, t), el in zip(pdg_edges, edge_labels):
    x1, y1, _ = node_info[s]; x2, y2, _ = node_info[t]
    ax.annotate("", xy=(x2, y2 + node_r * 0.8),
                xytext=(x1, y1 - node_r * 0.8),
                arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=0.9,
                                mutation_scale=7), zorder=2)

ax.text(9.5, 0.55, "●  data dep.\n●  ctrl dep.",
        ha="right", fontsize=6, color=C_GRAY)


# ──────────────────────────────────────────────────────────────────────────────
# Panel B — Graph & Image Branch
# ──────────────────────────────────────────────────────────────────────────────
ax = axes[1]
ax.set_facecolor(C_BG)
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.axis("off")
ax.set_title("(b)  Graph Branch & Image Branch", fontsize=10, fontweight="bold",
             color=C_DARK, pad=8)

# ── Graph branch ──────────────────────────────────────────────────────────────
gb = FancyBboxPatch((0.3, 5.4), 9.4, 4.2,
                    boxstyle="round,pad=0,rounding_size=0.2",
                    facecolor=C_LBLU, edgecolor=C_BLUE, linewidth=2)
ax.add_patch(gb)
ax.text(5.0, 9.3, "Graph Branch", ha="center", fontsize=9.5,
        fontweight="bold", color=C_BLUE)

# Mini GAT diagram
gat_nodes = [(1.5, 8.2),(3.0, 8.7),(3.0, 7.7),(4.5, 8.2),(6.0, 8.2)]
for x, y in gat_nodes:
    ax.add_patch(plt.Circle((x, y), 0.35, color="white",
                            edgecolor=C_BLUE, linewidth=1.5, zorder=3))
    ax.text(x, y, "v", ha="center", va="center", fontsize=7, color=C_BLUE, zorder=4)
for s, t in [(0,1),(0,2),(1,3),(2,3),(3,4)]:
    x1,y1 = gat_nodes[s]; x2,y2 = gat_nodes[t]
    ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle="-|>", color=C_BLUE, lw=1.0,
                                mutation_scale=7), zorder=2)
ax.text(1.5, 7.55, "CodeBERT\nnode features\n(768-dim)", ha="center",
        fontsize=6.5, color=C_BLUE)
ax.annotate("", xy=(6.8, 8.2), xytext=(6.35, 8.2),
            arrowprops=dict(arrowstyle="-|>", color=C_BLUE, lw=1.3,
                            mutation_scale=9))
ax.text(6.85, 8.2, "GAT\n(2 layers)", ha="left", va="center",
        fontsize=7, color=C_BLUE, fontweight="bold")
ax.text(6.85, 7.75, "α-weighted\naggregation", ha="left", va="center",
        fontsize=6.5, color=C_BLUE)

ax.annotate("", xy=(9.2, 8.2), xytext=(8.3, 8.2),
            arrowprops=dict(arrowstyle="-|>", color=C_BLUE, lw=1.3,
                            mutation_scale=9))
ax.text(9.25, 8.2, "mean\npool", ha="left", va="center", fontsize=7, color=C_BLUE)

ax.text(5.0, 5.75, "→  h_G ∈ ℝ²⁵⁶  (graph representation)", ha="center",
        fontsize=8, color=C_BLUE, fontweight="bold")

# ── Image branch ──────────────────────────────────────────────────────────────
ib = FancyBboxPatch((0.3, 0.5), 9.4, 4.5,
                    boxstyle="round,pad=0,rounding_size=0.2",
                    facecolor=C_LGRN, edgecolor=C_GREEN, linewidth=2)
ax.add_patch(ib)
ax.text(5.0, 4.75, "Image Branch", ha="center", fontsize=9.5,
        fontweight="bold", color=C_GREEN)

# Centrality image (fake heatmap)
img_ax = ax.inset_axes([0.05, 0.22, 0.28, 0.38])
rng = np.random.default_rng(42)
fake_img = rng.random((3, 30, 30))
fake_img[0] = np.clip(fake_img[0] * 1.4, 0, 1)  # degree channel
img_ax.imshow(fake_img.transpose(1,2,0), aspect="auto")
img_ax.set_xticks([]); img_ax.set_yticks([])
img_ax.set_title("3-ch\n100×100", fontsize=6, color=C_GREEN, pad=2)

ax.text(3.5, 3.85, "Channels:", fontsize=7, color=C_GREEN, fontweight="bold")
for i, ch in enumerate(["ch0: Degree centrality",
                         "ch1: Closeness centrality",
                         "ch2: Katz centrality"]):
    ax.text(3.5, 3.55 - i*0.28, f"• {ch}", fontsize=6.8, color=C_GREEN)

ax.text(3.5, 2.55, "5-layer CNN → GlobalAvgPool → Linear(256)",
        fontsize=7, color=C_GREEN, fontweight="bold")

ax.text(5.0, 0.85, "→  h_I ∈ ℝ²⁵⁶  (visual representation)", ha="center",
        fontsize=8, color=C_GREEN, fontweight="bold")


# ──────────────────────────────────────────────────────────────────────────────
# Panel C — LLM Branch + Fusion
# ──────────────────────────────────────────────────────────────────────────────
ax = axes[2]
ax.set_facecolor(C_BG)
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.axis("off")
ax.set_title("(c)  LLM Branch & Fusion", fontsize=10, fontweight="bold",
             color=C_DARK, pad=8)

# LLM branch
lb = FancyBboxPatch((0.3, 5.4), 9.4, 4.2,
                    boxstyle="round,pad=0,rounding_size=0.2",
                    facecolor=C_LPUR, edgecolor=C_PURP, linewidth=2)
ax.add_patch(lb)
ax.text(5.0, 9.3, "LLM Branch (CodeBERT)", ha="center", fontsize=9.5,
        fontweight="bold", color=C_PURP)

# Token row
tokens = ["<s>", "char", "buf", "[", "10", "]", ";", "memcpy", "...", "</s>"]
for i, tok in enumerate(tokens):
    xi = 0.55 + i * 0.93
    if xi > 9.5: break
    ax.add_patch(FancyBboxPatch((xi - 0.38, 8.35), 0.76, 0.45,
                                boxstyle="round,pad=0.05,rounding_size=0.08",
                                facecolor="white", edgecolor=C_PURP, linewidth=1))
    ax.text(xi, 8.57, tok, ha="center", va="center", fontsize=6, color=C_PURP)
ax.text(5.0, 8.15, "BPE Tokens (max_len=512)", ha="center", fontsize=7,
        color=C_PURP)

# Transformer layers
ax.annotate("", xy=(5.0, 7.6), xytext=(5.0, 8.1),
            arrowprops=dict(arrowstyle="-|>", color=C_PURP, lw=1.3,
                            mutation_scale=10))
ax.add_patch(FancyBboxPatch((1.0, 6.8), 8.0, 0.75,
                             boxstyle="round,pad=0.05,rounding_size=0.1",
                             facecolor="white", edgecolor=C_PURP, linewidth=1.5))
ax.text(5.0, 7.175, "CodeBERT  (RoBERTa-base, 12 layers, 768-dim)",
        ha="center", va="center", fontsize=7.5, color=C_PURP, fontweight="bold")

ax.annotate("", xy=(5.0, 6.55), xytext=(5.0, 6.8),
            arrowprops=dict(arrowstyle="-|>", color=C_PURP, lw=1.3,
                            mutation_scale=10))
ax.text(5.0, 6.4, "[CLS] token  →  768-dim  →  Linear(768→256)",
        ha="center", fontsize=7.5, color=C_PURP, fontweight="bold")
ax.text(5.0, 5.75, "→  h_L ∈ ℝ²⁵⁶  (semantic representation)", ha="center",
        fontsize=8, color=C_PURP, fontweight="bold")

# ── Fusion ────────────────────────────────────────────────────────────────────
C_RED = "#B71C1C"; C_LRED = "#FFCDD2"
fb = FancyBboxPatch((0.3, 0.5), 9.4, 4.5,
                    boxstyle="round,pad=0,rounding_size=0.2",
                    facecolor=C_LRED, edgecolor=C_RED, linewidth=2)
ax.add_patch(fb)
ax.text(5.0, 4.75, "Fusion & Classification", ha="center", fontsize=9.5,
        fontweight="bold", color=C_RED)

# Three h vectors → concat
for i, (tag, col) in enumerate(zip(["h_G (256)", "h_I (256)", "h_L (256)"],
                                    [C_BLUE, C_GREEN, C_PURP])):
    xi = 1.5 + i * 2.8
    ax.add_patch(FancyBboxPatch((xi - 0.8, 3.45), 1.6, 0.55,
                                boxstyle="round,pad=0.05,rounding_size=0.1",
                                facecolor="white", edgecolor=col, linewidth=1.8))
    ax.text(xi, 3.73, tag, ha="center", va="center", fontsize=8,
            color=col, fontweight="bold")
    ax.annotate("", xy=(5.0, 2.9), xytext=(xi, 3.45),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2,
                                mutation_scale=9,
                                connectionstyle="arc3,rad=0.0"), zorder=3)

ax.add_patch(FancyBboxPatch((1.8, 2.35), 6.4, 0.55,
                             boxstyle="round,pad=0.05,rounding_size=0.1",
                             facecolor="white", edgecolor=C_RED, linewidth=1.8))
ax.text(5.0, 2.625, "Concat  →  [h_G ; h_I ; h_L]  ∈  ℝ⁷⁶⁸",
        ha="center", va="center", fontsize=8, color=C_RED, fontweight="bold")

ax.annotate("", xy=(5.0, 2.05), xytext=(5.0, 2.35),
            arrowprops=dict(arrowstyle="-|>", color=C_RED, lw=1.5,
                            mutation_scale=11))

ax.add_patch(FancyBboxPatch((1.8, 1.5), 6.4, 0.55,
                             boxstyle="round,pad=0.05,rounding_size=0.1",
                             facecolor="white", edgecolor=C_RED, linewidth=1.8))
ax.text(5.0, 1.775, "MLP  (768 → 256 → 1)  +  Sigmoid",
        ha="center", va="center", fontsize=8, color=C_RED, fontweight="bold")

ax.annotate("", xy=(2.8, 0.88), xytext=(4.4, 1.5),
            arrowprops=dict(arrowstyle="-|>", color="#B71C1C", lw=1.3,
                            mutation_scale=10))
ax.annotate("", xy=(7.2, 0.88), xytext=(5.6, 1.5),
            arrowprops=dict(arrowstyle="-|>", color="#1B5E20", lw=1.3,
                            mutation_scale=10))

ax.text(2.2, 0.73, "Vulnerable", ha="center", fontsize=9, fontweight="bold",
        color="#B71C1C")
ax.text(7.8, 0.73, "Safe", ha="center", fontsize=9, fontweight="bold",
        color="#1B5E20")

# ── Save ──────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=1.2)
fig.savefig("docs/figures/fig2_pipeline.png", dpi=180,
            bbox_inches="tight", facecolor=C_BG)
print("Saved: docs/figures/fig2_pipeline.png")
