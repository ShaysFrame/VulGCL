# VulGCL: Multimodal Vulnerability Detection via Graph, CNN, and LLM Fusion

**Mohammad Mahafuj Rahman**, Bo LiLi  
Yangzhou University

---

## Overview

VulGCL is a multimodal vulnerability detection framework for general source code (C/C++/Java).
It combines three complementary views of a code snippet:

| Branch | Input | Model | What it captures |
|--------|-------|-------|-----------------|
| Graph  | PDG graph | GNN | Structural relationships between code elements |
| Image  | PDG → image | CNN | Visual patterns in code structure |
| LLM    | Code text | CodeBERT | Semantic meaning of code |

All three outputs are fused and passed to a classifier. A lightweight version
(**VulGCL-Lite**) is quantized for edge deployment on Raspberry Pi 4B.

---

## Project Structure

```
VulGCL/
├── paper/              # LaTeX paper
│   ├── main.tex        # Compile this
│   ├── sections/       # One .tex file per section
│   ├── figures/        # All figures (PDF/PNG)
│   ├── tables/         # Generated LaTeX tables
│   └── references.bib  # All citations
├── src/                # Source code
│   ├── data/           # Data extraction, labeling, PDG building
│   ├── models/         # VulGCL model architecture
│   ├── training/       # Training and evaluation
│   └── utils/          # Config, visualization helpers
├── data/               # Data (gitignored — too large)
│   ├── raw/            # Devign, BigVul, Stack Overflow snippets
│   ├── processed/      # Labeled train/val/test splits
│   └── pdgs/           # Generated PDG files
├── experiments/        # Reproducible experiments
│   ├── configs/        # YAML config per experiment
│   └── results/        # Saved metrics (gitignored)
├── notebooks/          # Exploration and analysis
├── deployment/         # Raspberry Pi quantization and benchmarking
└── tests/              # Unit tests
```

---

## Datasets

| Dataset | Size | Language | Source |
|---------|------|----------|--------|
| Devign  | 27K functions | C | NeurIPS 2019 |
| BigVul  | 188K functions | C/C++ | MSR 2020 |
| SO Snippets | 620K posts | Mixed | This work |

---

## Baselines

| Model | Description |
|-------|-------------|
| VulCNN | PDG → image → CNN |
| VulGAI | PDG → improved image → CNN |
| ReGVD | Code → graph → GNN |
| iGnnVD | Integrated GNN |
| CodeBERT-ft | Fine-tuned CodeBERT only |
| **VulGCL** | Graph + CNN + LLM (ours) |
| **VulGCL-Lite** | Quantized, runs on Raspberry Pi 4B |

---

## Setup

```bash
git clone <repo>
cd VulGCL
pip install -r requirements.txt
```

---

## Citation

```bibtex
@article{rahman2026vulgcl,
  title={VulGCL: Multimodal Vulnerability Detection via Graph, CNN, and LLM Fusion},
  author={Rahman, Mohammad Mahafuj and Bo, LiLi},
  journal={},
  year={2026}
}
```
