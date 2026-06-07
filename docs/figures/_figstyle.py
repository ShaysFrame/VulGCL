"""Shared palette + helpers for VulGCL presentation figures.
Imported by the gen_*.py scripts so every figure matches the architecture diagram.
Edit the colors here once and regenerate all figures to restyle the whole deck.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Brand palette (matches gen_architecture.py) ───────────────────────────────
C_IN = "#37474F"   # input / joern / pdg
C_G  = "#1565C0"   # graph branch
C_I  = "#2E7D32"   # image branch
C_L  = "#6A1B9A"   # llm branch
C_F  = "#B71C1C"   # fusion
C_OK = "#1B5E20"   # safe / positive
C_BAD = "#C62828"  # vulnerable / negative

BG_G = "#E3F2FD"
BG_I = "#E8F5E9"
BG_L = "#F3E5F5"
BG_F = "#FFEBEE"
BG_N = "#ECEFF1"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size":   9,
})


def new_canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, fc, ec, lw=1.4, rad=0.12, zo=4):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={rad}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zo, clip_on=False))


def arrow(ax, x1, y1, x2, y2, col="#555", lw=1.8, ms=13, rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                mutation_scale=ms,
                                connectionstyle=f"arc3,rad={rad}"), zorder=12)


def txt(ax, *args, **kw):
    """ax.text but always above box fills/arrows (zorder 15 unless overridden)."""
    kw.setdefault("zorder", 15)
    return ax.text(*args, **kw)


def title(ax, x, y, text, fs=11):
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fs, fontweight="bold", color="#212121", zorder=16)


def save(fig, path, dpi=200):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"Saved: {path}")
