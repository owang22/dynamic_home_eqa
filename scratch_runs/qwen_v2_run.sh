#!/bin/bash
# env-driven: no machine-specific paths. `source env.sh` provides PY, HSSD_DIR, endpoint.
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source env.sh
GENERATION_ENDPOINT="$GENERATION_ENDPOINT" HSSD_DIR="$HSSD_DIR" DYNAMIC_EQA_HF_HOME="$DYNAMIC_EQA_HF_HOME" \
  "$PY" scratch_runs/qwen_v2_bank.py > scratch_runs/qwen_v2.log 2>&1
echo "QWEN_V2_DONE $(date)" > scratch_runs/QWEN_V2_DONE.marker
