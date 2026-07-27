#!/bin/bash
# Anonymization LEARNING CURVE (accuracy vs days of evidence) for 3 models.
# Also completes the single-point anon confirmatory for GLM, whose leg died when
# the previous session's process group was torn down.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
run_one () {
  local M="$1" L="$2" ALSO_POINT="$3"; shift 3
  echo "=== [$(date +%H:%M)] serving $M ==="
  bash scratch_runs/serve_model.sh "$M" "$@" || { echo "SKIP $L"; return 1; }
  if [ "$ALSO_POINT" = "yes" ]; then
    echo "=== [$(date +%H:%M)] single-point anon: $L-anonfix ==="
    $PY -m dynbelief.h2.confirm --model "$M" --label "$L-anonfix" || echo "FAIL point $L"
  fi
  echo "=== [$(date +%H:%M)] anon CURVE: $L ==="
  $PY -m dynbelief.h2.confirm_curve --model "$M" --label "$L" || echo "FAIL curve $L"
  echo "=== [$(date +%H:%M)] $L DONE ==="
}
run_one "deepseek-ai/DeepSeek-V4-Flash" deepseek no  --kv-cache-dtype fp8 --moe-backend triton_unfused
run_one "Qwen/Qwen3.6-35B-A3B-FP8"      qwen36   no  --moe-backend triton --enforce-eager
run_one "zai-org/GLM-4.5-Air"           glm      yes --moe-backend triton --enforce-eager
echo ANON_CURVE_COMPLETE
