"""Image branch: PDG centrality image → CNN → embedding."""
import torch.nn as nn


class ImageBranch(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        # Input: (B, 3, H, W) — 3-channel PDG centrality image
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.fc = nn.Linear(64 * 4 * 4, cfg.hidden_dim)

    def forward(self, x):
        x = self.cnn(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)
