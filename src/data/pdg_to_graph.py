"""Convert a networkx PDG → PyTorch Geometric Data object.

Node features: CodeBERT [CLS] embedding of each statement's text (768-dim).
Edge index: directed edges from the PDG.
"""

import torch
import networkx as nx
from torch_geometric.data import Data
from transformers import AutoTokenizer, AutoModel


_TOKENIZER = None
_MODEL = None


def _get_codebert():
    global _TOKENIZER, _MODEL
    if _TOKENIZER is None:
        _TOKENIZER = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        _MODEL = AutoModel.from_pretrained("microsoft/codebert-base")
        _MODEL.eval()
    return _TOKENIZER, _MODEL


def pdg_to_pyg(
    G: nx.DiGraph,
    label: int = -1,
    device: str = "cpu",
) -> Data:
    """
    Convert a networkx PDG DiGraph to a torch_geometric.data.Data object.

    Args:
        G      : networkx DiGraph from build_pdg.extract_pdg()
        label  : 1 = vulnerable, 0 = safe, -1 = unknown
        device : 'cpu', 'mps', or 'cuda'

    Returns:
        Data with:
            x          shape (num_nodes, 768)  — CodeBERT embeddings
            edge_index shape (2, num_edges)    — directed PDG edges
            y          shape (1,)              — label
    """
    tokenizer, model = _get_codebert()
    model = model.to(device)

    nodes = list(G.nodes())
    node_to_idx = {nid: i for i, nid in enumerate(nodes)}

    # Collect statement text for each node
    codes = [G.nodes[nid].get("code", "") for nid in nodes]

    # Tokenize all statements in one batch
    encoding = tokenizer(
        codes,
        return_tensors="pt",
        max_length=128,      # statements are short — 128 is enough
        truncation=True,
        padding="max_length",
    )
    input_ids      = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    with torch.no_grad():
        out = model(input_ids=input_ids, attention_mask=attention_mask)
        # [CLS] token embedding for each statement
        x = out.last_hidden_state[:, 0, :]   # shape: (num_nodes, 768)

    # Build edge_index
    edges = list(G.edges())
    if edges:
        src = [node_to_idx[s] for s, _ in edges]
        dst = [node_to_idx[d] for _, d in edges]
        edge_index = torch.tensor([src, dst], dtype=torch.long, device=device)
    else:
        edge_index = torch.zeros((2, 0), dtype=torch.long, device=device)

    y = torch.tensor([label], dtype=torch.float, device=device)

    return Data(x=x.cpu(), edge_index=edge_index.cpu(), y=y.cpu())


if __name__ == "__main__":
    import sys
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
    print(f"Device: {device}\n")

    for name, code, lbl in [("VULNERABLE", VULNERABLE, 1), ("SAFE", SAFE, 0)]:
        print(f"--- {name} ---")
        print("  Extracting PDG (Joern)...")
        G = extract_pdg(code, project_name=f"test_{name.lower()}")
        print(f"  PDG: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        print("  Embedding nodes with CodeBERT...")
        data = pdg_to_pyg(G, label=lbl, device=device)

        print(f"  x shape         : {data.x.shape}      (nodes × 768)")
        print(f"  edge_index shape: {data.edge_index.shape}  (2 × edges)")
        print(f"  y               : {data.y.item()}  (label)")
        print(f"  x[0,:5]         : {data.x[0, :5].tolist()}")
        print()
