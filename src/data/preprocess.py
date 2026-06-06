"""
Batch-preprocess the Devign dataset → PyG graphs + centrality images.

Joern extraction pattern adapted from:
    VulCNN (Ma et al., ICSE 2022) — joern_graph_gen.py + ImageGeneration.py
    https://github.com/VulCNN/VulCNN

Improvements over VulCNN:
  * CodeBERT node embeddings instead of sent2vec
  * Embeddings shared between graph and image branches — CodeBERT runs ONCE
    per function (VulCNN runs it twice: once for graph, once for image)
  * Per-function resume (not per-run) — restart anytime without reprocessing
  * Proper error logging instead of silent except: pass
  * Structured output compatible with VulDataset mode='full'

Pipeline:
  Phase 1  CPU  multiprocessing  function text → Joern → networkx pickles
  Phase 2  GPU  single process   networkx → CodeBERT → PyG Data + image .pt

Usage:
    python src/data/preprocess.py                     # all splits, 4 workers
    python src/data/preprocess.py --workers 6
    python src/data/preprocess.py --split train --workers 4
    python src/data/preprocess.py --phase 2           # embed only (Joern done)

Output structure:
    data/devign/processed/
        train/00000.pt  00001.pt  ...    <- final output for VulDataset
        validation/...
        test/...
        graphs_nx/train/00000.pkl  ...  <- intermediate networkx pickles
        preprocess_log.json
"""

import argparse
import json
import os
import pickle
import shutil
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import torch
from tqdm import tqdm

# Ensure project root is on sys.path for worker processes too
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

DATA_RAW  = _PROJECT_ROOT / "data" / "devign" / "raw"
DATA_PROC = _PROJECT_ROOT / "data" / "devign" / "processed"

SPLITS = ["train", "validation", "test"]

# Joern creates a workspace per project under this path
_JOERN_WS = Path.home() / ".joern" / "workspace"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_split(split: str) -> list:
    path = DATA_RAW / f"{split}.jsonl"
    rows = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            rows.append({"func": r["func"], "label": int(r["target"])})
    return rows


def _worker_init():
    """Ensure imports work inside multiprocessing workers (Pool initializer)."""
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))


# ── Phase 1: Joern extraction (CPU, multiprocessing) ─────────────────────────
# Pattern from VulCNN joern_graph_gen.py Pool(n_workers).imap_unordered()
# Key difference: we use our extract_pdg() (.sc script approach) instead of
# VulCNN's joern-parse + joern-export CLI, because our approach correctly
# filters stubs via cpg.method.isNotStub and handles multi-block DOT output.

def _extract_one(args: tuple) -> tuple:
    """
    Worker: run Joern on one function, save networkx graph as pickle.
    Returns (idx, status_str).

    Status values mirror VulCNN's record_txt approach but per-function:
      'ok'       → PDG extracted and saved
      'empty'    → Joern ran but returned empty graph (platform-specific APIs)
      'skip'     → already done (resume)
      'skip_err' → previously failed (resume — don't retry broken functions)
      'error'    → unexpected exception
    """
    idx, func, label, split, pkl_dir = args

    # Ensure imports in worker process
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))
    from src.data.build_pdg import extract_pdg

    out_pkl  = Path(pkl_dir) / f"{idx:05d}.pkl"
    err_flag = Path(pkl_dir) / f"{idx:05d}.err"

    if out_pkl.exists():
        return idx, "skip"
    if err_flag.exists():
        return idx, "skip_err"

    # Unique project name → separate Joern workspace per function
    # This is the same strategy VulCNN uses with separate output dirs
    project_name = f"{split}_{idx}"

    try:
        G = extract_pdg(func, project_name=project_name)
        if G.number_of_nodes() == 0:
            err_flag.write_text("empty_pdg")
            return idx, "empty"
        with open(out_pkl, "wb") as f:
            pickle.dump({"graph": G, "label": label}, f)
        return idx, "ok"
    except Exception as e:
        err_flag.write_text(str(e))
        return idx, f"error"
    finally:
        # Clean up Joern workspace to keep disk usage low
        # (VulCNN never does this — workspaces accumulate indefinitely)
        ws = _JOERN_WS / project_name
        if ws.exists():
            shutil.rmtree(ws, ignore_errors=True)
        # Also check relative workspace (some Joern versions use ./workspace/)
        rel_ws = Path("workspace") / project_name
        if rel_ws.exists():
            shutil.rmtree(rel_ws, ignore_errors=True)


def phase1_extract(rows: list, split: str, pkl_dir: Path, n_workers: int) -> dict:
    """
    Run Joern on all functions in a split using multiprocessing.
    Adapted from VulCNN joern_graph_gen.py Pool(pool_num).map() pattern.
    """
    pkl_dir.mkdir(parents=True, exist_ok=True)

    args = [
        (idx, r["func"], r["label"], split, str(pkl_dir))
        for idx, r in enumerate(rows)
    ]

    counts = {"ok": 0, "empty": 0, "error": 0, "skip": 0, "skip_err": 0}

    print(f"\n[Phase 1] {split}  —  {len(args)} functions  |  {n_workers} workers")
    t0 = time.time()

    with Pool(n_workers, initializer=_worker_init) as pool:
        for _, status in tqdm(
            pool.imap_unordered(_extract_one, args),
            total=len(args),
            desc=f"  Joern/{split}",
        ):
            key = status if status in counts else "error"
            counts[key] = counts.get(key, 0) + 1

    elapsed = (time.time() - t0) / 60
    usable = counts["ok"] + counts["skip"]
    total  = len(args)
    print(f"  Finished in {elapsed:.1f} min")
    print(f"  ok={counts['ok']}  empty={counts['empty']}  "
          f"error={counts['error']}  skip={counts['skip']}  "
          f"skip_err={counts['skip_err']}")
    print(f"  Usable: {usable}/{total} = {usable/total*100:.1f}%")
    return counts


# ── Phase 2: CodeBERT embedding + save .pt (GPU, single process) ──────────────
# Key improvement over VulCNN ImageGeneration.py:
#   VulCNN runs sent2vec once per function for the image only.
#   We run CodeBERT ONCE and share the node embeddings between
#   the graph branch (pdg_to_pyg) and the image branch (pdg_to_image),
#   cutting GPU time roughly in half.

def phase2_embed(split: str, pkl_dir: Path, pt_dir: Path, device: str) -> dict:
    """
    Convert pickled networkx graphs → PyG Data + image tensors.
    Saves one .pt file per function: {graph, image, label, func_id, ...}
    """
    from src.data.pdg_to_graph import pdg_to_pyg, pdg_to_slice
    from src.data.pdg_to_image import pdg_to_image

    pt_dir.mkdir(parents=True, exist_ok=True)

    pkl_files = sorted(pkl_dir.glob("*.pkl"))
    print(f"\n[Phase 2] {split}  —  {len(pkl_files)} graphs  |  device={device}")

    ok = skip = err = 0
    t0 = time.time()

    for pkl_path in tqdm(pkl_files, desc=f"  Embed/{split}"):
        idx    = int(pkl_path.stem)
        pt_out = pt_dir / f"{idx:05d}.pt"

        if pt_out.exists():
            skip += 1
            continue

        try:
            with open(pkl_path, "rb") as f:
                obj = pickle.load(f)
            G, label = obj["graph"], obj["label"]

            # Graph branch: CodeBERT embeds each PDG node → data.x shape (N, 768)
            data = pdg_to_pyg(G, label=label, device=device)

            # Image branch: reuses data.x — no second CodeBERT pass
            img = pdg_to_image(G, node_embeddings=data.x, device=device)

            # LLM branch: top-10 statements by betweenness centrality as text
            # Independent modality — semantic meaning of the most critical code
            llm_slice = pdg_to_slice(G, top_k=10)

            torch.save({
                "graph":     data,
                "image":     img,
                "llm_slice": llm_slice,
                "label":     float(label),
                "func_id":   idx,
                "num_nodes": G.number_of_nodes(),
                "num_edges": G.number_of_edges(),
            }, pt_out)
            ok += 1

        except Exception as e:
            err += 1
            tqdm.write(f"  [embed error] {split}/{idx}: {e}")

    elapsed = (time.time() - t0) / 60
    print(f"  Finished in {elapsed:.1f} min  —  ok={ok}  skip={skip}  err={err}")
    return {"ok": ok, "skip": skip, "err": err}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Preprocess Devign → PDG graphs + centrality images"
    )
    parser.add_argument(
        "--workers", type=int, default=4,
        help="Parallel Joern workers for Phase 1 (default: 4)"
    )
    parser.add_argument(
        "--split", type=str, default=None,
        choices=["train", "validation", "test"],
        help="Process one split only (default: all three)"
    )
    parser.add_argument(
        "--phase", type=int, default=0, choices=[0, 1, 2],
        help="0=both phases  1=Joern only  2=embed only (default: 0)"
    )
    args = parser.parse_args()

    splits = [args.split] if args.split else SPLITS
    device = (
        "mps"  if torch.backends.mps.is_available() else
        "cuda" if torch.cuda.is_available()         else
        "cpu"
    )

    print("=" * 60)
    print("VulGCL Preprocessing")
    print("=" * 60)
    print(f"Device  : {device}")
    print(f"Splits  : {splits}")
    print(f"Workers : {args.workers}  (Phase 1 only — Phase 2 is GPU-only)")
    print(f"Phase   : {args.phase}  (0=both, 1=Joern, 2=embed)")
    print(f"Output  : {DATA_PROC}")
    print("=" * 60)

    log = {}

    for split in splits:
        rows    = _load_split(split)
        pkl_dir = DATA_PROC / "graphs_nx" / split
        pt_dir  = DATA_PROC / split

        print(f"\n{'─'*60}")
        print(f"  {split.upper()}  ({len(rows)} functions)")
        print(f"{'─'*60}")

        if args.phase in (0, 1):
            counts = phase1_extract(rows, split, pkl_dir, args.workers)
            log[f"{split}_phase1"] = counts

        if args.phase in (0, 2):
            counts = phase2_embed(split, pkl_dir, pt_dir, device)
            log[f"{split}_phase2"] = counts

    DATA_PROC.mkdir(parents=True, exist_ok=True)
    log_path = DATA_PROC / "preprocess_log.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    print(f"\nLog saved → {log_path}")
    print("\nNext step:")
    print("  Update src/data/dataset.py to load mode='full' from processed/*.pt")


if __name__ == "__main__":
    main()
