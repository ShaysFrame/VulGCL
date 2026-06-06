# VulGCL Session Log

One entry per session. Most recent at the top.

---

## 2026-06-06 (continued)

### Coverage results & MAX_NODES fix

**measure_joern_coverage.py ran overnight on 200 Devign functions:**
- Empty PDG (Joern fail): 12/200 = 6.0%
- Node distribution: median=41, P90=223, P95=363, max=1444
- Timing: 13.9s/function → 105.8 hours for full dataset (confirms need for batch Joern)

**Critical fix: removed MAX_NODES=150 cutoff**
- Root cause of the transcode RAM crash was NOT the node count itself — it was calling
  CodeBERT with all 2067 nodes in a single batch
- Fix: both pdg_to_graph.py and pdg_to_image.py now embed nodes in batches of 64
  (~25MB per batch, flat regardless of function size)
- Usable fraction goes from 76.5% → 94.0% (only 6% excluded for empty PDG)
- Updated: paper_notes.md, paper_notes_joern_coverage.txt

---

## 2026-06-06

### What was done

**Studied VulCNN open-source code** at `/Users/shay/Dev/research/external/VulCNN`
- `ImageGeneration.py`: their image = centrality × sent2vec(statement) per node, not adjacency matrix
- `joern_graph_gen.py`: 2-step pipeline (joern-parse → joern-export), silent `except: pass` on failures
- Key finding: VulCNN never reports how many functions were excluded — a weakness we will improve on

**Rewrote `src/data/pdg_to_image.py`** to match VulCNN's construction, upgraded with CodeBERT:
- Old: adjacency matrix weighted by centrality (wrong — not what VulCNN does)
- New: centrality × CodeBERT embedding per node — rows=statements, cols=embedding dims
- Improvement over VulCNN: CodeBERT instead of sent2vec (richer semantic understanding of code)
- Added `MAX_NODES=150` — functions above this are truncated to avoid memory crash
  (the 1,763-line `transcode` function used 16GB RAM and took 22 min without this limit)
- `node_embeddings` parameter: pass pre-computed embeddings from graph branch to avoid
  running CodeBERT twice

**Real Devign test (Phase 3.2):**
- Vulnerable (FFmpeg r3d_read_rdvo, 62 nodes): all 3 branches ✅
- Safe (vdadec_init): empty PDG — Apple VDA SDK types unresolvable by Joern ⚠️
- Safe (transcode, 2067 nodes): worked but crashed RAM — triggers MAX_NODES filter ⚠️
- Conclusion: need to measure Joern parse failure rate across full dataset before preprocessing

### What is next
- Run updated `pdg_to_image.py` and verify new images look better
- Measure Joern parse failure rate on a 200-function sample
- Write `src/data/dataset.py` — VulDataset class tying all three branches together

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
