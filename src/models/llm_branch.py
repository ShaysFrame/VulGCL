"""LLM branch: code text → CodeBERT [CLS] → embedding."""
import torch
import torch.nn as nn
from transformers import RobertaModel, AutoTokenizer


class LLMBranch(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.encoder = RobertaModel.from_pretrained("microsoft/codebert-base")
        self.proj = nn.Linear(768, cfg.hidden_dim)

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = out.last_hidden_state[:, 0, :]  # [CLS] token
        return self.proj(cls)


if __name__ == "__main__":
    # ── Two real functions: one vulnerable, one safe ───────────────────────────
    VULNERABLE = """
    void copy_input(char *user_input) {
        char buf[64];
        strcpy(buf, user_input);  // no bounds check — buffer overflow
    }
    """

    SAFE = """
    void copy_input(char *user_input) {
        char buf[64];
        strncpy(buf, user_input, sizeof(buf) - 1);
        buf[sizeof(buf) - 1] = '\\0';  // properly bounds-checked
    }
    """

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}\n")

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

    class Cfg:
        hidden_dim = 256

    model = LLMBranch(Cfg()).to(device)
    model.eval()

    for label, code in [("VULNERABLE", VULNERABLE), ("SAFE", SAFE)]:
        tokens = tokenizer(
            code,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding="max_length",
        )
        input_ids      = tokens["input_ids"].to(device)
        attention_mask = tokens["attention_mask"].to(device)

        with torch.no_grad():
            h_l = model(input_ids, attention_mask)

        print(f"[{label}]")
        print(f"  input_ids shape     : {input_ids.shape}  (1 function, 512 tokens)")
        print(f"  h_L shape           : {h_l.shape}        (1 function, 256-dim embedding)")
        print(f"  h_L[:5] values      : {h_l[0, :5].tolist()}")
        print(f"  h_L norm            : {h_l.norm().item():.4f}")
        print(f"  Cosine sim to other : (run both to compare)\n")
