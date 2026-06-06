# VulGCL — Progress Update
**Date:** June 6, 2026  
**Presenter:** Mohammad Mahafuj Rahman  
**Supervisor:** Prof. LiLi Bo  
**Target venue:** IEEE TIFS (fallback: IST)

---

## 1. Research Problem

Existing vulnerability detection tools either:
- Use **code structure** (graph-based, e.g., Devign/IVDetect) — miss semantic context
- Use **language models** (e.g., CodeBERT) — ignore structural dependencies
- Never combine graph + visual + semantic signals in one unified framework

**VulGCL bridges this gap**: a multimodal framework that fuses three independent views of the same C/C++ function.

---

## 2. Proposed Architecture — VulGCL

```
C/C++ Function
      │
      ├─── Joern (static analysis) ──→ PDG (Program Dependency Graph)
      │         │                              │
      │         │                    ┌─────────┴──────────┐
      │         │                    │                     │
      │         ▼                    ▼                     ▼
      │    Graph Branch          Image Branch          LLM Branch
      │    PDG + GAT             PDG → centrality      CodeBERT
      │    → h_G (256)           image → CNN           [CLS] → h_L (256)
      │                          → h_I (256)
      │                              │
      └──────────────────────────────┴─────────────────────┘
                                     │
                              Concatenate (768-dim)
                                     │
                                  MLP head
                                     │
                           Vulnerable / Safe
```

**Key design decisions:**
- Three branches produce equal-dimensional representations (256-dim each)
- Late fusion (concatenation) preserves modality-specific information
- CodeBERT fine-tuned jointly with the classifier head
- AdamW: backbone lr=2e-5, head lr=2e-4 (standard for BERT fine-tuning)

---

## 3. Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| `src/data/build_pdg.py` | ✅ Done | Joern .sc file approach, parses DOT output |
| `src/data/pdg_to_graph.py` | ✅ Done | CodeBERT node embeddings, batched (64/batch) |
| `src/data/pdg_to_image.py` | ✅ Done | VulCNN-style centrality × CodeBERT image |
| `src/data/dataset.py` | ✅ Done | LLM-only and full multimodal mode |
| `src/training/train.py` | ✅ Done | YAML config, early stopping, fp16 |
| `src/training/evaluate.py` | ✅ Done | F1, Accuracy, Precision, Recall, AUC-ROC |
| Graph branch (GAT) | ✅ Done | 2-layer GAT, 256-dim output |
| Image branch (CNN) | ✅ Done | 3-channel (100×100) centrality images |
| LLM branch (CodeBERT) | ✅ Done | RobertaModel + Linear(768→256) |
| Full VulGCL fusion | 🔄 Pending | Waiting for Joern batch preprocessing |
| Joern batch preprocessing | 🔄 Next | Need to run on all 27K functions |

---

## 4. Dataset: Devign

| Split | Functions | Vulnerable | Safe |
|-------|-----------|------------|------|
| Train | 21,854 | ~45% | ~55% |
| Val | 2,732 | ~45% | ~55% |
| Test | 2,732 | ~45% | ~55% |
| **Total** | **27,318** | — | — |

**Source:** Real C/C++ functions from FFmpeg, QEMU, LibTIFF, VLC  
**PDG coverage study** (200-function sample):
- Joern extraction success: **94.0%** of functions
- Failed (empty PDG): **6.0%** — platform-specific APIs (Apple VDA, Windows COM)
- Median nodes per function: **41** | P90: **223** | Max: **1,444**

---

## 5. Current Experimental Results

### Phase 7.1 — Baseline: CodeBERT-only  
*(Running now on Kaggle 2× T4 GPU — full dataset, 20 epochs, fp16)*

| Epoch | Train Loss | Val F1 | Val Acc | Val AUC |
|-------|-----------|--------|---------|---------|
| 1 | 0.6524 | 0.3170 | 0.6325 | 0.6612 |
| 2 | 0.6103 | **0.5843** | 0.6380 | 0.7059 |
| 3 | 0.5562 | 0.5465 | 0.6611 | 0.7256 |
| 4 | 0.4940 | 0.5634 | 0.6482 | 0.7151 |
| 5+ | *running...* | — | — | — |

**Observations:**
- Loss consistently decreasing (0.65 → 0.49) — model is learning
- Val F1 oscillating around 0.56–0.58 — normal for early BERT fine-tuning, will stabilize by epoch 8–10
- AUC-ROC reaching 0.7256 — model discriminates vulnerable vs safe functions reasonably well
- **Expected final F1: 0.64–0.68** (consistent with reported CodeBERT on Devign in literature)

*See: `docs/figures/learning_curve_codebert.png`*

---

## 6. Comparison with Related Work (Literature Baseline)

| Method | Dataset | F1 | Notes |
|--------|---------|-----|-------|
| Devign (original, 2019) | Devign | 0.5490 | GRU + GNN |
| IVDetect (2021) | Devign | 0.6170 | GNN + feature engineering |
| ReVeal (2021) | Devign | 0.5880 | Graph + embedding |
| LineVul (2022) | Devign | 0.6510 | CodeBERT + line-level |
| **VulGCL (CodeBERT-only baseline, ours)** | Devign | **~0.65 (projected)** | Still training |
| **VulGCL (full multimodal, target)** | Devign | **≥0.68** | 3-branch fusion |

Our CodeBERT baseline needs to be competitive with LineVul to justify the multimodal overhead.  
The full VulGCL must beat CodeBERT-only by **≥2 F1 points** to claim multimodal benefit.

---

## 7. Next Steps (2–3 weeks)

| Step | Task | Timeline |
|------|------|----------|
| 7.1 ✅ | CodeBERT baseline results | Today/Tomorrow |
| 4.2 | Write `preprocess.py` — batch Joern on 27K functions | 2–3 days |
| 7.2 | Train GNN-only baseline (GAT on PDG) | After preprocessing |
| 7.3 | Train CNN-only baseline (centrality images) | After preprocessing |
| 8.1 | Train full VulGCL (3-branch fusion) | ~1 week |
| 8.3 | Ablation study (remove one branch at a time) | ~1 week |
| 10 | Write results section + paper | Weeks 2–3 |

---

## 8. Open Questions for Discussion

1. **BigVul as second dataset** — should we add it for generalization claims?  
   (BigVul: 91K functions, 10 CWE types — stronger paper but adds 2+ weeks)

2. **Modality independence** — image and LLM branches both use CodeBERT embeddings.  
   Reviewer concern: are they independent enough?  
   Options: (a) use sent2vec for image branch like VulCNN original, (b) keep CodeBERT but show correlation analysis

3. **Target F1 threshold** — if full VulGCL doesn't beat CodeBERT-only by ≥2 F1,  
   we need either cross-modal attention fusion OR stronger graph features

---

*Full codebase: `/Users/shay/Dev/research/VulGCL/`  
Training logs: Kaggle notebook `VulGCL.ipynb`  
Roadmap: `progress/ROADMAP.md`*
