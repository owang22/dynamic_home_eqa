#!/bin/bash
# 24-household atypical passive pool (v22 + v22b, d0/rand3) for Qwen + GLM,
# matching the deepseek all_rows_{v22,v22b}_distractor_d0 protocol.
# WAITS for the typ multimodel script to finish before touching the GPUs.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
while ! grep -qE "TYP_MULTIMODEL_COMPLETE" scratch_runs/typ_passive_multimodel.log 2>/dev/null; do
  sleep 120
done
run_model () {
  local M="$1" L="$2"; shift 2
  echo "=== [$(date +%H:%M)] serving $M ==="
  bash scratch_runs/serve_model.sh "$M" "$@" || { echo "SKIP $L"; return 1; }
  for B in v22 v22b; do
    $PY -m dynbelief.reflect.run --endpoint http://127.0.0.1:8400 --model "$M" \
        --label "d0_$L" --bank $B --arms direct,nomem --obs-per-day rand3 \
        --distractors 0 || { echo "RUNFAIL $B $L"; return 1; }
    $PY -m dynbelief.reflect.report --bank $B --label "d0_$L" --alpha-max 8 \
        --obs-per-day rand3 > "reports/reflect/report_${B}_d0_${L}.txt" 2>&1 \
        || echo "REPORTFAIL $B $L"
    echo "=== [$(date +%H:%M)] $B $L done ==="
  done
}
run_model "Qwen/Qwen3.6-35B-A3B-FP8" qwen36 --moe-backend triton --enforce-eager
run_model "zai-org/GLM-4.5-Air"      glm    --moe-backend triton --enforce-eager
echo V22_MULTIMODEL_COMPLETE
