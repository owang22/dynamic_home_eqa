#!/bin/bash
# Re-run of the ATYPICAL (conf) leg of the active anon experiment. The first
# attempt crashed on an unmapped object: env.household_queries draws typical
# objects from by_obj UNION init, and a static object ("keys") was absent from
# the anon map domain. The typ leg completed and is NOT re-run -- receptacle ids
# derive only from h["cands"], which the fix does not touch, so those rows stay
# valid (only object-id numbering shifts, and objects are prompt-side only).
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
run_model () {
  local M="$1" L="$2" TAU="$3" ALPHA="$4"; shift 4
  echo "=== [$(date +%H:%M)] serving $M ==="
  bash scratch_runs/serve_model.sh "$M" "$@" || { echo "SKIP $L"; return 1; }
  $PY -m dynbelief.two_capacities.run2 --bank conf --arm llm_scaffold \
      --tau "$TAU" --alpha "$ALPHA" --endpoint http://127.0.0.1:8400 \
      --model "$M" --anon --tag "anon_${L}" || echo "RUNFAIL conf $L"
  echo "=== [$(date +%H:%M)] anon-active conf $L done ==="
}
run_model "deepseek-ai/DeepSeek-V4-Flash" deepseek 0.45 2.72 --kv-cache-dtype fp8 --moe-backend triton_unfused
run_model "Qwen/Qwen3.6-35B-A3B-FP8"      qwen36   0.70 2.75 --moe-backend triton --enforce-eager
run_model "zai-org/GLM-4.5-Air"           glm      0.70 0.65 --moe-backend triton --enforce-eager
echo ANON_ACTIVE_CONF_COMPLETE
