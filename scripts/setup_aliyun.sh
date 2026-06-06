#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# VulGCL — Aliyun DSW setup + preprocess runner
# Run once in a DSW terminal after uploading the project zip.
#
# Usage:
#   bash scripts/setup_aliyun.sh
#
# Assumes:
#   - You are in /mnt/workspace/VulGCL/  (project root)
#   - DSW instance: 8+ vCPU, 32GB RAM  (CPU instance for Phase 1)
#   - For Phase 2 (CodeBERT): GPU instance recommended
# ─────────────────────────────────────────────────────────────────────────────
set -e

WORKSPACE=/mnt/workspace/VulGCL
JOERN_DIR=/mnt/workspace/joern-cli
JOERN_VERSION="2.0.406"

echo "============================================================"
echo " VulGCL Aliyun DSW Setup"
echo "============================================================"

# ── 1. Java ───────────────────────────────────────────────────────────────────
echo "[1/5] Installing Java 11..."
apt-get update -qq && apt-get install -y -qq default-jdk-headless
java -version

# ── 2. Joern ──────────────────────────────────────────────────────────────────
echo "[2/5] Installing Joern ${JOERN_VERSION}..."
if [ ! -f "${JOERN_DIR}/joern" ]; then
    cd /mnt/workspace
    wget -q "https://github.com/joernio/joern/releases/download/v${JOERN_VERSION}/joern-cli.zip" \
         -O joern-cli.zip
    unzip -q joern-cli.zip
    rm joern-cli.zip
    chmod +x joern-cli/joern joern-cli/joern-parse joern-cli/joern-export
    mv joern-cli "${JOERN_DIR}"
    echo "Joern installed at ${JOERN_DIR}"
else
    echo "Joern already installed — skipping"
fi

export PATH="${JOERN_DIR}:${PATH}"
echo "export PATH=${JOERN_DIR}:\$PATH" >> ~/.bashrc
joern --version

# ── 3. Python packages ────────────────────────────────────────────────────────
echo "[3/5] Installing Python packages..."
# Use Tsinghua mirror for speed inside China
pip install -q \
    torch torchvision \
    transformers datasets \
    torch-geometric \
    torch-scatter torch-sparse \
    networkx tqdm scikit-learn \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# ── 4. Environment variables ──────────────────────────────────────────────────
echo "[4/5] Setting environment variables..."
export JOERN_WORKSPACE=/mnt/workspace/VulGCL/joern_ws
export HF_ENDPOINT=https://hf-mirror.com   # HuggingFace mirror for China
mkdir -p "${JOERN_WORKSPACE}"

# Persist across terminal sessions
cat >> ~/.bashrc << 'EOF'
export JOERN_WORKSPACE=/mnt/workspace/VulGCL/joern_ws
export HF_ENDPOINT=https://hf-mirror.com
export PATH=/mnt/workspace/joern-cli:$PATH
EOF

# ── 5. Smoke test ─────────────────────────────────────────────────────────────
echo "[5/5] Smoke test — one function through Joern..."
cd "${WORKSPACE}"
python3 - << 'PYEOF'
import sys
sys.path.insert(0, ".")
import json, os
os.environ["JOERN_WORKSPACE"] = "/mnt/workspace/VulGCL/joern_ws"
from src.data.build_pdg import extract_pdg

test_func = """
void foo(char *src) {
    char buf[64];
    strcpy(buf, src);
}
"""
G = extract_pdg(test_func, project_name="smoke_test")
print(f"Joern OK — nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
PYEOF

echo ""
echo "============================================================"
echo " Setup complete. Now run:"
echo ""
echo "   cd ${WORKSPACE}"
echo "   export JOERN_WORKSPACE=/mnt/workspace/VulGCL/joern_ws"
echo "   export HF_ENDPOINT=https://hf-mirror.com"
echo "   nohup python src/data/preprocess.py --workers 8 > preprocess.log 2>&1 &"
echo "   tail -f preprocess.log"
echo "============================================================"
