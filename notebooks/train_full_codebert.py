"""
VulGCL — Full CodeBERT baseline training script.
Target: Aliyun ECS with T4 or V100 GPU (pay-as-you-go).

Setup on Aliyun (run once after SSH in):
    pip install transformers datasets scikit-learn tqdm

Run:
    python train_full_codebert.py

Outputs (in same directory):
    best_model.pt          — best checkpoint by val F1
    train_log.txt          — epoch-by-epoch metrics
    test_results.json      — final test metrics for the paper

Expected: ~1.5 hrs on T4, under $1.
"""

import json
import random
import time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, RobertaModel
from sklearn.metrics import (f1_score, roc_auc_score,
                             accuracy_score, precision_score, recall_score)
from datasets import load_dataset
from tqdm import tqdm

# ── Config ─────────────────────────────────────────────────────────────────────
CFG = {
    "model_name":       "microsoft/codebert-base",
    "hidden_dim":       256,
    "dropout":          0.3,
    "epochs":           20,
    "batch_size":       32,       # T4 can handle 32 at seq_len=512 with fp16
    "lr":               2e-5,
    "weight_decay":     1e-4,
    "max_seq_len":      512,
    "frac":             1.0,      # full dataset
    "seed":             42,
    "early_stop":       5,        # stop if val F1 doesn't improve for 5 epochs
    "fp16":             True,     # mixed precision — 2x faster on T4/V100
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device : {DEVICE}")
print(f"Config : batch={CFG['batch_size']}  epochs={CFG['epochs']}  fp16={CFG['fp16']}\n")


# ── Reproducibility ────────────────────────────────────────────────────────────
def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

set_seed(CFG["seed"])


# ── Dataset ────────────────────────────────────────────────────────────────────
print("Downloading Devign from HuggingFace...")
raw = load_dataset("DetectVul/devign")

tokenizer = AutoTokenizer.from_pretrained(CFG["model_name"])

def make_rows(split, frac=1.0):
    rows = [{"func": r["func"], "label": float(r["target"])} for r in raw[split]]
    if frac < 1.0:
        rng  = random.Random(CFG["seed"])
        rows = rng.sample(rows, max(1, int(len(rows) * frac)))
    return rows

train_rows = make_rows("train",      CFG["frac"])
val_rows   = make_rows("validation", 1.0)
test_rows  = make_rows("test",       1.0)
print(f"Train : {len(train_rows)} | Val : {len(val_rows)} | Test : {len(test_rows)}\n")


class DevignDataset(Dataset):
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        row = self.rows[idx]
        enc = tokenizer(
            row["func"],
            max_length=CFG["max_seq_len"],
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "label":          torch.tensor(row["label"], dtype=torch.float),
        }


train_loader = DataLoader(DevignDataset(train_rows), batch_size=CFG["batch_size"],
                          shuffle=True,  num_workers=4, pin_memory=True)
val_loader   = DataLoader(DevignDataset(val_rows),   batch_size=CFG["batch_size"],
                          shuffle=False, num_workers=4, pin_memory=True)
test_loader  = DataLoader(DevignDataset(test_rows),  batch_size=CFG["batch_size"],
                          shuffle=False, num_workers=4, pin_memory=True)


# ── Model ──────────────────────────────────────────────────────────────────────
class LLMClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder    = RobertaModel.from_pretrained(CFG["model_name"])
        self.proj       = nn.Linear(768, CFG["hidden_dim"])
        self.classifier = nn.Sequential(
            nn.Dropout(CFG["dropout"]),
            nn.Linear(CFG["hidden_dim"], 1),
        )

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = out.last_hidden_state[:, 0, :]
        h   = self.proj(cls)
        return self.classifier(h).squeeze(-1)


model = LLMClassifier().to(DEVICE)

optimizer = torch.optim.AdamW([
    {"params": model.encoder.parameters(),    "lr": CFG["lr"]},
    {"params": model.proj.parameters(),       "lr": CFG["lr"] * 10},
    {"params": model.classifier.parameters(), "lr": CFG["lr"] * 10},
], weight_decay=CFG["weight_decay"])

criterion = nn.BCEWithLogitsLoss()
scaler    = torch.cuda.amp.GradScaler(enabled=CFG["fp16"])

total_params = sum(p.numel() for p in model.parameters()) / 1e6
print(f"Model: {total_params:.1f}M parameters\n")


# ── Eval ───────────────────────────────────────────────────────────────────────
def evaluate(loader):
    model.eval()
    all_preds, all_labels, all_probs = [], [], []
    with torch.no_grad():
        for batch in loader:
            ids    = batch["input_ids"].to(DEVICE)
            mask   = batch["attention_mask"].to(DEVICE)
            with torch.cuda.amp.autocast(enabled=CFG["fp16"]):
                logits = model(ids, mask).cpu()
            probs  = torch.sigmoid(logits)
            preds  = (probs > 0.5).long()
            all_preds.extend(preds.tolist())
            all_labels.extend(batch["label"].long().tolist())
            all_probs.extend(probs.tolist())

    return {
        "f1":        f1_score(all_labels,        all_preds, zero_division=0),
        "acc":       accuracy_score(all_labels,  all_preds),
        "precision": precision_score(all_labels, all_preds, zero_division=0),
        "recall":    recall_score(all_labels,    all_preds, zero_division=0),
        "auc":       roc_auc_score(all_labels,   all_probs),
    }


# ── Training loop ──────────────────────────────────────────────────────────────
best_f1          = 0.0
epochs_no_improve = 0
log_lines        = []
start_time       = time.time()

print(f"{'Epoch':>6}  {'Loss':>7}  {'valF1':>7}  {'valAcc':>7}  {'valAUC':>7}  {'Time':>6}")
print("-" * 55)

for epoch in range(1, CFG["epochs"] + 1):
    model.train()
    total_loss  = 0.0
    epoch_start = time.time()

    pbar = tqdm(train_loader, desc=f"Ep {epoch:02d}/{CFG['epochs']}", leave=False)
    for batch in pbar:
        ids    = batch["input_ids"].to(DEVICE)
        mask   = batch["attention_mask"].to(DEVICE)
        labels = batch["label"].to(DEVICE)

        optimizer.zero_grad()
        with torch.cuda.amp.autocast(enabled=CFG["fp16"]):
            logits = model(ids, mask)
            loss   = criterion(logits, labels)

        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item()
        pbar.set_postfix(loss=f"{loss.item():.4f}")

    avg_loss    = total_loss / len(train_loader)
    val_m       = evaluate(val_loader)
    epoch_mins  = (time.time() - epoch_start) / 60

    line = (f"{epoch:6d}  {avg_loss:7.4f}  {val_m['f1']:7.4f}  "
            f"{val_m['acc']:7.4f}  {val_m['auc']:7.4f}  {epoch_mins:5.1f}m")
    print(line)
    log_lines.append(line)

    # Save best checkpoint
    if val_m["f1"] > best_f1:
        best_f1           = val_m["f1"]
        epochs_no_improve = 0
        torch.save(model.state_dict(), "best_model.pt")
    else:
        epochs_no_improve += 1

    # Early stopping
    if epochs_no_improve >= CFG["early_stop"]:
        print(f"\nEarly stopping at epoch {epoch} (no improvement for {CFG['early_stop']} epochs)")
        break

total_hrs = (time.time() - start_time) / 3600
print(f"\nBest val F1 : {best_f1:.4f}")
print(f"Total time  : {total_hrs:.2f} hrs")


# ── Test evaluation ────────────────────────────────────────────────────────────
model.load_state_dict(torch.load("best_model.pt", weights_only=True))
test_m = evaluate(test_loader)

print("\n" + "=" * 55)
print("TEST RESULTS — baseline_codebert (full Devign)")
print("=" * 55)
print(f"  F1        : {test_m['f1']:.4f}")
print(f"  Accuracy  : {test_m['acc']:.4f}")
print(f"  Precision : {test_m['precision']:.4f}")
print(f"  Recall    : {test_m['recall']:.4f}")
print(f"  AUC-ROC   : {test_m['auc']:.4f}")
print("=" * 55)

# Save results
with open("test_results.json", "w") as f:
    json.dump({"model": "baseline_codebert", "dataset": "devign", **test_m}, f, indent=2)

with open("train_log.txt", "w") as f:
    f.write("\n".join(log_lines))

print("\nSaved: best_model.pt | train_log.txt | test_results.json")
print(f"Estimated cost at $0.60/hr: ${total_hrs * 0.60:.2f}")
