#!/bin/bash
# Confirmatory re-run of scaffold_fusion at PER-MODEL (tau*, alpha*), replacing
# the runs that used DeepSeek's frozen tau=0.45 / alpha=6.07 for every model.
# Waits for the DeepSeek typical + anon jobs so the GPUs are free.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
until grep -q "ANON_RERUN_COMPLETE\|SERVE FAILED" scratch_runs/anon_rerun.log 2>/dev/null; do sleep 60; done

run_one () {  # run_one <hf_id> <tag> <tau> <alpha> <serve args...>
  local M="$1" T="$2" TAU="$3" AL="$4"; shift 4
  echo "=== [$(date +%H:%M)] serving $M ==="
  bash scratch_runs/serve_model.sh "$M" "$@" || { echo "SKIP $T"; return 1; }
  echo "=== [$(date +%H:%M)] $T scaffold_fusion tau=$TAU alpha=$AL ==="
  $PY -m dynbelief.two_capacities.run2 --bank conf --arm scaffold_fusion \
      --tau "$TAU" --alpha "$AL" --model "$M" --tag "permodel_$T" || echo "FAIL $T"
}
run_one "Qwen/Qwen3.6-35B-A3B-FP8" qwen36 0.70 2.75 --moe-backend triton --enforce-eager
run_one "zai-org/GLM-4.5-Air"      glm    0.70 0.65 --moe-backend triton --enforce-eager
run_one "deepseek-ai/DeepSeek-V4-Flash" deepseek 0.45 2.72 --kv-cache-dtype fp8 --moe-backend triton_unfused
echo PERMODEL_RERUN_COMPLETE
