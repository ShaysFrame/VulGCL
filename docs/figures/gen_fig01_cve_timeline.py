"""Fig 1 (Slide 3) — The Problem: CVE growth + scale facts.
Run: python docs/figures/gen_fig01_cve_timeline.py
Output: docs/figures/fig01_cve_timeline.png
"""
import numpy as np
from _figstyle import new_canvas, box, title, save, C_F, C_IN, BG_N
from _figstyle import txt
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

# ── Editable data ─────────────────────────────────────────────────────────────
years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
cves = [6447, 14645, 16511, 17305, 18325, 20156, 25081, 28902, 40000, 48448]
facts = [
    "~70% of Microsoft & Chrome security bugs are memory-safety issues (C/C++)",
    "2026 already hit 29,609 CVEs in its first 6 months",
    "Manual review can't scale: the Linux kernel alone is 27M lines of C",
]

fig, ax = new_canvas(12, 6.4)

x0, x1, ybase, ytop = 1.0, 11.4, 1.6, 5.2
xs = np.linspace(x0, x1, len(years))
maxc = max(cves)
for xi, yr, c in zip(xs, years, cves):
    h = (c / maxc) * (ytop - ybase)
    col = C_F if yr == 2025 else C_IN
    box(ax, xi - 0.42, ybase, 0.84, h, col, col, lw=0, rad=0.04, zo=4)
    txt(ax, xi, ybase + h + 0.18, f"{c/1000:.0f}k", ha="center", va="bottom",
        fontsize=7.5, fontweight="bold", color=col)
    txt(ax, xi, ybase - 0.22, str(yr), ha="center", va="top", fontsize=7.5,
        color="#555")

txt(ax, x0 - 0.35, ytop + 0.15, "CVEs reported per year", ha="left",
    va="bottom", fontsize=9.5, fontweight="bold", color=C_IN)
txt(ax, x1, ybase + (ytop - ybase) * 0.55, "7× since 2016\n— accelerating",
    ha="right", va="center", fontsize=9, color=C_F, fontweight="bold")

box(ax, 0.7, 0.15, 10.6, 0.95, BG_N, C_IN, lw=1.2, rad=0.1, zo=2)
for i, f in enumerate(facts):
    txt(ax, 1.0, 0.92 - i * 0.30, "•  " + f, ha="left", va="center",
        fontsize=8.2, color="#37474F")

title(ax, 6.0, 6.15,
      "Undetected C/C++ vulnerabilities cause catastrophic real-world damage",
      fs=11.5)

save(fig, os.path.join(os.path.dirname(__file__), "fig01_cve_timeline.png"))
