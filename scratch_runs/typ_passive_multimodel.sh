#!/bin/bash
# TYPICAL-bank passive runs for Qwen + GLM (matched to deepseek typd0: rand3,
# distractors 0). alpha only affects the fusion arm; frozen 8 as elsewhere.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
run_one () {
  local M="$1" L="$2"; shift 2
  echo "=== [$(date +%H:%M)] serving $M ==="
  bash scratch_runs/serve_model.sh "$M" "$@" || { echo "SKIP $L"; return 1; }
  $PY -m dynbelief.reflect.run --endpoint http://127.0.0.1:8400 --model "$M" \
      --label "$L" --bank typ --arms direct,nomem --obs-per-day rand3 \
      --distractors 0 || { echo "RUNFAIL $L"; return 1; }
  $PY -m dynbelief.reflect.report --bank typ --label "$L" --alpha-max 8 \
      --obs-per-day rand3 > "reports/reflect/report_typ_${L}.txt" 2>&1 \
      || echo "REPORTFAIL $L"
  echo "=== [$(date +%H:%M)] $L DONE ==="
}
run_one "Qwen/Qwen3.6-35B-A3B-FP8" typd0_qwen36 --moe-backend triton --enforce-eager
run_one "zai-org/GLM-4.5-Air"      typd0_glm    --moe-backend triton --enforce-eager
echo TYP_MULTIMODEL_COMPLETE
