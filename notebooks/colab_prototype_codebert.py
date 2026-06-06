# ============================================================
# VulGCL — Prototype: CodeBERT-only baseline on 10% Devign
# Run this on Google Colab (free T4 GPU, ~5 minutes)
#
# Steps:
#   1. Open https://colab.research.google.com
#   2. File → New notebook
#   3. Paste each cell block below into a separate Colab cell
#   4. Runtime → Change runtime type → T4 GPU
#   5. Run all cells top to bottom
# ============================================================


# ── CELL 1: Install dependencies ─────────────────────────────────────────────
# Paste and run this first

"""
!pip install -q transformers datasets scikit-learn tqdm
"""


# ── CELL 2: Imports and config ────────────────────────────────────────────────

"""
import json, random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, RobertaModel
from sklearn.metrics import f1_score, roc_auc_score, accuracy_score, precision_score, recall_score
from datasets import load_dataset
from tqdm import tqdm

# Config — mirrors experiments/configs/prototype_codebert.yaml
CFG = {
    "name":        "prototype_codebert",
    "hidden_dim":  256,
    "dropout":     0.3,
    "model_name":  "microsoft/codebert-base",
    "epochs":      3,
    "batch_size":  16,
    "lr":          2e-5,
    "max_seq_len": 512,
    "frac":        0.1,   # 10% of train set
    "seed":        42,
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

set_seed(CFG["seed"])
"""


# ── CELL 3: Load Devign from HuggingFace ─────────────────────────────────────

"""
print("Downloading Devign from HuggingFace...")
raw = load_dataset("DetectVul/devign")
print(raw)

def to_rows(split):
    rows = []
    for item in raw[split]:
        rows.append({"func": item["func"], "label": float(item["target"])})
    return rows

train_rows = to_rows("train")
val_rows   = to_rows("validation")
test_rows  = to_rows("test")

# Take 10% of train
rng = random.Random(CFG["seed"])
train_rows = rng.sample(train_rows, int(len(train_rows) * CFG["frac"]))

print(f"Train: {len(train_rows)} | Val: {len(val_rows)} | Test: {len(test_rows)}")
"""


# ── CELL 4: Dataset and DataLoader ───────────────────────────────────────────

"""
tokenizer = AutoTokenizer.from_pretrained(CFG["model_name"])

class DevignTextDataset(Dataset):
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

train_loader = DataLoader(DevignTextDataset(train_rows), batch_size=CFG["batch_size"], shuffle=True)
val_loader   = DataLoader(DevignTextDataset(val_rows),   batch_size=CFG["batch_size"], shuffle=False)
test_loader  = DataLoader(DevignTextDataset(test_rows),  batch_size=CFG["batch_size"], shuffle=False)
print("Dataloaders ready")
"""


# ── CELL 5: Model ─────────────────────────────────────────────────────────────

"""
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
        cls = out.last_hidden_state[:, 0, :]   # [CLS] token
        h   = self.proj(cls)
        return self.classifier(h).squeeze(-1)

model = LLMClassifier().to(DEVICE)

optimizer = torch.optim.AdamW([
    {"params": model.encoder.parameters(), "lr": CFG["lr"]},
    {"params": model.proj.parameters(),    "lr": CFG["lr"] * 10},
    {"params": model.classifier.parameters(), "lr": CFG["lr"] * 10},
], weight_decay=1e-4)

criterion = nn.BCEWithLogitsLoss()
print(f"Model loaded — {sum(p.numel() for p in model.parameters())/1e6:.1f}M parameters")
"""


# ── CELL 6: Eval function ─────────────────────────────────────────────────────

"""
def evaluate(model, loader):
    model.eval()
    all_preds, all_labels, all_probs = [], [], []
    with torch.no_grad():
        for batch in loader:
            ids    = batch["input_ids"].to(DEVICE)
            mask   = batch["attention_mask"].to(DEVICE)
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
"""


# ── CELL 7: Training loop ─────────────────────────────────────────────────────

"""
best_f1, best_state = 0.0, None

for epoch in range(1, CFG["epochs"] + 1):
    model.train()
    total_loss = 0.0
    pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{CFG['epochs']}", leave=True)

    for batch in pbar:
        ids    = batch["input_ids"].to(DEVICE)
        mask   = batch["attention_mask"].to(DEVICE)
        labels = batch["label"].to(DEVICE)

        optimizer.zero_grad()
        logits = model(ids, mask)
        loss   = criterion(logits, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += loss.item()
        pbar.set_postfix(loss=f"{loss.item():.4f}")

    avg_loss = total_loss / len(train_loader)
    val_m    = evaluate(model, val_loader)
    print(f"Epoch {epoch:02d}  loss={avg_loss:.4f}  val_F1={val_m['f1']:.4f}  "
          f"val_Acc={val_m['acc']:.4f}  val_AUC={val_m['auc']:.4f}")

    if val_m["f1"] > best_f1:
        best_f1    = val_m["f1"]
        best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

print(f"\nBest val F1: {best_f1:.4f}")
"""


# ── CELL 8: Test evaluation ───────────────────────────────────────────────────

"""
model.load_state_dict({k: v.to(DEVICE) for k, v in best_state.items()})
test_m = evaluate(model, test_loader)

print("=" * 50)
print("TEST RESULTS — prototype_codebert (10% train, 3 epochs)")
print("=" * 50)
print(f"  F1        : {test_m['f1']:.4f}")
print(f"  Accuracy  : {test_m['acc']:.4f}")
print(f"  Precision : {test_m['precision']:.4f}")
print(f"  Recall    : {test_m['recall']:.4f}")
print(f"  AUC-ROC   : {test_m['auc']:.4f}")
print("=" * 50)
print()
print("NEXT STEPS:")
print(f"  - If F1 > 0.60 → CodeBERT baseline is solid, proceed to full pipeline")
print(f"  - Full baseline_codebert (100% data, 20 epochs) expected F1 ~0.64–0.68")
print(f"  - VulGCL full model must beat this by ≥ 2 F1 points to justify multimodal design")
"""
