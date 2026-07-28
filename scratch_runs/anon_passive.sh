#!/bin/bash
# ANONYMIZED passive runs: llm_direct with every object/receptacle name mapped
# to object_N/receptacle_N (rooms hidden via receptacle ids). One anon run per
# model per bank; named LLM + classical baselines are reused from existing rows.
# WAITS for the v22 multimodel queue to finish.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
: # stage 2 already complete
run_model () {
  local M="$1" L="$2"; shift 2
  echo "=== [$(date +%H:%M)] serving $M ==="
  bash scratch_runs/serve_model.sh "$M" "$@" || { echo "SKIP $L"; return 1; }
  for B in v22 v22b typ; do
    $PY -m dynbelief.reflect.run --endpoint http://127.0.0.1:8400 --model "$M" \
        --label "anon_$L" --bank $B --arms direct --obs-per-day rand3 \
        --distractors 0 --anon || echo "RUNFAIL $B $L"
    echo "=== [$(date +%H:%M)] anon $B $L done ==="
  done
}
run_model "deepseek-ai/DeepSeek-V4-Flash" deepseek --kv-cache-dtype fp8 --moe-backend triton_unfused
run_model "Qwen/Qwen3.6-35B-A3B-FP8"      qwen36   --moe-backend triton --enforce-eager
run_model "zai-org/GLM-4.5-Air"           glm      --moe-backend triton --enforce-eager
echo ANON_PASSIVE_COMPLETE
