"""Evaluate a trained model on the Devign test set.

Usage:
    python src/training/evaluate.py --config experiments/configs/baseline_codebert.yaml
    python src/training/evaluate.py --config experiments/configs/prototype_codebert.yaml \
                                    --checkpoint experiments/checkpoints/prototype_codebert/best.pt
"""

import argparse
import json
import sys
import torch
import yaml
from pathlib import Path

sys.path.insert(0, ".")
from src.data.dataset import VulDataset
from src.training.train import LLMClassifier, evaluate, get_device
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main(config_path: str, checkpoint_path: str = None):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    name   = cfg["name"]
    device = get_device()

    # Default checkpoint location
    if checkpoint_path is None:
        checkpoint_path = str(PROJECT_ROOT / "experiments" / "checkpoints" / name / "best.pt")

    print(f"Config     : {config_path}")
    print(f"Checkpoint : {checkpoint_path}")
    print(f"Device     : {device}\n")

    data_dir    = PROJECT_ROOT / "data" / "devign" / "raw"
    max_seq_len = cfg["data"].get("max_seq_len", 512)
    model_name  = cfg["model"]["llm"].get("model_name", "microsoft/codebert-base")

    test_ds = VulDataset("test", str(data_dir),
                         max_seq_len=max_seq_len, model_name=model_name)
    loader  = DataLoader(test_ds, batch_size=cfg["training"]["batch_size"],
                         shuffle=False, num_workers=0)

    hidden_dim = cfg["model"]["llm"]["hidden_dim"]
    dropout    = cfg["model"].get("dropout", 0.1)

    model = LLMClassifier(hidden_dim, dropout, model_name).to(device)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device,
                                     weights_only=True))

    metrics = evaluate(model, loader, device)

    print(f"{'='*60}")
    print(f"TEST RESULTS — {name}")
    print(f"{'='*60}")
    print(f"  F1        : {metrics['f1']:.4f}")
    print(f"  Accuracy  : {metrics['acc']:.4f}")
    print(f"  Precision : {metrics['precision']:.4f}")
    print(f"  Recall    : {metrics['recall']:.4f}")
    print(f"  AUC-ROC   : {metrics['auc']:.4f}")
    print(f"{'='*60}")

    out = PROJECT_ROOT / "experiments" / "results" / name / "metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump({"config": name, **metrics}, f, indent=2)
    print(f"\nSaved → experiments/results/{name}/metrics.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",     required=True)
    parser.add_argument("--checkpoint", default=None)
    args = parser.parse_args()
    main(args.config, args.checkpoint)
