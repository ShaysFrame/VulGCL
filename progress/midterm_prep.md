# Mid-term Prep — Figures, FigJam Prompts, PPT Structure

---

## Section 1 — Paper Figure Outline (assuming experiments succeed)

For a 10-page IEEE TIFS paper: **6 figures + 4 tables**

| # | Figure | Purpose | Section |
|---|--------|---------|---------|
| Fig 1 | VulGCL Architecture — full 3-branch system | Main contribution visual | Methodology §3 |
| Fig 2 | PDG Construction — C code → Joern → labeled graph | Explains input representation | Methodology §3.1 |
| Fig 3 | Image Branch — how 3-channel centrality image is built | Explains visual modality | Methodology §3.2 |
| Fig 4 | Training Curves — loss + F1 over epochs for all 4 models | Shows convergence | Experiments §4 |
| Fig 5 | Ablation Bar Chart — each branch alone vs full VulGCL | Proves each branch contributes | Experiments §4.3 |
| Fig 6 | Case Study — real CVE function, what each branch captures | Qualitative analysis | Discussion §5 |

| # | Table | Purpose |
|---|-------|---------|
| Table 1 | Dataset statistics (Devign + BigVul) | Data section |
| Table 2 | Main results — VulGCL vs 8 baselines | Most important table |
| Table 3 | Ablation study numbers | Ablation section |
| Table 4 | Edge deployment latency — Raspberry Pi (optional) | Deployment section |

---

## Section 2 — FigJam AI Prompts

Go to FigJam → click the magic wand (AI) icon → "Generate diagram" → paste each prompt below.

---

### Fig 1 — VulGCL Architecture

```
Create a flowchart diagram showing a multimodal neural network architecture called VulGCL.

Start with a single box labeled "C/C++ Function (Source Code)" at the top.
Arrow down to box "Joern Static Analysis".
Arrow down to box "PDG - Program Dependency Graph".

From PDG, three arrows branch to three parallel boxes:
- Left box (blue): "Graph Branch" — "2-layer GAT" — output "h_G 256-dim"
- Middle box (green): "Image Branch" — "3-ch Centrality Image 100x100" — "5-layer CNN" — output "h_I 256-dim"
- Right box (purple): "LLM Branch" — "Top-10 critical statements (betweenness centrality)" — "CodeBERT (RoBERTa-base)" — "Linear 768 to 256" — output "h_L 256-dim"

Three arrows from the branches converge into box "Concatenate → 768-dim".
Arrow to box "MLP Classifier 768 → 256 → 1 + Sigmoid".
Two arrows split: "Vulnerable" (red label) and "Safe" (green label).

Use rounded boxes, clean white background, IEEE paper style.
```

---

### Fig 2 — PDG Construction

```
Create a two-panel diagram showing how C source code becomes a Program Dependency Graph.

Left panel: a code box showing a short C function (about 6 lines) with one line highlighted in red labeled "vulnerable line".

Arrow in the middle labeled "Joern Static Analysis".

Right panel: a directed graph with 6 circular nodes. Each node has a short code statement inside. Draw edges between nodes — solid arrows labeled "data dep" and dashed arrows labeled "ctrl dep". 

Below the graph: a small 3-column table with headers: Node ID | Statement | Type.
```

---

### Fig 3 — Image Branch Detail

```
Create a horizontal step-by-step flowchart:

Box 1: "PDG Graph" — small circles connected by arrows.
Arrow labeled "Compute 3 Centrality Scores per node".

Box 2: three rows stacked — "Degree centrality: 0.42", "Closeness centrality: 0.31", "Katz centrality: 0.27".
Arrow labeled "Multiply by CodeBERT node embedding (768-dim)".

Box 3: "3 × N × 768 Matrix" — shown as stacked rectangles colored blue, green, orange.
Arrow labeled "Bilinear Resize to 100×100".

Box 4: "3-channel Image (100×100)" — shown as three overlapping colored squares.
Arrow to "5-layer CNN → h_I ∈ R^256".
```

---

### Fig 4 — Training Curves (placeholder values, update after results)

```
Create a two-panel line chart.

Left panel title "Training Loss":
- One line labeled "CodeBERT baseline" going down from 0.65 to 0.38 over 12 epochs
- One line labeled "VulGCL full" going down from 0.68 to 0.32 over 12 epochs
- X axis: Epoch (1 to 12), Y axis: BCE Loss

Right panel title "Validation F1":
- One line labeled "CodeBERT baseline" rising from 0.32 to 0.65 with slight oscillation
- One line labeled "VulGCL full" rising from 0.30 to 0.71
- X axis: Epoch (1 to 12), Y axis: F1 Score (0.3 to 0.8)
- Mark the best epoch with a gold star on each line
```

---

### Fig 5 — Ablation Bar Chart (placeholder values)

```
Create a grouped bar chart.

X axis has 4 groups: "Graph Only", "Image Only", "LLM Only", "VulGCL Full"
Each group has 2 bars: F1 Score (blue), AUC-ROC (orange)

Values:
- Graph Only:  F1=0.58, AUC=0.70
- Image Only:  F1=0.55, AUC=0.68
- LLM Only:    F1=0.65, AUC=0.73
- VulGCL Full: F1=0.71, AUC=0.79

Add a horizontal dashed line at F1=0.65 labeled "LLM-only baseline".
Add percentage labels on top of each bar showing gain vs LLM-only.
Title: "Ablation Study on Devign Test Set"
Y axis: 0.50 to 0.85
```

---

### Fig 6 — Case Study

```
Create a three-column comparison diagram.

Title: "Case Study: CVE-2016-10087 (libpng buffer overflow)"

Left column header "Source Code":
Show a C function of about 8 lines. Highlight line 5 in red. Add a red label "vulnerable: no bounds check".

Middle column header "Graph Branch View":
Show a small PDG graph with 5 nodes. Highlight the vulnerable node in red. Label: "GAT assigns high attention weight to this node".

Right column header "Image Branch View":
Show a small heatmap image 4x4. Show one bright red cell. Label: "high centrality × CodeBERT signal at vulnerable statement".

Bottom row: "VulGCL prediction: Vulnerable (confidence 0.89)"
```

---

## Section 3 — Mid-term PPT Structure

12 slides total. The images from FigJam go where marked with [IMAGE].

---

### Slide 1 — Title
- Title: **VulGCL: A Multimodal Graph-CNN-LLM Framework for C/C++ Vulnerability Detection**
- Subtitle: Mid-term Progress Report
- Your name + supervisor name + Yangzhou University + June 2026

---

### Slide 2 — Motivation
- Headline: **Software vulnerabilities are a critical and growing threat**
- 3 bullet points:
  - CVE database: 25,226 new vulnerabilities reported in 2023 alone
  - Manual code review cannot scale to millions of lines of code
  - Automated tools have high false positive rates (Flawfinder: >80% FP)
- [IMAGE]: a bar chart showing CVE count growth from 2015 to 2023 — you can screenshot this from cvedetails.com

---

### Slide 3 — Research Gap
- Headline: **Existing methods each capture only one view of code**
- Table:

| Method | Captures Text? | Captures Structure? | Captures Visual Patterns? |
|--------|---------------|---------------------|--------------------------|
| CodeBERT / LineVul | ✅ | ❌ | ❌ |
| Devign / IVDetect (GNN) | ❌ | ✅ | ❌ |
| VulCNN | ❌ | ❌ | ✅ |
| **VulGCL (Ours)** | **✅** | **✅** | **✅** |

- One sentence: "No existing method fuses all three signal types in a single framework."

---

### Slide 4 — Proposed Solution
- Headline: **VulGCL fuses three independent views of every C/C++ function**
- [IMAGE]: Fig 1 architecture diagram from FigJam
- 3 bullets below the image:
  - Graph Branch: captures data/control dependencies via GAT
  - Image Branch: captures structural patterns as visual signals via CNN
  - LLM Branch: captures semantic meaning via CodeBERT

---

### Slide 5 — PDG Extraction
- Headline: **Step 1: Extract the Program Dependency Graph using Joern**
- [IMAGE]: Fig 2 PDG construction diagram from FigJam
- 2 bullets:
  - Joern: industry-standard static analysis tool (used in security research)
  - Coverage on Devign: 94.0% of functions successfully parsed (6% empty = platform-specific APIs)

---

### Slide 6 — Image Branch (your novel contribution)
- Headline: **Step 2: Convert PDG to a 3-channel centrality image**
- [IMAGE]: Fig 3 image branch diagram from FigJam
- 2 bullets:
  - Inspired by VulCNN (Ma et al., ICSE 2022) — upgraded with CodeBERT instead of sent2vec
  - Each channel = one centrality metric × CodeBERT semantic embedding per node

---

### Slide 7 — Dataset
- Headline: **Evaluation on Devign: 27,318 real-world C/C++ functions**
- Table:

| Split | Total | Vulnerable | Safe |
|-------|-------|-----------|------|
| Train | 21,854 | ~45% | ~55% |
| Validation | 2,732 | ~45% | ~55% |
| Test | 2,732 | ~45% | ~55% |

- Source: FFmpeg, QEMU, LibTIFF, VLC (real CVE-confirmed vulnerabilities)
- PDG extraction: 94% usable — measured on 200-function sample

---

### Slide 8 — Current Results (honest preliminary)
- Headline: **Preliminary baseline: CodeBERT-only on full Devign**
- Table:

| Epoch | Train Loss | Val F1 | Val AUC |
|-------|-----------|--------|---------|
| 1 | 0.6524 | 0.3170 | 0.6612 |
| 2 | **0.6103** | **0.5843** | **0.7059** |
| 3 | 0.5562 | 0.5465 | 0.7256 |
| ... | ... | ... | ... |
| Final (est.) | — | **0.64–0.67** | **0.73–0.76** |

- Note: rerunning with LR scheduler — expecting improvement
- This is the baseline VulGCL must beat

---

### Slide 9 — Expected Results (projected, will update)
- Headline: **VulGCL projected to outperform all single-modal baselines**
- [IMAGE]: Fig 5 ablation bar chart from FigJam (with placeholder values)
- Note on slide: *"Values are projections — will be updated with real numbers"*
- Key claim: multimodal fusion expected to gain +5 to +8 F1 points over best single branch

---

### Slide 10 — Comparison with Related Work
- Headline: **VulGCL targets state-of-the-art on Devign**

| Method | Devign F1 | Notes |
|--------|-----------|-------|
| Devign (Russell et al., 2019) | 0.549 | GRU + GNN |
| ReVeal (Chakraborty et al., 2021) | 0.588 | Graph embedding |
| IVDetect (Li et al., 2021) | 0.617 | GNN + features |
| LineVul (Fu & Tantithamthavorn, 2022) | 0.651 | CodeBERT line-level |
| **VulGCL (ours, projected)** | **≥0.68** | 3-branch fusion |

---

### Slide 11 — Next Steps & Timeline
- Headline: **3 remaining experiments, paper writing in parallel**

```
Week 1-2   Joern batch preprocessing (27K functions)
Week 2-3   Train Graph baseline + Image baseline (Kaggle, parallel)
Week 3-4   Train full VulGCL (3-branch fusion)
Week 4-5   Ablation study (remove one branch at a time)
Week 5-6   Write results section, complete paper draft
Week 7     Supervisor review + revisions
Week 8     Submit to IEEE TIFS
```

---

### Slide 12 — Summary
- Headline: **What we have built so far**
- 4 bullets:
  - Full 3-branch architecture implemented (Graph + Image + LLM)
  - PDG extraction pipeline: 94% coverage on Devign
  - Training infrastructure: fp16, DataParallel, early stopping, LR scheduler
  - CodeBERT baseline training: F1 = 0.5843 → rerunning with LR fix
- One sentence close: "VulGCL is the first framework to unify graph, visual, and semantic signals for C/C++ vulnerability detection."
