"""Convert a networkx PDG → 3-channel centrality image for the CNN branch.

Approach (VulCNN-inspired, upgraded with CodeBERT):

  VulCNN (original):
    channel_k[node] = centrality_k(node) × sent2vec(node.code)
    Image shape: (3, N_nodes, sent2vec_dim) → resize → (3, 100, 100)

  Ours (improvement):
    channel_k[node] = centrality_k(node) × CodeBERT_CLS(node.code)
    Image shape: (3, N_nodes, 768) → resize → (3, 100, 100)

  Each row of the image = one statement.
  The value at each column = how semantically meaningful this statement is
  (CodeBERT embedding) × how important it is in the dependency graph (centrality).
  CNN learns which statement patterns, weighted by graph importance, signal a vulnerability.

  Why CodeBERT > sent2vec:
    sent2vec is a lightweight general-purpose sentence encoder.
    CodeBERT is pretrained on 6M (code, doc) pairs — it understands that
    strcpy is dangerous, malloc must be paired with free, etc.

  Pre-computed node_embeddings can be passed in from pdg_to_pyg() to avoid
  running CodeBERT twice (graph branch already computes them).

  MAX_NODES: functions with more than MAX_NODES PDG nodes are truncated.
  Extremely large functions (1000+ nodes) produce near-zero centrality images
  (edge density < 0.1%) and require prohibitive memory for CodeBERT batching.
"""

import numpy as np
import networkx as nx
import torch
import torch.nn.functional as F


IMAGE_SIZE = 100   # fixed CNN input size
MAX_NODES  = 150   # truncate functions larger than this

_TOKENIZER = None
_MODEL     = None


def _get_codebert(device: str = "cpu"):
    global _TOKENIZER, _MODEL
    if _TOKENIZER is None:
        from transformers import AutoTokenizer, AutoModel
        _TOKENIZER = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        _MODEL     = AutoModel.from_pretrained("microsoft/codebert-base")
        _MODEL.eval()
    return _TOKENIZER, _MODEL.to(device)


def _embed_nodes(G: nx.DiGraph, nodes: list, device: str) -> torch.Tensor:
    """CodeBERT [CLS] embedding for each node's code statement. Returns (N, 768)."""
    tokenizer, model = _get_codebert(device)
    codes = [G.nodes[nid].get("code", "") for nid in nodes]
    enc   = tokenizer(
        codes,
        return_tensors="pt",
        max_length=128,
        truncation=True,
        padding="max_length",
    )
    with torch.no_grad():
        out = model(
            input_ids=enc["input_ids"].to(device),
            attention_mask=enc["attention_mask"].to(device),
        )
    return out.last_hidden_state[:, 0, :].cpu()   # (N, 768)


def pdg_to_image(
    G: nx.DiGraph,
    node_embeddings: torch.Tensor = None,
    device: str = "cpu",
) -> torch.Tensor:
    """
    Convert a PDG DiGraph to a (3, IMAGE_SIZE, IMAGE_SIZE) float tensor.

    Args:
        G               : networkx DiGraph from extract_pdg()
        node_embeddings : optional pre-computed (N, 768) tensor from pdg_to_pyg()
                          pass this to avoid running CodeBERT a second time
        device          : used only if computing embeddings from scratch

    Returns:
        Tensor shape (3, IMAGE_SIZE, IMAGE_SIZE), values in [0, 1]
    """
    n = G.number_of_nodes()
    if n == 0:
        return torch.zeros(3, IMAGE_SIZE, IMAGE_SIZE)

    nodes = list(G.nodes())

    # Truncate oversized functions
    if n > MAX_NODES:
        nodes = nodes[:MAX_NODES]
        n     = MAX_NODES

    # ── Node embeddings ────────────────────────────────────────────────────
    if node_embeddings is not None:
        emb = node_embeddings[:n].float()         # reuse from graph branch
    else:
        emb = _embed_nodes(G, nodes, device)      # compute fresh

    emb_np = emb.numpy()                          # (N, 768)

    # ── Centrality scores ─────────────────────────────────────────────────
    deg   = nx.degree_centrality(G)
    close = nx.closeness_centrality(G)
    try:
        katz = nx.katz_centrality(G, alpha=0.01, max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        katz = {nid: 0.0 for nid in nodes}

    # ── Build 3 channels: centrality × embedding per node ─────────────────
    # Each channel: (N, 768) — rows = statements, cols = embedding dims
    channels = []
    for c_dict in [deg, close, katz]:
        scores  = np.array(
            [c_dict.get(nid, 0.0) for nid in nodes], dtype=np.float32
        ).reshape(-1, 1)                          # (N, 1)
        channel = scores * emb_np                 # (N, 768) broadcast
        channels.append(channel)

    mat = np.stack(channels, axis=0)              # (3, N, 768)

    # Normalise each channel to [0, 1]
    for ch in range(3):
        mx = np.abs(mat[ch]).max()
        if mx > 0:
            mat[ch] /= mx

    # ── Resize to (3, IMAGE_SIZE, IMAGE_SIZE) ─────────────────────────────
    tensor  = torch.from_numpy(mat).unsqueeze(0)  # (1, 3, N, 768)
    resized = F.interpolate(
        tensor,
        size=(IMAGE_SIZE, IMAGE_SIZE),
        mode="bilinear",
        align_corners=False,
    ).squeeze(0)                                   # (3, 100, 100)

    return resized


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

    device          = "mps" if torch.backends.mps.is_available() else "cpu"
    CHANNEL_NAMES   = ["Degree × CodeBERT", "Closeness × CodeBERT", "Katz × CodeBERT"]

    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    fig.suptitle(
        "PDG Centrality Images (VulCNN approach + CodeBERT)\nVulnerable vs Safe",
        fontsize=13,
    )

    for row, (name, code) in enumerate([("VULNERABLE", VULNERABLE), ("SAFE", SAFE)]):
        print(f"--- {name} ---")
        G   = extract_pdg(code, project_name=f"img2_{name.lower()}")
        print(f"  PDG: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        img = pdg_to_image(G, device=device)
        print(f"  Image shape : {list(img.shape)}")
        for ch, cname in enumerate(CHANNEL_NAMES):
            d = img[ch]
            print(f"  {cname}: min={d.min():.3f}  max={d.max():.3f}  mean={d.mean():.4f}")

        for ch, cname in enumerate(CHANNEL_NAMES):
            ax = axes[row, ch]
            ax.imshow(img[ch].numpy(), cmap="hot", vmin=0, vmax=1)
            ax.set_title(f"{name}\n{cname}")
            ax.axis("off")
        print()

    plt.tight_layout()
    out_dir  = os.path.join(os.path.dirname(__file__), "../../docs/figures")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "pdg_codebert_images.png")
    plt.savefig(out_path, dpi=150)
    print(f"Saved → docs/figures/pdg_codebert_images.png")
