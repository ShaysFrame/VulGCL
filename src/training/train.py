"""Training loop for VulGCL and baseline models.

Usage:
    python src/training/train.py --config experiments/configs/baseline_codebert.yaml
    python src/training/train.py --config experiments/configs/prototype_codebert.yaml

Outputs (all inside project):
    experiments/checkpoints/{name}/best.pt  — best model by val F1
    experiments/results/{name}/metrics.json — final test metrics
    logs/{name}/train_log.txt               — epoch-by-epoch log
"""

import argparse
import json
import random
import sys
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
from sklearn.metrics import f1_score, roc_auc_score, accuracy_score, precision_score, recall_score
import yaml
from pathlib import Path

sys.path.insert(0, ".")
from src.data.dataset import VulDataset
from src.models.llm_branch import LLMBranch

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ── Helpers ────────────────────────────────────────────────────────────────────

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


# ── Models ─────────────────────────────────────────────────────────────────────

class LLMClassifier(nn.Module):
    """LLM branch (CodeBERT → 256-dim) + binary classifier head."""

    def __init__(self, hidden_dim: int, dropout: float, model_name: str):
        super().__init__()

        class _Cfg:
            pass

        cfg            = _Cfg()
        cfg.hidden_dim = hidden_dim
        cfg.model_name = model_name

        self.encoder    = LLMBranch(cfg)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, input_ids, attention_mask):
        h = self.encoder(input_ids, attention_mask)          # (B, hidden_dim)
        return self.classifier(h).squeeze(-1)                # (B,)


# ── Evaluation ─────────────────────────────────────────────────────────────────

def evaluate(model, loader, device):
    model.eval()
    all_preds, all_labels, all_probs = [], [], []

    with torch.no_grad():
        for batch in loader:
            ids   = batch["input_ids"].to(device)
            mask  = batch["attention_mask"].to(device)
            labels = batch["label"]

            logits = model(ids, mask).cpu()
            probs  = torch.sigmoid(logits)
            preds  = (probs > 0.5).long()

            all_preds.extend(preds.tolist())
            all_labels.extend(labels.long().tolist())
            all_probs.extend(probs.tolist())

    f1   = f1_score(all_labels,        all_preds, zero_division=0)
    acc  = accuracy_score(all_labels,  all_preds)
    prec = precision_score(all_labels, all_preds, zero_division=0)
    rec  = recall_score(all_labels,    all_preds, zero_division=0)
    try:
        auc = roc_auc_score(all_labels, all_probs)
    except Exception:
        auc = 0.0

    return {"f1": f1, "acc": acc, "precision": prec, "recall": rec, "auc": auc}


# ── Main ───────────────────────────────────────────────────────────────────────

def main(config_path: str):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    name   = cfg["name"]
    seed   = cfg["training"].get("seed", 42)
    device = get_device()
    set_seed(seed)

    print(f"{'='*60}")
    print(f"Run      : {name}")
    print(f"Config   : {config_path}")
    print(f"Device   : {device}")
    print(f"{'='*60}\n")

    # ── Dirs ──────────────────────────────────────────────────────────────────
    ckpt_dir    = PROJECT_ROOT / "experiments" / "checkpoints" / name
    results_dir = PROJECT_ROOT / "experiments" / "results"     / name
    log_dir     = PROJECT_ROOT / "logs" / name
    for d in [ckpt_dir, results_dir, log_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # ── Datasets ──────────────────────────────────────────────────────────────
    data_dir    = PROJECT_ROOT / "data" / "devign" / "raw"
    frac        = cfg["data"].get("frac", 1.0)
    max_seq_len = cfg["data"].get("max_seq_len", 512)
    model_name  = cfg["model"]["llm"].get("model_name", "microsoft/codebert-base")

    train_ds = VulDataset("train",      str(data_dir), frac=frac, seed=seed,
                          max_seq_len=max_seq_len, model_name=model_name)
    val_ds   = VulDataset("validation", str(data_dir),
                          max_seq_len=max_seq_len, model_name=model_name)
    test_ds  = VulDataset("test",       str(data_dir),
                          max_seq_len=max_seq_len, model_name=model_name)

    print(f"Train : {len(train_ds)} functions  (frac={frac})")
    print(f"Val   : {len(val_ds)} functions")
    print(f"Test  : {len(test_ds)} functions\n")

    bs = cfg["training"]["batch_size"]
    train_loader = DataLoader(train_ds, batch_size=bs, shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=bs, shuffle=False, num_workers=0)
    test_loader  = DataLoader(test_ds,  batch_size=bs, shuffle=False, num_workers=0)

    # ── Model ─────────────────────────────────────────────────────────────────
    hidden_dim = cfg["model"]["llm"]["hidden_dim"]
    dropout    = cfg["model"].get("dropout", 0.1)

    model = LLMClassifier(hidden_dim, dropout, model_name).to(device)

    lr = cfg["training"]["learning_rate"]
    optimizer = torch.optim.AdamW([
        {"params": model.encoder.encoder.parameters(), "lr": lr},
        {"params": model.encoder.proj.parameters(),    "lr": lr * 10},
        {"params": model.classifier.parameters(),      "lr": lr * 10},
    ], weight_decay=cfg["training"].get("weight_decay", 1e-4))

    criterion = nn.BCEWithLogitsLoss()

    # ── Training loop ─────────────────────────────────────────────────────────
    best_f1    = 0.0
    best_epoch = 0
    log_lines  = [f"Run: {name}", f"Config: {config_path}", f"Device: {device}", ""]

    for epoch in range(1, cfg["training"]["epochs"] + 1):
        model.train()
        total_loss = 0.0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch:02d}", leave=False)
        for batch in pbar:
            ids    = batch["input_ids"].to(device)
            mask   = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()
            logits = model(ids, mask)
            loss   = criterion(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
            pbar.set_postfix(loss=f"{loss.item():.4f}")

        avg_loss    = total_loss / len(train_loader)
        val_metrics = evaluate(model, val_loader, device)

        line = (f"Epoch {epoch:02d}/{cfg['training']['epochs']}  "
                f"loss={avg_loss:.4f}  "
                f"val_F1={val_metrics['f1']:.4f}  "
                f"val_Acc={val_metrics['acc']:.4f}  "
                f"val_AUC={val_metrics['auc']:.4f}")
        print(line)
        log_lines.append(line)

        if val_metrics["f1"] > best_f1:
            best_f1    = val_metrics["f1"]
            best_epoch = epoch
            torch.save(model.state_dict(), ckpt_dir / "best.pt")

    print(f"\nBest val F1: {best_f1:.4f} at epoch {best_epoch}")

    # ── Test evaluation ───────────────────────────────────────────────────────
    model.load_state_dict(torch.load(ckpt_dir / "best.pt",
                                     map_location=device, weights_only=True))
    test_metrics = evaluate(model, test_loader, device)

    result_block = (
        f"\n{'='*60}\n"
        f"TEST RESULTS — {name}\n"
        f"{'='*60}\n"
        f"  F1        : {test_metrics['f1']:.4f}\n"
        f"  Accuracy  : {test_metrics['acc']:.4f}\n"
        f"  Precision : {test_metrics['precision']:.4f}\n"
        f"  Recall    : {test_metrics['recall']:.4f}\n"
        f"  AUC-ROC   : {test_metrics['auc']:.4f}\n"
        f"{'='*60}"
    )
    print(result_block)
    log_lines.append(result_block)

    # Save log and results
    with open(log_dir / "train_log.txt", "w") as f:
        f.write("\n".join(log_lines))

    with open(results_dir / "metrics.json", "w") as f:
        json.dump({"config": name, **test_metrics}, f, indent=2)

    print(f"\nLog     → logs/{name}/train_log.txt")
    print(f"Results → experiments/results/{name}/metrics.json")
    print(f"Model   → experiments/checkpoints/{name}/best.pt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()
    main(args.config)
