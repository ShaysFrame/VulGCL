"""Fig 4 (Slide 6) — Step 0: C function → Joern → Program Dependency Graph.
Run: python docs/figures/gen_fig04_pdg_extraction.py
Output: docs/figures/fig04_pdg_extraction.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import new_canvas, box, arrow, title, save, C_IN, C_BAD, BG_N
import matplotlib.patches as mpatches

fig, ax = new_canvas(12, 5.6)

# 1. C function
box(ax, 0.3, 1.4, 3.2, 3.2, "#ECEFF1", C_IN, lw=1.6)
txt(ax, 1.9, 4.35, "C / C++ Function", ha="center", va="center", fontsize=9.5,
        fontweight="bold", color=C_IN)
code = ["void foo(char *s,int n){", "  char buf[10];", "  int  l = strlen(s);",
        "  memcpy(buf, s, l);", "  return buf[n];", "}"]
for i, line in enumerate(code):
    vuln = "memcpy" in line
    txt(ax, 0.5, 3.95 - i * 0.42, line, fontfamily="monospace", fontsize=8,
            color=C_BAD if vuln else "#455A64",
            fontweight="bold" if vuln else "normal", va="center")

arrow(ax, 3.6, 3.0, 4.5, 3.0, col=C_IN)
txt(ax, 4.05, 3.25, "parse", ha="center", va="bottom", fontsize=7.5,
        fontweight="bold", color=C_IN)

# 2. Joern
box(ax, 4.6, 2.25, 2.3, 1.5, BG_N, C_IN, lw=1.5)
txt(ax, 5.75, 3.35, "Joern", ha="center", va="center", fontsize=9.5,
        fontweight="bold", color=C_IN)
txt(ax, 5.75, 2.95, "static analysis", ha="center", va="center", fontsize=7.5,
        color=C_IN)
txt(ax, 5.75, 2.6, "CPG → PDG (DOT)", ha="center", va="center", fontsize=7,
        color="#607D8B")
arrow(ax, 6.9, 3.0, 7.8, 3.0, col=C_IN)

# 3. PDG graph
box(ax, 7.9, 1.0, 3.8, 4.0, "#FAFAFA", C_IN, lw=1.6, rad=0.15, zo=2)
txt(ax, 9.8, 4.7, "Program Dependency Graph", ha="center", va="center",
        fontsize=9, fontweight="bold", color=C_IN)
nodes = {"s": (8.6, 4.0, "param s", False), "buf": (10.9, 4.0, "buf[10]", False),
         "l": (8.6, 2.9, "l=strlen", False), "mem": (9.8, 2.0, "memcpy", True),
         "ret": (10.9, 2.9, "return", False)}
edges = [("s", "l"), ("s", "mem"), ("l", "mem"), ("buf", "mem"), ("mem", "ret")]
for a, b in edges:
    arrow(ax, nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1],
          col="#90A4AE", lw=1.3, ms=9, rad=0.12)
for k, (x, y, lbl, vuln) in nodes.items():
    c = C_BAD if vuln else C_IN
    ax.add_patch(mpatches.Circle((x, y), 0.42,
                                 facecolor="#FFEBEE" if vuln else "#ECEFF1",
                                 edgecolor=c, lw=1.6, zorder=6))
    txt(ax, x, y, lbl, ha="center", va="center", fontsize=6.8,
            fontweight="bold" if vuln else "normal", color=c, zorder=7)
txt(ax, 9.8, 1.2, "nodes = statements   ·   edges = data dependencies",
        ha="center", va="center", fontsize=7, color="#607D8B")

title(ax, 6.0, 5.35,
      "Everything starts from the PDG — one graph feeds all three branches", fs=11)

save(fig, os.path.join(os.path.dirname(__file__), "fig04_pdg_extraction.png"))
