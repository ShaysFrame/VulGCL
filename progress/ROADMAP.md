# VulGCL — Road to Submission
# Zero → 100 Plan

**Target venue:** IEEE Transactions on Information Forensics and Security (TIFS)
**Fallback venue:** Information and Software Technology (IST)
**Goal:** Mohammad Mahafuj Rahman as 2nd author, LiLi Bo as 1st

Mark steps done with [x] as you complete them.

---

## Where You Are Now

```
Project created       ✅
Paper skeleton        ✅
Model code stubs      ✅
References populated  ✅
Concepts documented   ✅
Professor pitched     ✅ (she wants to see more depth — this plan is the answer)
Mid-term PPT created  ✅ (presentations/VulGCL_MidTerm_2026.pptx)
Environment ready     ✅ torch 2.12.0 + PyG 2.7.0 + MPS on M1
```

---

## Phase 1 — Environment Setup ✅ COMPLETE
> Goal: everything installed and runnable on your machine

- [x] **1.1** Create and activate Python virtual environment (.venv, Python 3.12)
- [x] **1.2** Install PyTorch Geometric + torch-scatter + torch-sparse
  ```bash
  # Correct command for torch 2.12.0:
  pip install torch-scatter torch-sparse -f https://data.pyg.org/whl/torch-2.12.0+cpu.html
  ```
- [x] **1.3** All packages verified:
  - torch 2.12.0  |  MPS: True (M1 GPU acceleration active)
  - torch-geometric 2.7.0
  - torch-scatter 2.1.2, torch-sparse 0.6.18
  - transformers 5.9.0, networkx 3.6.1

- [ ] **1.4** Install Joern (PDG extractor) — do this when starting Phase 3
  ```bash
  # Download from https://github.com/joernio/joern/releases
  # Extract and add to PATH, then: joern --version
  ```

- [ ] **1.5** Verify CodeBERT downloads correctly (~500 MB, one-time)
  ```bash
  source .venv/bin/activate
  python3 -c "
  from transformers import AutoTokenizer, AutoModel
  tok = AutoTokenizer.from_pretrained('microsoft/codebert-base')
  mdl = AutoModel.from_pretrained('microsoft/codebert-base')
  print('CodeBERT ready')
  "
  ```

- [ ] **1.6** Run toy LLM branch test end-to-end (one real function → h_L vector)
  ```bash
  source .venv/bin/activate && python3 src/models/llm_branch.py
  ```

---

## Phase 2 — Get the Datasets ✅ COMPLETE (Devign)
> Goal: Devign and BigVul downloaded, split into train/val/test

- [x] **2.1** Download Devign dataset via HuggingFace (DetectVul/devign)
  - train: 21,854 | validation: 2,732 | test: 2,732 | total: 27,318
  - Saved to `data/devign/raw/` as train.jsonl / validation.jsonl / test.jsonl

- [x] **2.2** Label distribution verified:
  - Nearly balanced: ~45% vulnerable, ~55% safe — no class weighting needed
  - `target` is bool (False/True) → must convert with `float(row['target'])` in dataset class

- [ ] **2.3** Download BigVul — defer until Devign pipeline is fully working

- [ ] **2.4** Write `src/data/dataset_stats.py` — proper stats script for the paper

---

## Phase 3 — PDG Extraction Pipeline
> Goal: given a C function, extract its PDG as a graph object

- [x] **3.1** Write `src/data/build_pdg.py`
  - Joern .sc file approach (stdin pipe was unreliable)
  - Returns networkx DiGraph; node attrs: type, line, code; edge attr: var
  - Uses `cpg.method.isNotStub.dotPdg.l` to exclude stubs

- [x] **3.2** Test on one real Devign function
  - Tested on FFmpeg vulnerable function: 62 nodes, 55 edges ✅
  - Empty PDG rate on 200 sample: 6.0% (platform-specific API failures)
  - Saved report to docs/figures/phase32_report.txt

- [x] **3.3** Write `src/data/pdg_to_graph.py`
  - Node features: CodeBERT [CLS] per statement, batched in groups of 64
  - Batching keeps memory flat (~25MB/batch) regardless of function size

- [x] **3.4** Write `src/data/pdg_to_image.py`
  - VulCNN approach: centrality × CodeBERT embedding per node
  - 3 channels: degree, closeness, Katz centrality
  - Resize (3, N, 768) → (3, 100, 100) bilinear
  - CodeBERT also batched in groups of 64 — no node count limit

- [x] **3.5** Coverage measurement on 200 Devign functions
  - Empty PDG: 6.0% | Usable: 94.0%
  - Median nodes: 41 | P90: 223 | Max: 1444
  - Report: progress/paper_notes_joern_coverage.txt

---

## Phase 4 — Full Data Pipeline
> Goal: one script that reads Devign → outputs ready-to-train tensors

- [x] **4.1** Write `src/data/dataset.py`
  - mode="llm_only": returns (input_ids, attention_mask, label) — no Joern needed
  - mode="full": returns all five tensors — requires Phase 4.2 cache
  - frac parameter for prototype runs (e.g. frac=0.1 = 10% of train)

- [x] **4.2** Write `src/data/preprocess.py`
  - Phase 1: Joern extraction (multiprocessing, N workers) → networkx pickles
  - Phase 2: CodeBERT embedding (GPU, single process) → PyG Data + image .pt
  - Resume capability, error logging, workspace cleanup
  - Based on VulCNN joern_graph_gen.py + ImageGeneration.py with improvements

- [ ] **4.3** Test DataLoader
  ```python
  loader = DataLoader(dataset, batch_size=32)
  batch = next(iter(loader))
  print(batch)  # should print shapes without error
  ```

---

## Phase 5 — Verify Each Model Branch
> Goal: each branch runs on real data without errors

- [ ] **5.1** Test graph branch alone
  ```python
  from src.models.graph_branch import GraphBranch
  # feed one graph batch → get h_G shape (batch_size, 256)
  ```

- [ ] **5.2** Test image branch alone
  ```python
  from src.models.image_branch import ImageBranch
  # feed one image batch (B, 3, 100, 100) → get h_I shape (batch_size, 256)
  ```

- [ ] **5.3** Test LLM branch alone
  ```python
  from src.models.llm_branch import LLMBranch
  # feed input_ids, attention_mask → get h_L shape (batch_size, 256)
  ```

- [ ] **5.4** Test full VulGCL (all three branches fused)
  ```python
  from src.models.vulgcl import VulGCL
  # feed all inputs → get logit shape (batch_size,)
  # compute loss, call .backward() — no errors?
  ```

---

## Phase 6 — Training Infrastructure
> Goal: a training loop that saves checkpoints and logs metrics

- [x] **6.1** Write `src/training/train.py`
  - Reads YAML config, supports --config argument
  - AdamW with separate LRs: CodeBERT backbone (2e-5) vs head (2e-4)
  - Saves best checkpoint to experiments/checkpoints/{name}/best.pt
  - Saves epoch log to logs/{name}/train_log.txt

- [x] **6.2** Write `src/training/evaluate.py`
  - --config + optional --checkpoint arguments
  - Reports F1, Accuracy, Precision, Recall, AUC-ROC
  - Saves JSON to experiments/results/{name}/metrics.json

- [ ] **6.3** Test training loop on prototype (10% data, 3 epochs)
  - Run: python src/training/train.py --config experiments/configs/prototype_codebert.yaml
  - Does loss go down? Does val F1 improve?

---

## Phase 7 — Run Baseline Experiments
> Goal: numbers for the comparison table in the paper

Run each baseline. Record F1 on Devign test set.

- [x] **7.1** Run `baseline_codebert` (LLM branch only)
  - Result (2026-06-06): F1=0.6148, Acc=0.6541, Prec=0.6294, Rec=0.6008, AUC=0.7333
  - Stopped at epoch 11 (early stop=6). Kaggle 2×T4, lr=2e-5, linear warmup+decay.
  - Source: notebooks/VulGCL.ipynb → test_results.json

- [ ] **7.2** Run `baseline_gnn` (graph branch only)
  ```bash
  python src/training/train.py --config experiments/configs/baseline_gnn.yaml
  ```

- [ ] **7.3** Run `baseline_cnn` (image branch only)
  ```bash
  python src/training/train.py --config experiments/configs/baseline_cnn.yaml
  ```

- [ ] **7.4** Fill in baseline results in `paper/sections/04_experiments.tex`
  - Replace `--` placeholders with real numbers

---

## Phase 8 — Run Full VulGCL Experiments
> Goal: the main results that prove VulGCL works

- [ ] **8.1** Run full VulGCL on Devign (3 seeds, take average)
  ```bash
  python src/training/train.py --config experiments/configs/vulgcl_full.yaml --seed 42
  python src/training/train.py --config experiments/configs/vulgcl_full.yaml --seed 1
  python src/training/train.py --config experiments/configs/vulgcl_full.yaml --seed 7
  ```

- [ ] **8.2** Run full VulGCL on BigVul

- [ ] **8.3** Run ablation study (remove one branch at a time)
  - VulGCL without graph branch
  - VulGCL without image branch
  - VulGCL without LLM branch
  - Record each in the ablation table

- [ ] **8.4** Fill in all result tables in `paper/sections/04_experiments.tex`

---

## Phase 9 — Edge Deployment (Raspberry Pi)
> Goal: show VulGCL-Lite runs on hardware with acceptable latency

- [ ] **9.1** Export trained model to ONNX
  ```python
  from deployment.quantize import export_to_onnx
  export_to_onnx(model, sample_inputs, "deployment/vulgcl.onnx")
  ```

- [ ] **9.2** Apply int8 quantization
  ```python
  from deployment.quantize import quantize_model
  quantize_model("deployment/vulgcl.onnx", "deployment/vulgcl_int8.onnx")
  ```

- [ ] **9.3** Benchmark on Raspberry Pi 4B
  - Copy `vulgcl_int8.onnx` to Pi
  - Run `benchmark()` from `deployment/quantize.py`
  - Record: average latency (ms), RAM usage (MB)

- [ ] **9.4** Fill in edge deployment table in experiments section

---

## Phase 10 — Write the Paper
> Goal: complete, submission-ready paper

- [ ] **10.1** Draw architecture figure (Figure 1)
  - Three branches feeding into fusion MLP
  - Can use draw.io or Inkscape, save as PDF
  - Place in `paper/figures/architecture.pdf`
  - Add `\includegraphics` to `03_methodology.tex`

- [ ] **10.2** Complete `paper/sections/03_methodology.tex`
  - Fill in any missing equations
  - Reference Figure 1

- [ ] **10.3** Complete `paper/sections/04_experiments.tex`
  - All tables filled (from Phase 7, 8, 9)
  - Answer each RQ explicitly in text

- [ ] **10.4** Write `paper/sections/05_discussion.tex`
  - What do results mean?
  - Where does VulGCL fail? (error analysis)
  - Threats to validity

- [ ] **10.5** Polish `paper/sections/01_introduction.tex`
  - Update any placeholder numbers with real ones
  - Make sure contribution list matches final paper

- [ ] **10.6** Polish `paper/sections/06_conclusion.tex`

- [ ] **10.7** Build the PDF and read it top to bottom
  ```bash
  cd paper && latexmk -pdf -output-directory=build main.tex
  ```

---

## Phase 11 — Supervisor Review
> Goal: LiLi Bo approves the paper for submission

- [ ] **11.1** Send full draft to LiLi Bo
- [ ] **11.2** Address all her feedback
- [ ] **11.3** Second round review if needed

---

## Phase 12 — Submission
> Goal: paper submitted

- [ ] **12.1** Prepare replication package
  - Code + preprocessed data (or download script) + trained model weights
  - Upload to Zenodo or GitHub
  - Add DOI link to paper

- [ ] **12.2** Format check against venue requirements
  - Page limit? Double-blind? Figure resolution?

- [ ] **12.3** Submit via journal submission system

- [ ] **12.4** 🎉 Done. Wait for reviews.

---

## Progress Tracker

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Environment Setup | ✅ Complete |
| 2 | Get Datasets | ✅ Complete (Devign) |
| 3 | PDG Extraction Pipeline | ✅ Complete |
| 4 | Full Data Pipeline | 🔄 In progress (4.1 done, 4.2 pending) |
| 5 | Verify Model Branches | 🔄 In progress (LLM verified, graph/image pending) |
| 6 | Training Infrastructure | ✅ Complete (train.py + evaluate.py written) |
| 7 | Baseline Experiments | 🔄 Next — run prototype_codebert first |
| 8 | Full VulGCL Experiments | ⬜ Not started |
| 9 | Edge Deployment | ⬜ Not started |
| 10 | Write the Paper | 🔄 In progress (~50% done) |
| 11 | Supervisor Review | ⬜ Not started |
| 12 | Submission | ⬜ Not started |

---

## Rules

1. **Do phases in order.** Don't touch Phase 8 if Phase 3 isn't done.
2. **One checkbox at a time.** Finish it fully before moving to the next.
3. **Update this file** every time you complete a step.
4. **If you get stuck**, open an issue with Claude and describe exactly which step you're on.
5. **Don't rewrite things that work.** If a branch runs, move on.
