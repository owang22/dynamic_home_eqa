#!/bin/bash
# Anonymization confirmatory with the FIXED llm_anon scoring, on Qwen + GLM
# (DeepSeek already re-run as confirm_rows_deepseek-anonfix).
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
run_one () {
  local M="$1" L="$2"; shift 2
  echo "=== [$(date +%H:%M)] serving $M ==="
  bash scratch_runs/serve_model.sh "$M" "$@" || { echo "SKIP $L"; return 1; }
  echo "=== [$(date +%H:%M)] anon confirmatory: $L ==="
  $PY -m dynbelief.h2.confirm --model "$M" --label "$L" || echo "FAIL $L"
}
run_one "Qwen/Qwen3.6-35B-A3B-FP8" qwen36-anonfix --moe-backend triton --enforce-eager
run_one "zai-org/GLM-4.5-Air"      glm-anonfix    --moe-backend triton --enforce-eager
echo ANON_MULTIMODEL_COMPLETE
