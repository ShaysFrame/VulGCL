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

- 48,448 CVEs reported in 2025 — and 2026 has already hit 29,609 in just 6 months (source: CVEdetails.com)
- CVE volume has grown 7× since 2016 — the problem is accelerating, not slowing down
- ~70% of Microsoft's CVEs and ~70% of Chrome's security bugs are memory safety issues — both written in C/C++ (Microsoft Security Response Center 2019; Google Project Zero 2020)
- Real examples: Heartbleed (OpenSSL), EternalBlue — all missed by automated tools
- Manual review cannot scale: Linux kernel alone has 27 million lines of C code

**Visual:** `docs/figures/fig01_cve_timeline.png` — CVE growth + scale facts

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
| VulCNN | CNN | ❌ | ❌ | ✅ | 0.638 |
| **VulGCL (Ours)** | **Multimodal** | **✅** | **✅** | **✅** | **0.6533 F1 / 0.6693 AUC** |

**Visual:** `docs/figures/fig02_method_comparison.png` — capability matrix, VulGCL row highlighted

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

**Visual:** `docs/figures/fig03_architecture.png` — full 3-branch + gated fusion architecture

---

## Slide 6 — Step 0: Program Dependency Graph

**Headline:** Everything starts from the PDG — extracted by Joern, used by all three branches

- PDG nodes = individual statements
- PDG edges = data + control dependencies between statements
- Joern: industry-standard static analysis, handles real C/C++ (macros, typedefs, platform APIs)
- One PDG → feeds all three branches independently

**Visual:** `docs/figures/fig04_pdg_extraction.png` — C code → Joern → PDG

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

**Visual:** `docs/figures/fig05_graph_branch.png` — PDG → GAT → attention pool

---

## Slide 8 — Branch 2: Image

**Headline:** Image branch converts the PDG into a visual pattern a CNN can classify

- Each statement scored by 3 centrality metrics (degree, closeness, Katz)
- Score × CodeBERT embedding → 3-channel 100×100 image
- 5-layer CNN → h_I ∈ ℝ²⁵⁶
- Inspired by VulCNN — upgraded: sent2vec → CodeBERT (richer semantics)

**Visual:** `docs/figures/fig06_image_branch.png` — centrality × embedding → CNN

---

## Slide 9 — Branch 3: LLM

**Headline:** LLM branch focuses CodeBERT on the most structurally critical statements

- PDG → rank statements by betweenness centrality → keep top-10
- Top-10 statements concatenated as a focused "slice" (≤ 512 tokens)
- CodeBERT (RoBERTa-base, pretrained on 6M code-comment pairs) fine-tuned end-to-end
- [CLS] → Linear(768 → 256) → h_L ∈ ℝ²⁵⁶
- Captures semantic meaning of where bugs actually live

**Visual:** `docs/figures/fig07_llm_branch.png` — betweenness slice → CodeBERT

---

## Slide 10 — Fusion

**Headline:** Three independent 256-dim signals are fused by a lightweight MLP

- Concatenate: [h_G ; h_I ; h_L] → 768-dim vector
- MLP: 768 → 256 → 1 + Sigmoid → P(vulnerable)
- Loss: Binary Cross-Entropy
- Optimizer: AdamW + linear warmup + cosine decay

**Visual:** `docs/figures/fig08_fusion.png` — gated fusion → MLP → P(vuln)

---

## Slide 11 — Dataset & Experimental Setup

**Headline:** We evaluate on Devign — 27,318 real C/C++ functions labelled from security fix commits

| | Train | Validation | Test |
|--|-------|-----------|------|
| Total functions | 21,854 | 2,732 | 2,732 |
| Vulnerable | ~45% | ~45% | ~45% |

- Source: FFmpeg, QEMU, LibTIFF, VLC — labels from security-commit history
- Nearly balanced — no class weighting needed
- Training: NVIDIA L20 GPU (Aliyun), fp16 mixed precision, batch=32

---

# ══════════════════════════════════
# SECTION 5 — RESULTS
# ══════════════════════════════════

## Slide 12 — Results

**Headline:** VulGCL outperforms all published baselines on F1; fusion wins on AUC

**Table 1 — vs Published Baselines (F1)**

| Model | F1 |
|-------|----|
| Devign model | 0.572 |
| IVDetect | 0.617 |
| VulCNN | 0.638 |
| LineVul | 0.651 |
| **VulGCL (Ours)** | **0.653** |

**Table 2 — Ablation: F1 vs AUC**

| Model | F1 | AUC |
|-------|----|-----|
| Graph only | 0.630 | 0.573 |
| Image only | 0.625 | 0.572 |
| LLM only | **0.663** | 0.659 |
| **VulGCL (full)** | 0.653 | **0.669** |

- **Key message:** VulGCL is #1 on F1 against all published baselines. On AUC (threshold-independent), VulGCL beats every single branch — fusion adds +1.07pp over the strongest branch (LLM only).

**Visual:** `docs/figures/fig10_results.png` — F1 + AUC per ablation variant

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
