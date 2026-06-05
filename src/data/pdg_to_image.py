"""Convert a networkx PDG → 3-channel centrality image for the CNN branch.

Approach (from VulCNN):
  1. Compute 3 centrality scores per node: degree, Katz, closeness.
  2. Build a (N×N) matrix for each centrality:
       matrix[i][j] = centrality(i)  if edge i→j exists, else 0
  3. Stack → (3, N, N) tensor.
  4. Resize to (3, IMAGE_SIZE, IMAGE_SIZE) so the CNN gets a fixed-size input.

Why this works:
  High-centrality nodes that connect to dangerous sinks (like strcpy)
  create bright spots in the image. CNN learns to recognize these patterns
  the same way it recognises edges in photos.
"""

import numpy as np
import networkx as nx
import torch
import torch.nn.functional as F


IMAGE_SIZE = 100  # fixed output size for the CNN


def pdg_to_image(G: nx.DiGraph) -> torch.Tensor:
    """
    Convert a PDG DiGraph to a (3, IMAGE_SIZE, IMAGE_SIZE) float tensor.

    Returns zeros tensor if the graph is empty.
    """
    n = G.number_of_nodes()
    if n == 0:
        return torch.zeros(3, IMAGE_SIZE, IMAGE_SIZE)

    nodes = list(G.nodes())
    idx = {nid: i for i, nid in enumerate(nodes)}

    # ── Centrality computation ─────────────────────────────────────────────
    # Degree: fraction of all possible neighbours this node connects to
    deg = nx.degree_centrality(G)

    # Katz: weighted count of all paths reaching this node (shorter = higher weight)
    # alpha must be < 1/largest_eigenvalue; 0.01 is conservative and always safe
    try:
        katz = nx.katz_centrality(G, alpha=0.01, max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        katz = {nid: 0.0 for nid in nodes}

    # Closeness: how quickly this node can reach all others
    # For directed graphs networkx uses reachable nodes only
    close = nx.closeness_centrality(G)

    centralities = [deg, katz, close]

    # ── Build 3-channel N×N matrix ─────────────────────────────────────────
    mat = np.zeros((3, n, n), dtype=np.float32)

    for src, dst in G.edges():
        i, j = idx[src], idx[dst]
        for ch, c in enumerate(centralities):
            mat[ch, i, j] = c.get(src, 0.0)

    # ── Normalise each channel to [0, 1] ──────────────────────────────────
    for ch in range(3):
        mx = mat[ch].max()
        if mx > 0:
            mat[ch] /= mx

    # ── Resize to fixed IMAGE_SIZE × IMAGE_SIZE ────────────────────────────
    tensor = torch.from_numpy(mat).unsqueeze(0)          # (1, 3, N, N)
    resized = F.interpolate(
        tensor,
        size=(IMAGE_SIZE, IMAGE_SIZE),
        mode="bilinear",
        align_corners=False,
    ).squeeze(0)                                          # (3, H, W)

    return resized                                        # shape: (3, 100, 100)


if __name__ == "__main__":
    import os
    import sys
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, ".")
    from src.data.build_pdg import extract_pdg

    VULNERABLE = """
void copy_input(char *user_input) {
    char buf[64];
    strcpy(buf, user_input);
}
"""

    SAFE = """
void copy_input(char *user_input) {
    char buf[64];
    strncpy(buf, user_input, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\\0';
}
"""

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    CHANNEL_NAMES = ["Degree", "Katz", "Closeness"]

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    fig.suptitle("PDG Centrality Images — Vulnerable vs Safe", fontsize=14)

    for row, (name, code) in enumerate([("VULNERABLE", VULNERABLE), ("SAFE", SAFE)]):
        print(f"--- {name} ---")
        G = extract_pdg(code, project_name=f"img_{name.lower()}")
        print(f"  PDG: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        img = pdg_to_image(G)
        print(f"  Image shape: {img.shape}   (3 channels × {IMAGE_SIZE} × {IMAGE_SIZE})")
        print(f"  Channel stats:")
        for ch, cname in enumerate(CHANNEL_NAMES):
            ch_data = img[ch]
            print(f"    {cname:10s}: min={ch_data.min():.3f}  max={ch_data.max():.3f}  mean={ch_data.mean():.3f}")

        for ch, cname in enumerate(CHANNEL_NAMES):
            ax = axes[row, ch]
            ax.imshow(img[ch].numpy(), cmap="hot", vmin=0, vmax=1)
            ax.set_title(f"{name}\n{cname} centrality")
            ax.axis("off")
        print()

    plt.tight_layout()
    out_dir = os.path.join(os.path.dirname(__file__), "../../docs/figures")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "pdg_centrality_images.png")
    plt.savefig(out_path, dpi=150)
    print(f"Saved visualization to {out_path}")
    print("Open docs/figures/pdg_centrality_images.png to see how vulnerable and safe functions look different.")
