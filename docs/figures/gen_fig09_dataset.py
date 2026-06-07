"""Fig 9 (Slide 11) — Dataset & experimental setup (Devign).
Run: python docs/figures/gen_fig09_dataset.py
Output: docs/figures/fig09_dataset.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _figstyle import txt
from _figstyle import new_canvas, box, title, save, C_IN, C_G, C_BAD, C_OK, BG_N

# ── Editable data ─────────────────────────────────────────────────────────────
splits = [("Train", 21854), ("Validation", 2732), ("Test", 2732)]
vuln_ratio = 0.45
sources = ["FFmpeg", "QEMU", "LibTIFF", "VLC"]

fig, ax = new_canvas(12, 5.4)

# split bars
total = sum(n for _, n in splits)
txt(ax, 2.9, 4.5, "27,318 real C/C++ functions", ha="center", fontsize=10,
        fontweight="bold", color=C_IN)
y = 3.7
for name, n in splits:
    w = (n / total) * 5.2
    box(ax, 0.6, y - 0.28, w, 0.56, C_G, C_G, lw=0, rad=0.06, zo=4)
    txt(ax, 0.7, y, f"{name}", ha="left", va="center", fontsize=8,
            fontweight="bold", color="white")
    txt(ax, 0.6 + w + 0.15, y, f"{n:,}", ha="left", va="center", fontsize=8,
            color=C_IN)
    y -= 0.8

# class balance donut-ish bar
txt(ax, 9.0, 4.5, "Nearly balanced classes", ha="center", fontsize=10,
        fontweight="bold", color=C_IN)
bx, bw = 6.7, 4.4
box(ax, bx, 3.2, bw * vuln_ratio, 0.7, C_BAD, C_BAD, lw=0, rad=0.06, zo=4)
box(ax, bx + bw * vuln_ratio, 3.2, bw * (1 - vuln_ratio), 0.7, C_OK, C_OK,
    lw=0, rad=0.06, zo=4)
txt(ax, bx + bw * vuln_ratio / 2, 3.55, f"Vulnerable\n{int(vuln_ratio*100)}%",
        ha="center", va="center", fontsize=7.5, fontweight="bold", color="white")
txt(ax, bx + bw * vuln_ratio + bw * (1 - vuln_ratio) / 2, 3.55,
        f"Safe\n{int((1-vuln_ratio)*100)}%", ha="center", va="center",
        fontsize=7.5, fontweight="bold", color="white")
txt(ax, 9.0, 2.85, "→ no class weighting needed", ha="center", va="center",
        fontsize=7.5, color="#546E7A", style="italic")

# bottom strip: sources + setup
box(ax, 0.6, 0.4, 10.8, 1.6, BG_N, C_IN, lw=1.2, rad=0.1, zo=2)
txt(ax, 0.9, 1.65, "Source projects (all CVE-confirmed):", ha="left",
        va="center", fontsize=8.3, fontweight="bold", color=C_IN)
for i, s in enumerate(sources):
    box(ax, 0.9 + i * 1.5, 1.0, 1.3, 0.42, "white", C_IN, lw=1.1, rad=0.08, zo=3)
    txt(ax, 0.9 + i * 1.5 + 0.65, 1.21, s, ha="center", va="center",
            fontsize=7.5, color=C_IN)
txt(ax, 7.0, 1.55, "Training setup", ha="left", va="center", fontsize=8.3,
        fontweight="bold", color=C_IN)
for i, t in enumerate(["L20 GPU · fp16 mixed precision",
                       "AdamW · BCE loss · batch 16",
                       "val-tuned decision threshold"]):
    txt(ax, 7.0, 1.2 - i * 0.32, "•  " + t, ha="left", va="center",
            fontsize=7.3, color="#37474F")

title(ax, 6.0, 5.1,
      "Evaluated on Devign — 27,318 real C/C++ functions with confirmed CVEs",
      fs=11)

save(fig, os.path.join(os.path.dirname(__file__), "fig09_dataset.png"))
