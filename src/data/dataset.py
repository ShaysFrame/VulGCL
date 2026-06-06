"""VulDataset — loads Devign and returns tensors per training mode.

mode="llm_only": returns (input_ids, attention_mask, label)
                 No Joern needed — just tokenized function text.
                 Used for CodeBERT baseline and prototype experiments.

mode="full":     returns (graph_data, image_tensor, input_ids, attention_mask, label)
                 Requires preprocessed PDG cache from Phase 4.2.
                 Used for full VulGCL training.
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
            data_dir    : path to data/devign/raw/
            mode        : "llm_only" | "full"
            max_seq_len : max tokens for CodeBERT (512 for full function)
            frac        : fraction of split to use (0.1 = 10% for prototype)
            seed        : random seed for frac sampling
            model_name  : HuggingFace model name for tokenizer
        """
        self.mode        = mode
        self.max_seq_len = max_seq_len

        path = Path(data_dir) / f"{split}.jsonl"
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

        self.rows      = rows
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        row = self.rows[idx]

        enc = self.tokenizer(
            row["func"],
            max_length=self.max_seq_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )

        return {
            "input_ids":      enc["input_ids"].squeeze(0),       # (max_seq_len,)
            "attention_mask": enc["attention_mask"].squeeze(0),  # (max_seq_len,)
            "label":          torch.tensor(row["label"], dtype=torch.float),
        }
