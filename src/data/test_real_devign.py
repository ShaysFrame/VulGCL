"""Phase 3.2 — Test the full PDG pipeline on real Devign functions.

Picks one vulnerable and one safe function from data/devign/raw/train.jsonl,
runs them through all three data transforms, and saves a report + figures
inside the project.

Usage:
    python src/data/test_real_devign.py
"""

import json
import os
import sys
import time

sys.path.insert(0, ".")

import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.data.build_pdg import extract_pdg
from src.data.pdg_to_graph import pdg_to_pyg
from src.data.pdg_to_image import pdg_to_image

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TRAIN_FILE   = os.path.join(PROJECT_ROOT, "data", "devign", "raw", "train.jsonl")
FIGURES_DIR  = os.path.join(PROJECT_ROOT, "docs", "figures")
REPORT_PATH  = os.path.join(PROJECT_ROOT, "docs", "figures", "phase32_report.txt")
os.makedirs(FIGURES_DIR, exist_ok=True)

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def pick_samples(path: str, pool: int = 20):
    """
    Return up to `pool` candidates per class.
    Caller tries each in order and skips any that produce an empty PDG.
    """
    vulnerable, safe = [], []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            label = int(float(row["target"]))
            if label == 1 and len(vulnerable) < pool:
                vulnerable.append(row)
            elif label == 0 and len(safe) < pool:
                safe.append(row)
            if len(vulnerable) >= pool and len(safe) >= pool:
                break
    return vulnerable[:pool], safe[:pool]


def run_pipeline(row: dict, label: int, tag: str, report_lines: list):
    """Run one sample through the full pipeline. Append results to report_lines."""
    func_code = row["func"]
    project   = row.get("project", "unknown")
    commit    = row.get("commit_id", "unknown")[:8]

    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"Tag     : {tag}")
    report_lines.append(f"Label   : {'VULNERABLE' if label == 1 else 'SAFE'}")
    report_lines.append(f"Project : {project}  commit={commit}")
    report_lines.append(f"Lines   : {len(func_code.splitlines())}")
    report_lines.append(f"Chars   : {len(func_code)}")
    report_lines.append("Function (first 10 lines):")
    for ln in func_code.splitlines()[:10]:
        report_lines.append(f"  {ln}")
    if len(func_code.splitlines()) > 10:
        report_lines.append(f"  ... ({len(func_code.splitlines()) - 10} more lines)")

    # ── Step 1: PDG extraction ──────────────────────────────────────────────
    print(f"  [{tag}] Extracting PDG...")
    t0 = time.time()
    G = extract_pdg(func_code, project_name=f"devign_{tag}")
    pdg_time = time.time() - t0

    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    report_lines.append(f"\nPDG Extraction ({pdg_time:.1f}s):")
    report_lines.append(f"  Nodes : {n_nodes}")
    report_lines.append(f"  Edges : {n_edges}")
    if n_nodes == 0:
        report_lines.append("  WARNING: empty graph — Joern may not have parsed this function")
        print(f"  [{tag}] WARNING: empty PDG")
        return None, None

    # Print node list to report
    report_lines.append("  Node list:")
    for _, attr in list(G.nodes(data=True))[:15]:
        report_lines.append(
            f"    [{attr.get('type','?'):25s}] line={attr.get('line','?'):3}  "
            f"code={attr.get('code','')!r:.60}"
        )
    if n_nodes > 15:
        report_lines.append(f"    ... ({n_nodes - 15} more nodes)")

    # ── Step 2: PDG → PyG graph ────────────────────────────────────────────
    print(f"  [{tag}] Embedding with CodeBERT...")
    t0 = time.time()
    pyg_data = pdg_to_pyg(G, label=label, device=DEVICE)
    pyg_time = time.time() - t0

    report_lines.append(f"\nGraph Branch ({pyg_time:.1f}s):")
    report_lines.append(f"  x shape         : {list(pyg_data.x.shape)}  (nodes × 768)")
    report_lines.append(f"  edge_index shape: {list(pyg_data.edge_index.shape)}")
    report_lines.append(f"  y               : {pyg_data.y.item()}")
    report_lines.append(f"  x[0,:5]         : {pyg_data.x[0, :5].tolist()}")

    # ── Step 3: PDG → centrality image ────────────────────────────────────
    print(f"  [{tag}] Building centrality image...")
    t0 = time.time()
    img = pdg_to_image(G)
    img_time = time.time() - t0

    report_lines.append(f"\nImage Branch ({img_time:.1f}s):")
    report_lines.append(f"  Image shape     : {list(img.shape)}  (3 × 100 × 100)")
    for ch, name in enumerate(["Degree", "Katz", "Closeness"]):
        ch_data = img[ch]
        report_lines.append(
            f"  {name:10s}: min={ch_data.min():.3f}  "
            f"max={ch_data.max():.3f}  mean={ch_data.mean():.4f}"
        )

    return pyg_data, img


def find_parseable(candidates: list, label: int, tag: str, report_lines: list):
    """Try candidates in order, return first one Joern successfully parses."""
    for i, row in enumerate(candidates):
        print(f"  [{tag}] Trying candidate {i+1}/{len(candidates)}...")
        pyg_data, img = run_pipeline(row, label, tag, report_lines)
        if pyg_data is not None:
            return pyg_data, img
    print(f"  [{tag}] All candidates produced empty PDGs.")
    return None, None


def main():
    print(f"Device: {DEVICE}")
    print(f"Loading samples from {TRAIN_FILE}...")
    vulnerable, safe = pick_samples(TRAIN_FILE)

    report_lines = [
        "VulGCL Phase 3.2 — Real Devign Function Pipeline Test",
        f"Date   : 2026-06-05",
        f"Device : {DEVICE}",
    ]

    images = {}
    for candidates, label, tag in [(vulnerable, 1, "vuln"), (safe, 0, "safe")]:
        pyg_data, img = find_parseable(candidates, label, tag, report_lines)
        if img is not None:
            images[tag] = img

    # ── Save report ────────────────────────────────────────────────────────
    report_text = "\n".join(report_lines)
    with open(REPORT_PATH, "w") as f:
        f.write(report_text)
    print(f"\nReport saved → docs/figures/phase32_report.txt")
    print(report_text)

    # ── Save visualization ─────────────────────────────────────────────────
    if len(images) == 2:
        CHANNEL_NAMES = ["Degree", "Katz", "Closeness"]
        fig, axes = plt.subplots(2, 3, figsize=(12, 8))
        fig.suptitle("Real Devign Functions — PDG Centrality Images", fontsize=13)

        for row_idx, (tag, lbl) in enumerate([("vuln", "VULNERABLE"), ("safe", "SAFE")]):
            img = images[tag]
            for ch, cname in enumerate(CHANNEL_NAMES):
                ax = axes[row_idx, ch]
                ax.imshow(img[ch].numpy(), cmap="hot", vmin=0, vmax=1)
                ax.set_title(f"{lbl}\n{cname}")
                ax.axis("off")

        plt.tight_layout()
        fig_path = os.path.join(FIGURES_DIR, "phase32_real_devign_images.png")
        plt.savefig(fig_path, dpi=150)
        print(f"Figure saved → docs/figures/phase32_real_devign_images.png")


if __name__ == "__main__":
    main()
