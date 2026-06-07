# VulGCL — Aliyun Run Checklist

## Instance
- [ ] Click **Yes** to create `ecs.gn8is.4xlarge` (1× L20, ¥15.84/hr)
- [ ] Wait for instance status → **Running** (~2 min)
- [ ] Click **Open** → JupyterLab opens in browser

---

## Upload Code
- [ ] In JupyterLab left sidebar → right-click → **Upload**
- [ ] Upload the entire `VulGCL/` folder to `/mnt/workspace/VulGCL`
  - Must include: `src/`, `data/devign/raw/*.jsonl`, `notebooks/ali.ipynb`
  - Tip: zip VulGCL locally, upload the zip, then unzip in terminal:
    ```bash
    cd /mnt/workspace
    unzip VulGCL.zip
    ```

---

## Notebook — Run Cells in Order

Open `notebooks/ali.ipynb` in JupyterLab.

- [ ] **Cell 1** — Install packages (`transformers`, `torch-geometric`, etc.)
  - Takes ~2 min
- [ ] **Cell 2** — Check Java + install Joern v2.0.406
  - Takes ~3 min on first run; instant on re-run
- [ ] **Cell 3** — Setup paths
  - Verify output shows `OSS save: /mnt/data` and `Device: cuda`
- [ ] **Cell 4** — Phase 1: Joern PDG extraction
  - **~3–4 hours** on 16 vCPU (28 workers)
  - Resumes if interrupted — re-run cell to continue
  - Done when: `train ok=~20000 / val ok=~2700 / test ok=~2700`
- [ ] **Cell 5** — Define Phase 2 functions (instant)
- [ ] **Cell 6** — Phase 2: CodeBERT embed → .pt files
  - **~2–3 hours** on L20 GPU
  - Resumes if interrupted
  - Done when: all 3 splits show `ok=XXXX err=0`
- [ ] **Cell 7** — Load datasets
  - Verify: `train: ~20000 samples  val: ~2700  test: ~2700`
- [ ] **Cell 8** — Define models (instant)
- [ ] **Cell 9** — Define training loop (instant)
- [ ] **Cell 10** — Run all 4 experiments
  - `graph_only` — 10 epochs, lr=1e-4  (~30 min)
  - `image_only` — 10 epochs, lr=1e-4  (~20 min)
  - `llm_only`   — 5 epochs,  lr=2e-5  (~1.5 hrs)
  - `vulgcl`     — 10 epochs, lr=2e-5  (~3 hrs)
  - **Total: ~5–6 hours**
- [ ] **Cell 11** — Print results + save `results.json`

---

## Collect Results
- [ ] Check `/mnt/data/experiments/results.json` — final F1/AUC/Acc for all 4 models
- [ ] Download `results.json` to local machine
- [ ] Fill in paper Slide 12 results table with real numbers

---

## Stop Instance
- [ ] In Aliyun DSW → click **Stop** on the VulGCL instance
- [ ] Verify data is in OSS bucket (`/mnt/data/` contents saved)
- [ ] **Do not Delete** until you've confirmed results.json is downloaded

---

## Expected Results (targets)

| Model      | F1 target | AUC target |
|------------|-----------|------------|
| graph_only | ≥ 0.61    | ≥ 0.68     |
| image_only | ≥ 0.58    | ≥ 0.65     |
| llm_only   | ≥ 0.61    | ≥ 0.73     |
| **vulgcl** | **≥ 0.68**| **≥ 0.78** |

---

## Time Estimate

| Step         | Time        |
|--------------|-------------|
| Setup        | ~10 min     |
| Phase 1      | ~3–4 hrs    |
| Phase 2      | ~2–3 hrs    |
| Training ×4  | ~5–6 hrs    |
| **Total**    | **~11–13 hrs** |

Cost estimate: 13 hrs × ¥15.84 ≈ **¥206 total**
