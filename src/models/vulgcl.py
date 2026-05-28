"""VulGCL: Multimodal vulnerability detection (Graph + CNN + LLM)."""
import torch
import torch.nn as nn
from .graph_branch import GraphBranch
from .image_branch import ImageBranch
from .llm_branch import LLMBranch


class VulGCL(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.graph_branch = GraphBranch(cfg.graph)
        self.image_branch = ImageBranch(cfg.image)
        self.llm_branch   = LLMBranch(cfg.llm)

        fused_dim = cfg.graph.hidden_dim + cfg.image.hidden_dim + cfg.llm.hidden_dim
        self.classifier = nn.Sequential(
            nn.Linear(fused_dim, 256),
            nn.ReLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(256, 1),
        )

    def forward(self, graph, image, input_ids, attention_mask):
        h_g = self.graph_branch(graph)
        h_i = self.image_branch(image)
        h_l = self.llm_branch(input_ids, attention_mask)

        fused = torch.cat([h_g, h_i, h_l], dim=-1)
        return self.classifier(fused).squeeze(-1)
