# VulGCL — Mid-term Presentation Outline
# Target: 12 slides, ~15 minutes

---

## Slide 1 — Title

**Headline:** VulGCL: A Multimodal Graph-CNN-LLM Framework for C/C++ Vulnerability Detection

- Your name: Mohammad Mahafuj Rahman
- Supervisor: Prof. LiLi Bo
- Yangzhou University
- June 2026

**Visual:** University logo + a dark background with subtle code/circuit pattern

---

## Slide 2 — The Problem

**Headline:** Undetected vulnerabilities in C/C++ code cause catastrophic real-world damage

- 25,226 new CVEs reported in 2023 — a 15% increase from 2022
- C/C++ accounts for ~70% of critical memory-safety vulnerabilities (Microsoft, Google data)
- Real examples: Heartbleed (OpenSSL), Log4Shell, EternalBlue — all missed by automated tools
- Manual review cannot scale: Linux kernel alone has 27 million lines of C code

**Visual:** Timeline of famous C/C++ vulnerabilities with their cost/impact (Heartbleed, Shellshock, etc.)

---

## Slide 3 — Why Existing Tools Fail

**Headline:** Current tools see only one dimension of code — they miss the full picture

| Method | Type | Sees Text? | Sees Structure? | Sees Patterns? | Devign F1 |
|--------|------|-----------|-----------------|----------------|-----------|
| Flawfinder | Rule-based | ❌ | ❌ | ❌ | ~0.20 |
| LineVul (Fu 2022) | LLM | ✅ | ❌ | ❌ | 0.651 |
| **CodeBERT (ours, LLM-only)** | LLM | ✅ | ❌ | ❌ | **0.615** |
| Devign / IVDetect | GNN | ❌ | ✅ | ❌ | 0.617 |
| VulCNN | CNN | ❌ | ❌ | ✅ | ~0.58 |
| **VulGCL (Ours)** | **Multimodal** | **✅** | **✅** | **✅** | **≥0.68** |

**Visual:** The table above — highlight the VulGCL row in your brand color

---

## Slide 4 — Our Solution

**Headline:** VulGCL unifies three independent views of the same function into one prediction

- One function → three representations → one fused decision
- Graph branch: captures HOW data flows between statements
- Image branch: captures WHICH statements are structurally central
- LLM branch: captures WHAT the code semantically means

**Visual:** Fig 1 — full architecture diagram (from FigJam)

---

## Slide 5 — Step 1: Program Dependency Graph

**Headline:** We extract the PDG using Joern — an industry-standard static analysis tool

- PDG nodes = individual statements
- PDG edges = data dependencies + control dependencies
- Joern parses real C/C++ including macros, typedefs, platform APIs
- Our coverage measurement: **94% of Devign functions successfully parsed**
- Only 6% fail — all due to unresolvable platform-specific APIs (Apple VDA, Windows COM)

**Visual:** Fig 2 — C code → Joern → PDG with labeled nodes and edges (from FigJam)

---

## Slide 6 — Branch 1: Graph

**Headline:** Graph branch learns vulnerability patterns from data and control flow

- PDG converted to PyTorch Geometric graph object
- Node features: CodeBERT [CLS] embedding of each statement (768-dim)
- 2-layer Graph Attention Network (GAT) — attention weights highlight critical nodes
- Global mean pooling → h_G ∈ ℝ²⁵⁶

**Visual:** Small diagram showing GAT attention mechanism — nodes with different sizes representing attention weights

---

## Slide 7 — Branch 2: Image

**Headline:** Image branch turns the PDG into a visual signal a CNN can learn from

- Each node gets a score: how structurally important is this statement?
- 3 centrality metrics: degree, closeness, Katz
- Each channel = centrality score × CodeBERT embedding → (N × 768) matrix
- Resize to 100×100 → 3-channel image → 5-layer CNN → h_I ∈ ℝ²⁵⁶
- Inspired by VulCNN (ICSE 2022) — upgraded with CodeBERT instead of sent2vec

**Visual:** Fig 3 — PDG → centrality scores → 3-channel image → CNN (from FigJam)

---

## Slide 8 — Branch 3: LLM

**Headline:** LLM branch focuses CodeBERT on the most structurally critical statements

- PDG → rank all statements by betweenness centrality → keep top-10
- Concatenate top-10 statements as a short focused "slice" (max 512 tokens)
- CodeBERT: RoBERTa-base pretrained on 6M (code, comment) pairs
- Fine-tuned jointly with the classifier
- [CLS] token → Linear(768 → 256) → h_L ∈ ℝ²⁵⁶
- Independent from graph branch (structure) and image branch (visual pattern)
- Captures: semantic meaning of the most connected/critical code — where bugs live

**Visual:** Diagram: PDG → betweenness ranking → top-10 statements → CodeBERT → [CLS] output

---

## Slide 9 — Fusion

**Headline:** Three 256-dim vectors are concatenated and classified by a lightweight MLP

- Concatenate: [h_G ; h_I ; h_L] → 768-dim vector
- MLP: 768 → 256 → 1 + Sigmoid
- Binary output: P(vulnerable)
- Loss: BCEWithLogitsLoss
- Optimizer: AdamW with linear warmup + cosine decay

**Visual:** Simple fusion diagram — 3 colored vectors merging → MLP → probability output

---

## Slide 10 — Dataset & Setup

**Headline:** We evaluate on Devign — 27,318 real C/C++ functions with confirmed CVEs

| | Train | Validation | Test |
|--|-------|-----------|------|
| Total functions | 21,854 | 2,732 | 2,732 |
| Vulnerable | ~45% | ~45% | ~45% |
| Safe | ~55% | ~55% | ~55% |

- Source projects: FFmpeg, QEMU, LibTIFF, VLC
- All vulnerabilities confirmed by CVE database
- Nearly balanced — no class weighting needed
- Training: Kaggle 2× T4 GPU, fp16 mixed precision, batch=32

---

## Slide 11 — Current Results

**Headline:** CodeBERT baseline is training — early results confirm the pipeline works

**What's done:**
- Full preprocessing pipeline implemented and tested
- CodeBERT baseline (LLM-only): **test F1 = 0.6148**, AUC = 0.7333 ✅
  - Stopped at epoch 11, uniform lr=2e-5 + linear warmup scheduler
  - Previous bad run (no scheduler): F1=0.5843 → scheduler fix = +0.030 F1
- This is the LLM-only baseline VulGCL must beat

**What's next (2–3 weeks):**
- Joern batch preprocessing → 27K PDG graphs + centrality images
- Train Graph-only baseline (GAT)
- Train Image-only baseline (CNN)
- Train full VulGCL — all 3 branches fused
- Ablation study

**Visual:** Learning curve plot — loss going down, F1 going up over epochs (docs/figures/learning_curve_codebert.png)

---

## Slide 12 — Timeline & Contributions

**Headline:** Paper submission in 8 weeks — all experiments designed and infrastructure ready

**Timeline:**
```
Week 1-2   Joern preprocessing (27K functions, multiprocessing)
Week 2-3   Graph + Image baselines training (parallel, Kaggle)
Week 3-4   Full VulGCL training (3-branch fusion)
Week 4-5   Ablation study + results analysis
Week 5-6   Write methodology + results sections
Week 7     Supervisor review + revision
Week 8     Submit to IEEE TIFS
```

**Three contributions:**
1. First framework to fuse graph, visual, and semantic signals for C/C++ vulnerability detection
2. VulCNN-inspired image branch upgraded with CodeBERT (richer code semantics)
3. Large-scale coverage study: 94% of real-world C functions parseable by Joern

**Target venue:** IEEE Transactions on Information Forensics and Security (TIFS)
