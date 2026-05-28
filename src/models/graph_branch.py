"""Graph branch: PDG → GNN → embedding."""
import torch.nn as nn
from torch_geometric.nn import GATConv, global_mean_pool


class GraphBranch(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.convs = nn.ModuleList([
            GATConv(cfg.in_dim if i == 0 else cfg.hidden_dim, cfg.hidden_dim)
            for i in range(cfg.num_layers)
        ])
        self.relu = nn.ReLU()

    def forward(self, data):
        x, edge_index, batch = data.x, data.edge_index, data.batch
        for conv in self.convs:
            x = self.relu(conv(x, edge_index))
        return global_mean_pool(x, batch)
