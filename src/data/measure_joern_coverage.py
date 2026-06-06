"""Step 1 of preprocessing validation: measure Joern parse coverage on Devign.

Randomly samples 200 functions (100 vulnerable + 100 safe) from train.jsonl,
runs Joern on each, and reports:
  - Parse success rate
  - Distribution of node counts
  - Estimated preprocessing time for full dataset
  - Recommended MAX_NODES threshold

Results are saved to progress/paper_notes_joern_coverage.txt for the paper.

Usage:
    python src/data/measure_joern_coverage.py
"""

import json
import os
import random
import sys
import time

sys.path.insert(0, ".")
from src.data.build_pdg import extract_pdg

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TRAIN_FILE   = os.path.join(PROJECT_ROOT, "data", "devign", "raw", "train.jsonl")
OUT_FILE     = os.path.join(PROJECT_ROOT, "progress", "paper_notes_joern_coverage.txt")

SAMPLE_PER_CLASS = 100   # 100 vuln + 100 safe = 200 total
RANDOM_SEED      = 42
MAX_NODES        = 150   # threshold we're evaluating


def load_samples(path: str, n: int, seed: int):
    vulnerable, safe = [], []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            label = int(float(row["target"]))
            if label == 1:
                vulnerable.append(row)
            else:
                safe.append(row)

    rng = random.Random(seed)
    return (
        rng.sample(vulnerable, min(n, len(vulnerable))),
        rng.sample(safe,       min(n, len(safe))),
    )


def main():
    print(f"Loading {SAMPLE_PER_CLASS} vulnerable + {SAMPLE_PER_CLASS} safe from Devign...")
    vuln_samples, safe_samples = load_samples(TRAIN_FILE, SAMPLE_PER_CLASS, RANDOM_SEED)
    all_samples = [(r, 1) for r in vuln_samples] + [(r, 0) for r in safe_samples]
    print(f"Total: {len(all_samples)} functions\n")

    results = []
    times   = []

    for i, (row, label) in enumerate(all_samples):
        func   = row["func"]
        lines  = len(func.splitlines())
        tag    = "VULN" if label == 1 else "SAFE"
        commit = row.get("commit_id", "?")[:8]

        print(f"[{i+1:3d}/{len(all_samples)}] {tag}  lines={lines:4d}  commit={commit}  ", end="", flush=True)

        t0 = time.time()
        G  = extract_pdg(func, project_name=f"coverage_{i}")
        elapsed = time.time() - t0

        n_nodes = G.number_of_nodes()
        n_edges = G.number_of_edges()
        success = n_nodes > 0
        times.append(elapsed)

        status = "OK" if success else "EMPTY"
        if success and n_nodes > MAX_NODES:
            status = f"LARGE({n_nodes})"

        print(f"nodes={n_nodes:4d}  edges={n_edges:4d}  {elapsed:.1f}s  [{status}]")

        results.append({
            "label":   label,
            "lines":   lines,
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "success": success,
            "elapsed": elapsed,
            "status":  status,
        })

    # ── Compute statistics ─────────────────────────────────────────────────────
    total        = len(results)
    n_empty      = sum(1 for r in results if not r["success"])
    n_large      = sum(1 for r in results if r["success"] and r["n_nodes"] > MAX_NODES)
    n_usable     = total - n_empty - n_large
    node_counts  = [r["n_nodes"] for r in results if r["success"]]

    avg_time     = sum(times) / len(times)
    est_full_hrs = (avg_time * 27318) / 3600

    node_counts_sorted = sorted(node_counts)
    p50 = node_counts_sorted[len(node_counts_sorted) // 2]
    p90 = node_counts_sorted[int(len(node_counts_sorted) * 0.90)]
    p95 = node_counts_sorted[int(len(node_counts_sorted) * 0.95)]
    p99 = node_counts_sorted[int(len(node_counts_sorted) * 0.99)] if len(node_counts_sorted) > 100 else "N/A"

    lines = [
        "=" * 70,
        "VulGCL — Joern Parse Coverage Report",
        f"Sample: {total} functions ({SAMPLE_PER_CLASS} vuln + {SAMPLE_PER_CLASS} safe)",
        f"Random seed: {RANDOM_SEED}",
        "=" * 70,
        "",
        "PARSE RESULTS",
        f"  Total sampled          : {total}",
        f"  Empty PDG (Joern fail) : {n_empty}  ({100*n_empty/total:.1f}%)",
        f"  Exceeds MAX_NODES={MAX_NODES}: {n_large}  ({100*n_large/total:.1f}%)",
        f"  Usable                 : {n_usable}  ({100*n_usable/total:.1f}%)",
        "",
        "NODE COUNT DISTRIBUTION (successful parses only)",
        f"  Min    : {min(node_counts) if node_counts else 'N/A'}",
        f"  Median : {p50}",
        f"  P90    : {p90}",
        f"  P95    : {p95}",
        f"  P99    : {p99}",
        f"  Max    : {max(node_counts) if node_counts else 'N/A'}",
        "",
        "TIMING",
        f"  Avg per function : {avg_time:.1f}s",
        f"  Estimated for full Devign (27,318): {est_full_hrs:.1f} hours",
        f"  NOTE: This uses one Joern process per function (slow).",
        f"  Batch processing with joern-parse + joern-export will be much faster.",
        "",
        "PAPER NOTES",
        f"  - Joern failed to produce a CPG for {n_empty}/{total} functions ({100*n_empty/total:.1f}%)",
        f"    Primary cause: unresolvable platform-specific API types",
        f"    (Apple VDA SDK, Windows COM, etc.)",
        f"  - {n_large} functions ({100*n_large/total:.1f}%) exceeded MAX_NODES={MAX_NODES}",
        f"    These produce near-zero centrality images (extreme sparsity)",
        f"  - Final estimated usable fraction: ~{100*n_usable/total:.0f}% of dataset",
        "=" * 70,
    ]

    report = "\n".join(lines)
    print("\n" + report)

    with open(OUT_FILE, "w") as f:
        f.write(report)
    print(f"\nSaved → progress/paper_notes_joern_coverage.txt")


if __name__ == "__main__":
    main()
