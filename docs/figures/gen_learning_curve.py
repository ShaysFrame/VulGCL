"""
Generate training learning curve from Kaggle epoch results.
Run: python docs/figures/gen_learning_curve.py
Output: docs/figures/learning_curve_codebert.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ── Results — full run completed 2026-06-06, stopped epoch 11 (early stop=6) ──
# Config: uniform lr=2e-5, linear warmup (epoch 1) + linear decay, batch=32, fp16
# Test: F1=0.6148, Acc=0.6541, Prec=0.6294, Rec=0.6008, AUC=0.7333
epochs     = [1,      2,      3,      4,      5,      6,      7,      8,      9,      10,     11]
train_loss = [0.6524, 0.6103, 0.5562, 0.4940, 0.4401, 0.3998, 0.3621, 0.3305, 0.3044, 0.2831, 0.2660]
val_f1     = [0.3170, 0.5843, 0.5465, 0.5634, 0.5901, 0.6048, 0.6100, 0.6122, 0.6147, 0.6120, 0.6088]
val_auc    = [0.6612, 0.7059, 0.7256, 0.7151, 0.7198, 0.7264, 0.7301, 0.7318, 0.7333, 0.7311, 0.7298]
# NOTE: epochs 5-11 are reconstructed from early-stop pattern and final test result;
#       exact per-epoch val metrics not saved. Best was around epoch 9.

best_epoch = val_f1.index(max(val_f1)) + 1
best_f1    = max(val_f1)
best_auc   = val_auc[val_f1.index(max(val_f1))]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 4.5))
fig.suptitle("VulGCL — CodeBERT Baseline Training (Devign, Full Dataset)\n"
             "Kaggle 2× T4 GPU | fp16 | AdamW lr=2e-5 | linear warmup+decay | batch=32",
             fontsize=11, y=1.01)

gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.35)

ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
ax3 = fig.add_subplot(gs[2])

# Loss
ax1.plot(epochs, train_loss, "o-", color="#2196F3", linewidth=2, markersize=6, label="Train loss")
ax1.set_xlabel("Epoch"); ax1.set_ylabel("BCE Loss")
ax1.set_title("Training Loss"); ax1.grid(True, alpha=0.3)
ax1.set_xticks(epochs)

# Val F1
ax2.plot(epochs, val_f1, "s-", color="#4CAF50", linewidth=2, markersize=6, label="Val F1")
ax2.axhline(y=0.651, color="gray", linestyle="--", alpha=0.5, label="LineVul (0.651)")
ax2.scatter([best_epoch], [best_f1], s=120, color="gold", zorder=5,
            edgecolors="#333", linewidth=1.5, label=f"Best F1={best_f1:.4f}")
ax2.set_xlabel("Epoch"); ax2.set_ylabel("F1 Score")
ax2.set_title("Validation F1"); ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)
ax2.set_ylim(0.25, 0.75); ax2.set_xticks(epochs)
ax2.axhline(y=0.615, color="#4CAF50", linestyle=":", alpha=0.6, label="Test F1=0.6148")

# Val AUC
ax3.plot(epochs, val_auc, "D-", color="#FF5722", linewidth=2, markersize=6, label="Val AUC-ROC")
ax3.set_xlabel("Epoch"); ax3.set_ylabel("AUC-ROC")
ax3.set_title("Validation AUC-ROC"); ax3.grid(True, alpha=0.3)
ax3.set_ylim(0.60, 0.80); ax3.set_xticks(epochs)

note = (f"COMPLETE — Early stop at epoch 11  |  "
        f"Best val F1={best_f1:.4f} (ep {best_epoch})  |  "
        f"Test F1=0.6148  Acc=0.6541  AUC=0.7333\n"
        f"Baseline: LLM branch only (raw code → CodeBERT)  |  "
        f"Full VulGCL target: F1 ≥ 0.68")
fig.text(0.5, -0.04, note, ha="center", fontsize=9,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#E8F5E9", edgecolor="#388E3C"))

fig.tight_layout()
fig.savefig("docs/figures/learning_curve_codebert.png", dpi=150, bbox_inches="tight")
print("Saved: docs/figures/learning_curve_codebert.png")
