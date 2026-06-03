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

## Phase 2 — Get the Datasets
> Goal: Devign and BigVul downloaded, split into train/val/test

- [ ] **2.1** Download Devign dataset
  - Source: https://sites.google.com/view/devign
  - ~27K C functions, JSON format with labels
  - Save to `data/devign/raw/`

- [ ] **2.2** Download BigVul dataset
  - Source: https://github.com/ZeoVan/MSR_20_Code_vulnerability_V2.0
  - ~188K C/C++ functions, CSV format
  - Save to `data/bigvul/raw/`

- [ ] **2.3** Verify dataset files are in place
  ```bash
  ls data/devign/raw/
  ls data/bigvul/raw/
  ```

- [ ] **2.4** Write `src/data/dataset_stats.py` — print label distribution
  - How many vulnerable vs. non-vulnerable in each dataset?
  - Are they balanced? (Devign ≈ 45% vulnerable, BigVul ≈ 5% — very imbalanced)

---

## Phase 3 — PDG Extraction Pipeline
> Goal: given a C function, extract its PDG as a graph object

- [ ] **3.1** Write `src/data/build_pdg.py`
  - Input: path to a `.c` file with one function
  - Run Joern on it
  - Parse Joern's output (nodes + edges JSON)
  - Return: networkx graph object

- [ ] **3.2** Test on one real Devign function
  - Pick any vulnerable function from the dataset
  - Extract its PDG
  - Print: number of nodes, number of edges
  - Visualize with matplotlib (optional but impressive to show professor)

- [ ] **3.3** Write `src/data/pdg_to_graph.py`
  - Convert networkx PDG → PyTorch Geometric `Data` object
  - Node features: CodeBERT embedding of the statement text (768-dim)
  - This feeds into the graph branch

- [ ] **3.4** Write `src/data/pdg_to_image.py`
  - Input: networkx PDG
  - Compute: degree centrality, Katz centrality, closeness centrality per node
  - Build: 3-channel centrality matrix
  - Resize to fixed size (e.g., 100×100) for CNN
  - Output: numpy array of shape (3, 100, 100)

- [ ] **3.5** Test image conversion on the same function from 3.2
  - Visualize all 3 channels as grayscale images
  - Do they look different from each other? (They should)

---

## Phase 4 — Full Data Pipeline
> Goal: one script that reads Devign → outputs ready-to-train tensors

- [ ] **4.1** Write `src/data/dataset.py`
  - Class `VulDataset(torch.utils.data.Dataset)`
  - `__getitem__` returns: `(graph, image, input_ids, attention_mask, label)`
  - Handle caching: PDG extraction is slow, cache results to disk

- [ ] **4.2** Write `src/data/preprocess.py`
  - Run full preprocessing on Devign (all 27K functions)
  - Save processed data to `data/devign/processed/`
  - Expected time: 2–5 hours on CPU (PDG extraction is slow)

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

- [ ] **6.1** Write `src/training/train.py`
  - Load config from YAML
  - Build model + optimizer + scheduler
  - Training loop with loss logging
  - Save best checkpoint (based on val F1)

- [ ] **6.2** Write `src/training/evaluate.py`
  - Load checkpoint
  - Run on test set
  - Report: Accuracy, Precision, Recall, F1, AUC

- [ ] **6.3** Test training loop on tiny subset (500 samples)
  - Does it run for 2 epochs without crashing?
  - Does loss go down?

---

## Phase 7 — Run Baseline Experiments
> Goal: numbers for the comparison table in the paper

Run each baseline. Record F1 on Devign test set.

- [ ] **7.1** Run `baseline_codebert` (LLM branch only)
  ```bash
  python src/training/train.py --config experiments/configs/baseline_codebert.yaml
  ```

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
| 2 | Get Datasets | ⬜ Not started |
| 3 | PDG Extraction Pipeline | ⬜ Not started |
| 4 | Full Data Pipeline | ⬜ Not started |
| 5 | Verify Model Branches | 🔄 In progress (LLM branch next) |
| 6 | Training Infrastructure | ⬜ Not started |
| 7 | Baseline Experiments | ⬜ Not started |
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
