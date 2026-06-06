#!/bin/bash
# Run VulGCL preprocessing on Aliyun DSW.
# Uses nohup — safe to close the terminal after starting.
#
# Usage:  bash scripts/run_preprocess.sh
# Watch:  tail -f /mnt/workspace/VulGCL/preprocess.log

export JOERN_WORKSPACE=/mnt/workspace/VulGCL/joern_ws
export HF_ENDPOINT=https://hf-mirror.com
export PATH=/mnt/workspace/joern-cli:$PATH

cd /mnt/workspace/VulGCL

# Adjust --workers to your instance's vCPU count (use n_vcpu - 2)
# e.g. 8-core instance → --workers 6
WORKERS=${1:-6}

echo "Starting preprocessing with ${WORKERS} workers..."
echo "Log: /mnt/workspace/VulGCL/preprocess.log"
echo "To watch progress: tail -f preprocess.log"
echo ""

nohup python src/data/preprocess.py --workers "${WORKERS}" \
    > /mnt/workspace/VulGCL/preprocess.log 2>&1 &

echo "PID: $!"
echo $! > /mnt/workspace/VulGCL/preprocess.pid
echo "PID saved to preprocess.pid"
