"""Fig 4 (Slide 6) — C source → Joern static analysis → PDG with data/ctrl dep edges.
Run: python docs/figures/gen_fig04_pdg_extraction.py
Output: docs/figures/fig04_pdg_extraction.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt, new_canvas, box, title, save
from _figstyle import C_IN, C_BAD
import matplotlib.patches as mpatches
import numpy as np

C_DATA = "#1565C0"   # solid blue  — data dependency
C_CTRL = "#E65100"   # dashed orange — control dependency
C_NODE_E = "#5B9BD5"
C_NODE_F = "#EBF3FB"
C_HDR    = "#4472C4"

fig, ax = new_canvas(14, 8.0)

title(ax, 7.0, 7.78, "Program Dependency Graph Construction", fs=13)

# ── LEFT: code panel ──────────────────────────────────────────────────────────
txt(ax, 2.25, 7.38, "Source C Code", ha="center", fontsize=10,
        fontweight="bold", color=C_IN)

box(ax, 0.2, 3.9, 4.1, 3.25, "#FAFAFA", "#90A4AE", lw=1.2, rad=0.1, zo=3)
# fake "title bar"
box(ax, 0.2, 6.85, 4.1, 0.3, "#B3C6E7", "#90A4AE", lw=0, rad=0.08, zo=4)

code_lines = [
    ("void vulnerable_fn(int x) {", False),
    ("    int buffer[10];",          False),
    ("    if (x > 0 && x < 20) {",  False),
    ("        buffer[x] = 0;",      True),
    ("    }",                        False),
    ('    printf("%d", buffer[0]);', False),
    ("}",                            False),
]
for i, (line, vuln) in enumerate(code_lines):
    y = 6.55 - i * 0.39
    if vuln:
        box(ax, 0.25, y - 0.17, 4.0, 0.34, "#FFEBEE", "#FFCDD2", lw=0, rad=0.02, zo=4)
    txt(ax, 0.38, y, line, ha="left", va="center",
            fontfamily="monospace", fontsize=7.7,
            color=C_BAD if vuln else "#212121",
            fontweight="bold" if vuln else "normal")
    if vuln:
        txt(ax, 2.55, y - 0.3, "← vulnerable line", ha="center", va="center",
                fontsize=6.5, color=C_BAD, style="italic")

# ── CENTER: chunky Joern arrow ────────────────────────────────────────────────
pts = np.array([[4.45,5.25],[5.15,5.25],[5.15,5.52],[5.72,5.0],
                [5.15,4.48],[5.15,4.75],[4.45,4.75]])
ax.fill(pts[:,0], pts[:,1], color="#4472C4", zorder=8, alpha=0.92)
txt(ax, 5.0, 5.0, "Joern\nStatic\nAnalysis", ha="center", va="center",
        fontsize=7.4, fontweight="bold", color="white")

# ── RIGHT: PDG graph ──────────────────────────────────────────────────────────
txt(ax, 10.1, 7.38, "Program Dependency Graph (PDG)", ha="center",
        fontsize=10, fontweight="bold", color=C_IN)

R = 0.50
nodes = {
    1: (6.9,  6.5, "1: int\nbuffer[10];"),
    2: (9.0,  5.35, "2: if (x >\n0 && x\n< 20) {"),
    3: (11.7, 6.25, "3:\nbuffer[x]\n= 0;"),
    4: (11.45, 4.15, "4: }"),
    5: (7.45,  3.9, "5: printf\n(\"%d\",\nbuffer[0]);"),
    6: (13.05, 4.5, "6: }"),
}

def edge(src, dst, col, dashed=False, rad=0.15, lbl=None, lx=None, ly=None):
    x1, y1 = nodes[src][0], nodes[src][1]
    x2, y2 = nodes[dst][0], nodes[dst][1]
    ls = (0, (5, 3)) if dashed else "solid"
    ax.add_patch(mpatches.FancyArrowPatch(
        (x1, y1), (x2, y2),
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=13,
        color=col, lw=1.5, linestyle=ls,
        shrinkA=34, shrinkB=34, zorder=5))
    if lbl and lx is not None:
        txt(ax, lx, ly, lbl, ha="center", va="center",
                fontsize=6.4, color=col, fontweight="bold")

# data dep (solid blue)
edge(1, 2, C_DATA, rad= 0.08, lbl="data dep", lx=7.75, ly=6.2)
edge(1, 3, C_DATA, rad=-0.22, lbl="data dep", lx=9.6,  ly=6.75)
edge(2, 3, C_DATA, rad=-0.1,  lbl="data dep", lx=10.6, ly=6.05)
edge(1, 5, C_DATA, rad= 0.18, lbl="data dep", lx=6.5,  ly=5.1)
edge(2, 5, C_DATA, rad= 0.1,  lbl="data dep", lx=7.95, ly=4.55)

# ctrl dep (dashed orange)
edge(2, 4, C_CTRL, dashed=True, rad= 0.15, lbl="ctrl dep", lx=10.5, ly=4.9)
edge(2, 5, C_CTRL, dashed=True, rad=-0.15, lbl="ctrl dep", lx=8.75, ly=4.45)
edge(4, 6, C_CTRL, dashed=True, rad= 0.1,  lbl="ctrl dep", lx=12.45, ly=4.55)

# draw circles on top of edges
for nid, (nx, ny, lbl) in nodes.items():
    ax.add_patch(mpatches.Circle((nx, ny), R,
                                 facecolor=C_NODE_F, edgecolor=C_NODE_E,
                                 lw=1.8, zorder=6))
    txt(ax, nx, ny, lbl, ha="center", va="center",
            fontfamily="monospace", fontsize=6.0, color="#212121", zorder=7)

# legend (top-right of graph area)
for i, (col, ls, lbl) in enumerate([
        (C_DATA, "solid",      "data dep"),
        (C_CTRL, (0,(4,3)),    "ctrl dep")]):
    ly = 7.1 - i * 0.38
    ax.plot([12.25, 12.8], [ly, ly], color=col, lw=1.8, linestyle=ls, zorder=9)
    ax.annotate("", xy=(12.82, ly), xytext=(12.62, ly),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.4,
                                mutation_scale=10), zorder=10)
    txt(ax, 12.9, ly, lbl, ha="left", va="center", fontsize=7.2, color=col)

# ── BOTTOM: Node table ────────────────────────────────────────────────────────
TX   = 5.85
TW   = 7.9
ROWY = 3.5
RH   = 0.46
CWS  = [0.75, 3.55, 3.6]     # Node ID | Statement | Type

headers = ["Node ID", "Statement", "Type"]
rows = [
    ("1", "int buffer[10];",             "Declaration"),
    ("2", "if (x > 0 && x < 20) {",      "Control (If)"),
    ("3", "buffer[x] = 0;",              "Assignment (Vulnerable)"),
    ("4", "}",                            "Control (End If)"),
    ("5", 'printf("%d", buffer[0]);',     "Function Call"),
    ("6", "}",                            "Control (End Function)"),
]

# header
hx = TX
for hdr, cw in zip(headers, CWS):
    box(ax, hx, ROWY - RH, cw, RH, C_HDR, C_HDR, lw=0, rad=0.0, zo=4)
    txt(ax, hx + cw/2, ROWY - RH/2, hdr, ha="center", va="center",
            fontsize=8, fontweight="bold", color="white")
    hx += cw

# data rows
for ri, (nid, stmt, ntype) in enumerate(rows):
    ry  = ROWY - RH * (ri + 2)
    bg  = "#FFEBEE" if "Vulnerable" in ntype else ("#F7F7F7" if ri % 2 == 0 else "white")
    rx  = TX
    for ci, (val, cw) in enumerate(zip([nid, stmt, ntype], CWS)):
        box(ax, rx, ry, cw, RH, bg, "#CFD8DC", lw=0.6, rad=0.0, zo=4)
        fc = C_BAD if ("Vulnerable" in ntype and ci == 2) else "#212121"
        fw = "bold" if ("Vulnerable" in ntype and ci == 2) else "normal"
        txt(ax, rx + cw/2, ry + RH/2, val, ha="center", va="center",
                fontsize=7.3,
                fontfamily="monospace" if ci == 1 else "DejaVu Sans",
                color=fc, fontweight=fw)
        rx += cw

# outer table border
box(ax, TX, ROWY - RH*(len(rows)+1), TW, RH*(len(rows)+1),
    "none", "#90A4AE", lw=1.2, rad=0.04, zo=5)

save(fig, os.path.join(os.path.dirname(__file__), "fig04_pdg_extraction.png"))
