"""Fig 5 (Slide 7) — Graph Branch: PDG structural features → GAT × 2 → h_G.
Run: python docs/figures/gen_fig05_graph_branch.py
Output: docs/figures/fig05_graph_branch.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt, new_canvas, box, title, save
from _figstyle import C_G, C_IN, BG_G
import matplotlib.patches as mpatches
import numpy as np

C_DATA = "#1565C0"
C_CTRL = "#E65100"
C_HDR  = "#1565C0"

fig, ax = new_canvas(14, 8.0)
title(ax, 7.0, 7.78, "Graph Branch — GAT learns structural vulnerability patterns from the PDG", fs=12.5)

# ── LEFT: labeled PDG graph ───────────────────────────────────────────────────
txt(ax, 2.4, 7.38, "Input PDG", ha="center", fontsize=10,
        fontweight="bold", color=C_G)
txt(ax, 2.4, 7.08, "node features: type bucket + in-deg + out-deg",
        ha="center", fontsize=7.5, color="#546E7A")

R = 0.46
nodes_L = {
    1: (1.2, 6.2, "1: int\nbuffer[10];"),
    2: (2.8, 5.2, "2: if (x>\n0&&x<20)"),
    3: (4.2, 6.1, "3: buf[x]\n= 0;"),
    4: (4.0, 3.8, "4: }"),
    5: (1.3, 3.6, "5: printf\n(buf[0])"),
}

def pedge(ax, nodes, src, dst, col, dashed=False, rad=0.12):
    x1, y1 = nodes[src][0], nodes[src][1]
    x2, y2 = nodes[dst][0], nodes[dst][1]
    ax.add_patch(mpatches.FancyArrowPatch(
        (x1,y1),(x2,y2), connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=11, color=col, lw=1.4,
        linestyle=(0,(5,3)) if dashed else "solid",
        shrinkA=31, shrinkB=31, zorder=5))

pedge(ax, nodes_L, 1, 2, C_DATA, rad= 0.08)
pedge(ax, nodes_L, 1, 3, C_DATA, rad=-0.20)
pedge(ax, nodes_L, 2, 3, C_DATA, rad=-0.10)
pedge(ax, nodes_L, 1, 5, C_DATA, rad= 0.15)
pedge(ax, nodes_L, 2, 5, C_DATA, rad= 0.10)
pedge(ax, nodes_L, 2, 4, C_CTRL, dashed=True, rad=0.14)

for nid, (nx, ny, lbl) in nodes_L.items():
    ax.add_patch(mpatches.Circle((nx,ny), R, facecolor="#EBF3FB",
                                 edgecolor=C_DATA, lw=1.7, zorder=6))
    txt(ax, nx, ny, lbl, ha="center", va="center",
            fontfamily="monospace", fontsize=5.8, color="#212121", zorder=7)

# structural feature chips near each node
feat_data = {
    1: (0.06,  6.7,  "type:5  indeg:0  outdeg:3"),
    2: (1.5,   4.52, "type:12  indeg:1  outdeg:3"),
    3: (4.1,   5.42, "type:7  indeg:2  outdeg:1"),
    4: (3.05,  3.28, "type:13  indeg:1  outdeg:0"),
    5: (0.06,  2.92, "type:3  indeg:2  outdeg:0"),
}
for nid, (fx, fy, ftxt) in feat_data.items():
    cw = len(ftxt)*0.062 + 0.12
    box(ax, fx, fy-0.13, cw, 0.27, BG_G, C_G, lw=0.8, rad=0.05, zo=7)
    txt(ax, fx+0.08, fy, ftxt, ha="left", va="center", fontsize=5.6, color=C_G)

# edge legend
for i, (col, ls, lbl) in enumerate([(C_DATA, "solid",    "data dep"),
                                     (C_CTRL, (0,(4,3)),  "ctrl dep")]):
    legy = 2.55 - i * 0.33
    ax.plot([0.25,0.75],[legy,legy], color=col, lw=1.5, linestyle=ls, zorder=9)
    ax.annotate("", xy=(0.77,legy), xytext=(0.58,legy),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2, mutation_scale=9))
    txt(ax, 0.82, legy, lbl, ha="left", va="center", fontsize=6.5, color=col)

# ── CENTER: GAT arrow ─────────────────────────────────────────────────────────
pts = np.array([[4.78,5.5],[5.38,5.5],[5.38,5.78],[5.92,5.25],
                [5.38,4.72],[5.38,5.0],[4.78,5.0]])
ax.fill(pts[:,0], pts[:,1], color=C_G, zorder=8, alpha=0.90)
txt(ax, 5.35, 5.25, "GAT\n×2", ha="center", va="center",
        fontsize=7.5, fontweight="bold", color="white")

# ── RIGHT: attention-weighted graph ───────────────────────────────────────────
txt(ax, 9.55, 7.38, "After GAT: attention-weighted updates",
        ha="center", fontsize=10, fontweight="bold", color=C_G)

nodes_R = {k: (v[0]+6.55, v[1], v[2]) for k, v in nodes_L.items()}

att_cfg = {
    (1,2): (0.42,  0.08,  C_DATA, False),
    (1,3): (0.18, -0.20,  C_DATA, False),
    (2,3): (0.31, -0.10,  C_DATA, False),
    (1,5): (0.22,  0.15,  C_DATA, False),
    (2,5): (0.35,  0.10,  C_DATA, False),
    (2,4): (0.28,  0.14,  C_CTRL, True),
}
for (s,d), (w, rad, col, dsh) in att_cfg.items():
    x1, y1 = nodes_R[s][0], nodes_R[s][1]
    x2, y2 = nodes_R[d][0], nodes_R[d][1]
    ax.add_patch(mpatches.FancyArrowPatch(
        (x1,y1),(x2,y2), connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=11,
        color=col, lw=1.0 + w*3.2, alpha=0.45 + w*0.55,
        linestyle=(0,(5,3)) if dsh else "solid",
        shrinkA=31, shrinkB=31, zorder=5))
    mx = (x1+x2)/2 + (0.08 if x2>x1 else -0.08)
    my = (y1+y2)/2 + 0.13
    txt(ax, mx, my, f"α={w:.2f}", ha="center", va="center", fontsize=5.4, color=col)

for nid, (nx, ny, lbl) in nodes_R.items():
    ax.add_patch(mpatches.Circle((nx,ny), R, facecolor="#EBF3FB",
                                 edgecolor=C_DATA, lw=1.7, zorder=6))
    txt(ax, nx, ny, lbl, ha="center", va="center",
            fontfamily="monospace", fontsize=5.8, color="#212121", zorder=7)

# attention pool → h_G output
ax.annotate("", xy=(12.35, 5.2), xytext=(11.1, 5.2),
            arrowprops=dict(arrowstyle="-|>", color=C_G, lw=1.8, mutation_scale=13))
txt(ax, 11.7, 5.45, "attn\npool", ha="center", va="center", fontsize=7.2, color=C_G)
box(ax, 12.4, 4.58, 1.35, 1.25, BG_G, C_G, lw=1.8, rad=0.12, zo=5)
txt(ax, 13.08, 5.38, "h_G",   ha="center", va="center", fontsize=11, fontweight="bold", color=C_G)
txt(ax, 13.08, 4.9,  "∈  ℝ²⁵⁶", ha="center", va="center", fontsize=8.5, color=C_G)

# ── BOTTOM: node feature table ────────────────────────────────────────────────
TX = 0.2; TW = 9.6; ROWY = 2.42; RH = 0.41
CWS     = [0.95, 3.0, 1.65, 1.0, 1.05, 1.95]
headers = ["Node", "Statement", "Type bucket", "In-deg", "Out-deg", "Centrality"]
rows    = [
    ("1", "int buffer[10];",            "Declaration (5)",  "0", "3", "0.20"),
    ("2", "if (x > 0 && x < 20) {",    "Control (12)",     "1", "3", "0.62"),
    ("3", "buffer[x] = 0;",            "Assignment (7)",   "2", "1", "0.41"),
    ("4", "}",                           "Ctrl-End (13)",    "1", "0", "0.15"),
    ("5", 'printf("%d", buffer[0]);',   "FuncCall (3)",     "2", "0", "0.31"),
]

hx = TX
for hdr, cw in zip(headers, CWS):
    box(ax, hx, ROWY-RH, cw, RH, C_HDR, C_HDR, lw=0, rad=0.0, zo=4)
    txt(ax, hx+cw/2, ROWY-RH/2, hdr, ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="white")
    hx += cw

for ri, row in enumerate(rows):
    ry = ROWY - RH*(ri+2)
    bg = "#F7F7F7" if ri%2==0 else "white"
    rx = TX
    for ci, (val, cw) in enumerate(zip(row, CWS)):
        box(ax, rx, ry, cw, RH, bg, "#CFD8DC", lw=0.6, rad=0.0, zo=4)
        txt(ax, rx+cw/2, ry+RH/2, val, ha="center", va="center", fontsize=7.0,
                fontfamily="monospace" if ci==1 else "DejaVu Sans", color="#212121")
        rx += cw

box(ax, TX, ROWY-RH*(len(rows)+1), TW, RH*(len(rows)+1),
        "none", "#90A4AE", lw=1.2, rad=0.04, zo=5)

save(fig, os.path.join(os.path.dirname(__file__), "fig05_graph_branch.png"))
