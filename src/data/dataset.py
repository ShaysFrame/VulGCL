"""VulDataset — loads Devign and returns tensors per training mode.

mode="llm_only": returns (input_ids, attention_mask, label)
                 No Joern needed — just tokenized function text.
                 Used for CodeBERT baseline and prototype experiments.

mode="full":     returns (graph_data, image_tensor, input_ids, attention_mask, label)
                 Requires preprocessed .pt cache from preprocess.py (Phase 4.2).
                 LLM input is the PDG-guided slice (top-10 central statements),
                 NOT the full function — making it an independent modality.
                 data_dir must point to data/devign/ (parent of raw/ and processed/).
"""

import json
import random
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer
from pathlib import Path


class VulDataset(Dataset):
    def __init__(
        self,
        split: str,
        data_dir: str,
        mode: str = "llm_only",
        max_seq_len: int = 512,
        frac: float = 1.0,
        seed: int = 42,
        model_name: str = "microsoft/codebert-base",
    ):
        """
        Args:
            split       : "train", "validation", or "test"
            data_dir    : path to data/devign/  (parent of raw/ and processed/)
            mode        : "llm_only" | "full"
            max_seq_len : max tokens for CodeBERT (512 for full function)
            frac        : fraction of split to use (0.1 = 10% for prototype)
            seed        : random seed for frac sampling
            model_name  : HuggingFace model name for tokenizer
        """
        self.mode        = mode
        self.max_seq_len = max_seq_len
        self.tokenizer   = AutoTokenizer.from_pretrained(model_name)

        data_dir = Path(data_dir)

        if mode == "llm_only":
            path = data_dir / "raw" / f"{split}.jsonl"
            rows = []
            with open(path) as f:
                for line in f:
                    row = json.loads(line)
                    rows.append({
                        "func":  row["func"],
                        "label": float(row["target"]),
                    })
            if frac < 1.0:
                rng  = random.Random(seed)
                rows = rng.sample(rows, max(1, int(len(rows) * frac)))
            self.rows = rows

        elif mode == "full":
            pt_dir = data_dir / "processed" / split
            pt_files = sorted(pt_dir.glob("*.pt"))
            if frac < 1.0:
                rng      = random.Random(seed)
                pt_files = rng.sample(pt_files, max(1, int(len(pt_files) * frac)))
            self.pt_files = pt_files

        else:
            raise ValueError(f"Unknown mode '{mode}'. Use 'llm_only' or 'full'.")

    def __len__(self):
        if self.mode == "llm_only":
            return len(self.rows)
        return len(self.pt_files)

    def __getitem__(self, idx):
        if self.mode == "llm_only":
            row = self.rows[idx]
            enc = self.tokenizer(
                row["func"],
                max_length=self.max_seq_len,
                truncation=True,
                padding="max_length",
                return_tensors="pt",
            )
            return {
                "input_ids":      enc["input_ids"].squeeze(0),
                "attention_mask": enc["attention_mask"].squeeze(0),
                "label":          torch.tensor(row["label"], dtype=torch.float),
            }

        # mode == "full"
        obj = torch.load(self.pt_files[idx], map_location="cpu", weights_only=False)

        # LLM branch: tokenize the PDG-guided slice (top-10 central statements)
        # Falls back to empty string if slice is missing (e.g. tiny functions)
        slice_text = obj.get("llm_slice", "") or ""
        enc = self.tokenizer(
            slice_text,
            max_length=self.max_seq_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )

        return {
            "graph":          obj["graph"],                          # PyG Data
            "image":          obj["image"],                          # (3, 100, 100)
            "input_ids":      enc["input_ids"].squeeze(0),           # (max_seq_len,)
            "attention_mask": enc["attention_mask"].squeeze(0),      # (max_seq_len,)
            "label":          torch.tensor(obj["label"], dtype=torch.float),
        }
