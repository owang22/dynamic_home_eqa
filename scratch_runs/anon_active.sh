#!/bin/bash
# ANONYMIZED ACTIVE-SENSING runs (answer-or-resense scarce loop).
# Arm: llm_scaffold ONLY -- the LLM alone receives "object_1"/"receptacle_3"
# instead of "mug"/"craft_desk" and makes its own answer-or-resense choices.
# The comparison is named-LLM vs anonymized-LLM (vs the classical reference):
# how much of the active-sensing benefit is WORLD KNOWLEDGE rather than
# evidence integration. NO fusion -- it would reintroduce the classical channel,
# which is name-invariant, and dilute exactly the contrast being measured.
# classical/oracle need no anon run (name-invariant by construction).
# Per-model tau/alpha from reports/answer_or_resense/frozen_dev_params.json.
# WAITS for the passive anon stage to finish.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
while ! grep -qE "ANON_PASSIVE_COMPLETE" scratch_runs/anon_passive.log 2>/dev/null; do
  sleep 120
done
run_model () {
  local M="$1" L="$2" TAU="$3" ALPHA="$4"; shift 4
  echo "=== [$(date +%H:%M)] serving $M ==="
  bash scratch_runs/serve_model.sh "$M" "$@" || { echo "SKIP $L"; return 1; }
  for BANK in conf typ; do
    $PY -m dynbelief.two_capacities.run2 --bank $BANK --arm llm_scaffold \
        --tau "$TAU" --alpha "$ALPHA" --endpoint http://127.0.0.1:8400 \
        --model "$M" --anon --tag "anon_${L}" \
        || echo "RUNFAIL $BANK llm_scaffold $L"
    echo "=== [$(date +%H:%M)] anon-active $BANK llm_scaffold $L done ==="
  done
}
run_model "deepseek-ai/DeepSeek-V4-Flash" deepseek 0.45 2.72 --kv-cache-dtype fp8 --moe-backend triton_unfused
run_model "Qwen/Qwen3.6-35B-A3B-FP8"      qwen36   0.70 2.75 --moe-backend triton --enforce-eager
run_model "zai-org/GLM-4.5-Air"           glm      0.70 0.65 --moe-backend triton --enforce-eager
echo ANON_ACTIVE_COMPLETE
