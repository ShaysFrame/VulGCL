# VulGCL — Mid-term Presentation Outline
# Target: ~15 slides, ~15 minutes

---

## Slide 1 — Title

**Headline:** VulGCL: Multimodal Vulnerability Detection via Graph Neural Network, CNN, and Large Language Model Fusion

- Your name: Mohammad Mahafuj Rahman
- Supervisor: Prof. LiLi Bo
- Yangzhou University
- June 2026

**Visual:** University logo + dark background with subtle code/circuit pattern

---

## Slide 2 — Contents

**Headline:** Outline

1. The Problem
2. What Current Tools Miss
3. Our Solution
4. VulGCL In Depth
5. Results
6. Future Research

**Visual:** Clean numbered list with section icons or color blocks

---

# ══════════════════════════════════
# SECTION 1 — THE PROBLEM
# ══════════════════════════════════

## Slide 3 — The Problem

**Headline:** Undetected vulnerabilities in C/C++ code cause catastrophic real-world damage

- 25,226 new CVEs reported in 2023 — a 15% increase from 2022
- C/C++ accounts for ~70% of critical memory-safety vulnerabilities (Microsoft, Google data)
- Real examples: Heartbleed (OpenSSL), EternalBlue — all missed by automated tools
- Manual review cannot scale: Linux kernel alone has 27 million lines of C code

**Visual:** Timeline of famous C/C++ vulnerabilities with their cost/impact

---

# ══════════════════════════════════
# SECTION 2 — WHAT CURRENT TOOLS MISS
# ══════════════════════════════════

## Slide 4 — What Current Tools Miss

**Headline:** Every existing tool sees only one dimension of code — they miss the full picture

| Method | Type | Sees Semantics? | Sees Structure? | Sees Patterns? | Devign F1 |
|--------|------|:-:|:-:|:-:|:-:|
| Flawfinder | Rule-based | ❌ | ❌ | ❌ | ~0.20 |
| LineVul (Fu 2022) | LLM | ✅ | ❌ | ❌ | 0.651 |
| Devign / IVDetect | GNN | ❌ | ✅ | ❌ | 0.617 |
| VulCNN | CNN | ❌ | ❌ | ✅ | ~0.58 |
| **VulGCL (Ours)** | **Multimodal** | **✅** | **✅** | **✅** | **≥0.68** |

**Visual:** Highlight the VulGCL row in brand color — the only row with all ✅

---

# ══════════════════════════════════
# SECTION 3 — OUR SOLUTION
# ══════════════════════════════════

## Slide 5 — Our Solution: VulGCL

**Headline:** VulGCL unifies three independent views of the same function into one prediction

- One function → three representations → one fused decision
- Graph branch: captures HOW data flows between statements
- Image branch: captures WHICH statements are structurally central
- LLM branch: captures WHAT the most critical code semantically means
- All three views come from the same PDG — no redundancy

**Visual:** Full architecture diagram (docs/figures/fig1_architecture.png)

---

## Slide 6 — Step 0: Program Dependency Graph

**Headline:** Everything starts from the PDG — extracted by Joern, used by all three branches

- PDG nodes = individual statements
- PDG edges = data + control dependencies between statements
- Joern: industry-standard static analysis, handles real C/C++ (macros, typedefs, platform APIs)
- One PDG → feeds all three branches independently

**Visual:** C code snippet → Joern → PDG with labeled nodes and edges

---

# ══════════════════════════════════
# SECTION 4 — VULGCL IN DEPTH
# ══════════════════════════════════

## Slide 7 — Branch 1: Graph

**Headline:** Graph branch learns vulnerability patterns from data and control flow structure

- PDG → PyTorch Geometric graph
- Node features: CodeBERT [CLS] embedding per statement (768-dim)
- 2-layer GAT (Graph Attention Network) → learns which dependencies matter most
- Global mean pooling → h_G ∈ ℝ²⁵⁶

**Visual:** PDG graph with highlighted edges → GNN layers → pooled vector

---

## Slide 8 — Branch 2: Image

**Headline:** Image branch converts the PDG into a visual pattern a CNN can classify

- Each statement scored by 3 centrality metrics (degree, closeness, Katz)
- Score × CodeBERT embedding → 3-channel 100×100 image
- 5-layer CNN → h_I ∈ ℝ²⁵⁶
- Inspired by VulCNN — upgraded: sent2vec → CodeBERT (richer semantics)

**Visual:** PDG → centrality scores → 3-channel image → CNN output

---

## Slide 9 — Branch 3: LLM

**Headline:** LLM branch focuses CodeBERT on the most structurally critical statements

- PDG → rank statements by betweenness centrality → keep top-10
- Top-10 statements concatenated as a focused "slice" (≤ 512 tokens)
- CodeBERT (RoBERTa-base, pretrained on 6M code-comment pairs) fine-tuned end-to-end
- [CLS] → Linear(768 → 256) → h_L ∈ ℝ²⁵⁶
- Captures semantic meaning of where bugs actually live

**Visual:** PDG → betweenness ranking → top-10 slice → CodeBERT → output

---

## Slide 10 — Fusion

**Headline:** Three independent 256-dim signals are fused by a lightweight MLP

- Concatenate: [h_G ; h_I ; h_L] → 768-dim vector
- MLP: 768 → 256 → 1 + Sigmoid → P(vulnerable)
- Loss: Binary Cross-Entropy
- Optimizer: AdamW + linear warmup + cosine decay

**Visual:** 3 colored vectors → concat → MLP → probability bar

---

## Slide 11 — Dataset & Experimental Setup

**Headline:** We evaluate on Devign — 27,318 real C/C++ functions with confirmed CVEs

| | Train | Validation | Test |
|--|-------|-----------|------|
| Total functions | 21,854 | 2,732 | 2,732 |
| Vulnerable | ~45% | ~45% | ~45% |

- Source: FFmpeg, QEMU, LibTIFF, VLC — all CVE-confirmed
- Nearly balanced — no class weighting needed
- Training: Kaggle 2× T4 GPU, fp16 mixed precision, batch=32

---

# ══════════════════════════════════
# SECTION 5 — RESULTS
# ══════════════════════════════════

## Slide 12 — Results

**Headline:** LLM baseline done — preprocessing running — full results in 3 weeks

| Model | F1 | AUC | Status |
|-------|-----|-----|--------|
| LLM only (CodeBERT, ours) | **0.6148** | **0.7333** | ✅ Done |
| Graph only (GNN) | — | — | Queued |
| Image only (CNN) | — | — | Queued |
| **VulGCL (3-branch)** | **≥0.68** | **≥0.78** | Queued |

- Joern preprocessing running NOW: 27K functions → PDG graphs + images + LLM slices
- Full training begins this week after preprocessing completes

**Visual:** Learning curve — docs/figures/learning_curve_codebert.png

---

# ══════════════════════════════════
# SECTION 6 — FUTURE RESEARCH
# ══════════════════════════════════

## Slide 13 — Future Research

**Headline:** Three directions to extend this work after TIFS submission

1. **Cross-dataset generalization** — Evaluate on BigVul (188K functions, C/C++) and Devign-XL to test how well VulGCL transfers to unseen codebases

2. **Vulnerability type analysis** — Use saliency maps to explain which branch catches which bug class (buffer overflows vs. use-after-free vs. integer overflows)

3. **Community signals** — Integrate Stack Overflow code quality signals (accepted answers, security-flagged comments) as a fourth modality

**Visual:** Three icons: datasets → explanation → community, with short descriptions

---

# ══════════════════════════════════
# REFERENCE (NOT IN PRESENTATION)
# ══════════════════════════════════

## [Reference] Timeline

```
Week 1  (NOW)   Preprocessing complete + Phase 2 CodeBERT embed
Week 2          Graph-only + Image-only baselines on Kaggle
Week 3          Full VulGCL 3-branch training + ablation
Week 4          Results analysis + paper writing
Week 5          Write results + discussion sections
Week 6          Supervisor review + revision
Week 7          Submit to IEEE TIFS
```

**Three contributions:**
1. First framework fusing graph structural, visual, and PDG-guided semantic signals for C/C++ vuln detection
2. PDG-guided LLM slice: betweenness centrality focuses CodeBERT on where bugs live
3. VulCNN image branch upgraded with CodeBERT (sent2vec → 768-dim richer semantics)
