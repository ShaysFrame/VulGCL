# VulGCL Session Log

One entry per session. Most recent at the top.

---

## 2026-06-05

### What was done

**Phase 1 — Environment (completed earlier)**
- Python 3.12 venv, torch 2.12.0, PyG 2.7.0, MPS active on M1
- Joern installed via `brew install joern` (version HEAD+20260529-1450)

**Phase 2 — Devign dataset (completed earlier)**
- Downloaded via HuggingFace `DetectVul/devign`
- 21,854 train / 2,732 val / 2,732 test — saved to `data/devign/raw/`
- Labels: bool target, ~45% vulnerable (balanced — no class weighting needed)

**Phase 3 — PDG extraction pipeline (completed today)**

- `src/data/build_pdg.py` — runs Joern on a C function string, parses DOT output, returns networkx DiGraph
  - Fixed stdin-pipe bug: Joern needs a `.sc` file, not stdin heredoc
  - Fixed stub pollution: changed to `cpg.method.isNotStub` to exclude strcpy/operator stubs
  - Fixed bare-node crash: parse each digraph block separately, return the largest

- `src/data/pdg_to_graph.py` — converts networkx PDG → PyTorch Geometric Data object
  - Node features: CodeBERT [CLS] embedding of each statement (768-dim per node)
  - Tested on vulnerable (6 nodes, 9 edges) and safe (11 nodes, 17 edges) functions
  - Output: x shape [N, 768], edge_index shape [2, E], y = label

- `src/data/pdg_to_image.py` — converts networkx PDG → 3-channel centrality image
  - 3 channels: degree centrality, Katz centrality, closeness centrality
  - Builds N×N adjacency matrix weighted by centrality, then resizes to (3, 100, 100)
  - Tested and visualised: vulnerable/safe functions produce visually distinct heatmaps
  - Output saved to `docs/figures/pdg_centrality_images.png`

**Docs updated**
- `docs/1. concepts.md` Section 4 rewritten with full Joern DOT output walkthrough,
  ASCII PDG visualization, build_pdg.py step-by-step, and centrality image interpretation

### What was confirmed working
- Joern extracts PDG for a real C buffer-overflow function ✅
- Python parses the DOT output into a networkx graph ✅
- CodeBERT embeds each PDG node (statement → 768-dim vector) ✅
- Centrality image pipeline produces visually distinct vulnerable vs safe outputs ✅

### What is next
- Phase 3.2: Test the full pipeline on a real Devign function (not a hand-written toy)
- Phase 4: Write `src/data/dataset.py` — VulDataset class that ties all three branches together
- Phase 4: Write `src/data/preprocess.py` — batch-process all 27K Devign functions

---
