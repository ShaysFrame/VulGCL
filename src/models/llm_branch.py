"""LLM branch: code text → CodeBERT [CLS] → embedding."""
import torch.nn as nn
from transformers import RobertaModel


class LLMBranch(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.encoder = RobertaModel.from_pretrained("microsoft/codebert-base")
        self.proj = nn.Linear(768, cfg.hidden_dim)

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = out.last_hidden_state[:, 0, :]  # [CLS] token
        return self.proj(cls)
