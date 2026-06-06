# VulGCL — Paper-Ready Notes

This file captures findings, decisions, and numbers that go directly into the paper.
Updated as experiments run. Every entry has a source so it can be verified.

---

## Dataset — Devign

| Item | Value | Source |
|------|-------|--------|
| Total functions | 27,318 | HuggingFace DetectVul/devign |
| Train | 21,854 | data/devign/raw/train.jsonl |
| Validation | 2,732 | data/devign/raw/validation.jsonl |
| Test | 2,732 | data/devign/raw/test.jsonl |
| Vulnerable (train) | ~45% | src/data/dataset_stats.py (TODO) |
| Safe (train) | ~55% | src/data/dataset_stats.py (TODO) |
| Label format | bool (False/True) → float(row['target']) | verified manually |

**Note for paper:** Dataset is nearly balanced — no class weighting needed.

---

## Data Filtering — Joern Parse Coverage

**To be filled after running `src/data/measure_joern_coverage.py` on 200 samples.**

| Item | Value | Source |
|------|-------|--------|
| Sample size | 200 (100 vuln + 100 safe) | measure_joern_coverage.py |
| Parse success rate | TODO | |
| Empty PDG rate | TODO | |
| Reason for failures | Platform-specific APIs (Apple VDA, etc.) | observed manually |
| MAX_NODES threshold | 150 | design decision |
| Functions excluded by MAX_NODES | TODO | |
| Final usable dataset size | TODO | |

**Note for paper (Threats to Validity):**
"We exclude functions for which Joern produced an empty CPG (X%) and functions
exceeding 150 PDG nodes (Y%). The latter produce near-zero centrality images due
to extreme graph sparsity (observed edge density < 0.1%) and require prohibitive
memory for CodeBERT batching. These exclusions introduce a selection bias toward
medium-complexity functions and constitute a threat to external validity."

---

## Design Decisions

### Why PDG over AST or CFG?
PDG captures both data and control dependencies simultaneously. A buffer overflow
(external input → unsafe memory operation with no bounds check) is directly
visible as a graph path in the PDG. AST captures only structure; CFG captures
only execution order. PDG is the most complete representation for taint-style
vulnerability analysis.
**Cite:** Yamaguchi et al. "Modeling and Discovering Vulnerabilities with Code
Property Graphs" (S&P 2014).

### Why GAT over GCN?
Vulnerability-relevant edges (e.g., user_input → strcpy) should dominate the
signal. GAT learns attention weights per edge so the model discovers which
dependency edges matter without hard-coding it.
**Cite:** Veličković et al. "Graph Attention Networks" (ICLR 2018).

### Why CodeBERT for the LLM branch?
CodeBERT is pretrained on 6M (code, documentation) pairs across 6 languages.
Its [CLS] token produces a 768-dim summary of the full function capturing
semantic meaning (e.g., recognises strcpy as unsafe, malloc/free pairing, etc.).
We use it at lower learning rate (2e-5) to fine-tune without destroying pretrained
weights.
**Cite:** Feng et al. "CodeBERT: A Pre-Trained Model for Programming and Natural
Languages" (EMNLP 2020).

### Why NOT GraphCodeBERT?
GraphCodeBERT encodes data flow graphs internally — this would overlap with our
explicit graph branch and make ablation results uninterpretable.

### Image branch — adapted from VulCNN
Construction: for each PDG node, centrality_score × CodeBERT_CLS(statement_code).
Stack all nodes → (N, 768) matrix per channel. 3 channels (degree, closeness, Katz).
Resize to (3, 100, 100). CNN classifies the resulting image.
We use CodeBERT instead of VulCNN's sent2vec because (a) no pretrained sent2vec
model is available for our corpus, and (b) CodeBERT is already loaded for the LLM
branch, avoiding an extra model dependency.
**Cite:** Wang et al. "VulCNN: An Image-inspired Scalable Vulnerability Detection
System" (ICSE 2022).

### Why late fusion (concatenation) not cross-modal attention?
Late fusion is simpler, interpretable, and allows clean ablation (remove one branch
at a time). Cross-modal attention (as in TMF-Net) creates inter-branch dependencies
that make ablation results harder to interpret. Acknowledged as future work.

### Learning rates
- CodeBERT branch: 2e-5 (pretrained — update carefully)
- Graph branch: 1e-4 (random init — learn fast)
- Image branch: 1e-4 (random init — learn fast)

### No node-count cutoff
We do not exclude functions by PDG size. The RAM issue observed with a 2,067-node
function was caused by batching all nodes into a single CodeBERT call. Fix: call
CodeBERT in batches of 64 nodes. Peak memory per batch = ~25MB, flat regardless
of function size. Coverage measurement confirmed Joern parses functions up to 1,444
nodes without issue.

---

## Novelty Claims (what makes VulGCL different)

| Claim | Evidence needed |
|-------|----------------|
| First to combine PDG-graph + centrality-image + LLM for C/C++ general vulnerability detection | Literature survey showing no prior work does all three |
| CodeBERT outperforms single-branch baselines | Ablation study results (Phase 8.3) |
| Edge deployment feasible (Raspberry Pi 4B) | Benchmark results (Phase 9) |

**What we do NOT claim as novel:**
- PDG-based graph analysis (prior: Devign, ReGVD)
- Centrality image construction (prior: VulCNN)
- CodeBERT for vulnerability detection (prior: LineVul, others)

The novelty is the **combination and the deployment**.

---

## Results Tables (to be filled)

### Baseline Run — CodeBERT LLM-only (2026-06-06)

**Config:** uniform lr=2e-5, linear warmup (1 epoch) + linear decay, early stop=6,
batch=32, fp16, 2×T4 GPU on Kaggle. Early stopping fired at epoch 11.

| Metric | Test set |
|--------|----------|
| F1 | **0.6148** |
| Accuracy | 0.6541 |
| Precision | 0.6294 |
| Recall | 0.6008 |
| AUC-ROC | 0.7333 |

**Source:** notebooks/VulGCL.ipynb → `/kaggle/working/test_results.json`

**Notes:**
- Previous run (no scheduler, 10× head LR): best val F1=0.5843 at epoch 2, fired at epoch 7
- Scheduler fix: +3 F1 points (+0.030), now stops at epoch 11
- Below LineVul (0.651) — expected, LineVul uses line-level attention on full context
- This is the "LLM branch only" row in Table 2 ablation and the "LLM-only baseline" line in Table 1

---

### Table 1 — Comparison with baselines on Devign

| Method | Accuracy | Precision | Recall | F1 | AUC |
|--------|----------|-----------|--------|----|-----|
| Flawfinder (static) | -- | -- | -- | -- | -- |
| Devign (GNN) | 0.619 | -- | -- | 0.549 | -- |
| VulCNN (image) | -- | -- | -- | ~0.58 | -- |
| IVDetect (GNN) | -- | -- | -- | 0.617 | -- |
| LineVul (CodeBERT) | -- | -- | -- | 0.651 | -- |
| **CodeBERT baseline (ours)** | 0.654 | 0.629 | 0.601 | **0.615** | 0.733 |
| **VulGCL full (ours)** | -- | -- | -- | -- | -- |

### Table 2 — Ablation study on Devign

| Variant | F1 | AUC |
|---------|----|----|
| Graph branch only | -- | -- |
| Image branch only | -- | -- |
| LLM branch only (= CodeBERT baseline) | **0.615** | **0.733** |
| Graph + Image | -- | -- |
| Graph + LLM | -- | -- |
| Image + LLM | -- | -- |
| **Full VulGCL** | -- | -- |

### Table 3 — Edge deployment (Raspberry Pi 4B)

| Model | Latency (ms) | RAM (MB) | F1 |
|-------|-------------|----------|----|
| VulGCL-Lite (int8 ONNX) | -- | -- | -- |

---

## Open Questions (to resolve during experiments)

1. What is the actual Joern parse failure rate on Devign? (run measure_joern_coverage.py)
2. What is the node count distribution? Is MAX_NODES=150 the right threshold?
3. Does CodeBERT for image branch help or hurt vs no embedding (pure centrality)?
4. What is the BigVul dataset size after filtering?
