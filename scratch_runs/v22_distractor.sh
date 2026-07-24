#!/bin/bash
# VERSION22 distractor experiment ("distractor"): reflective-memory arms on the
# version22 banks (12 households) at obs/day ~3 (rand3), sweeping the number of
# static-distractor sightings/day in {0, 3, 6, 12}. Per level:
#   1. v22dev bank, direct arm only  -> alpha sweep rows (dev/test wall)
#   2. v22 bank, direct + nomem arms -> confirmatory rows
#   3. offline report (classical + fusion + tables + figures)
set -e
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
EP=http://127.0.0.1:8400
MODEL=deepseek-ai/DeepSeek-V4-Flash

for D in 0 3 6 12; do
  L="distractor_d${D}"
  echo "=== [$(date +%H:%M:%S)] distractor level $D (label $L) ==="
  $PY -m dynbelief.reflect.run --endpoint $EP --model $MODEL --label $L \
      --bank v22dev --arms direct --obs-per-day rand3 --distractors $D
  $PY -m dynbelief.reflect.run --endpoint $EP --model $MODEL --label $L \
      --bank v22 --arms direct,nomem --obs-per-day rand3 --distractors $D
  $PY -m dynbelief.reflect.report --bank v22 --label $L --obs-per-day rand3 \
      > reports/reflect/report_v22_${L}.txt 2>&1 || echo "report $L failed"
  echo "=== [$(date +%H:%M:%S)] $L done ==="
done
echo "DISTRACTOR SWEEP COMPLETE"
