#!/bin/bash
# VERSION22b expansion sweeps (Change 0): 3 new confusable pairs x 2 seed
# instances = 12 households. Runs the SAME protocol/settings as the frozen
# version22 run (rand3 obs, distractors 0/3/6/12) so the rows POOL with
# version22 into the "expanded" (24-household) numbers. Reuses the existing
# version22_dev alpha wall (rows_v22dev_distractor_d*), so no dev run here.
set -e
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
EP=http://127.0.0.1:8400
MODEL=deepseek-ai/DeepSeek-V4-Flash

for D in 0 3 6 12; do
  L="distractor_d${D}"
  echo "=== [$(date +%H:%M:%S)] v22b nightly+classical level $D ==="
  $PY -m dynbelief.reflect.run --endpoint $EP --model $MODEL --label $L \
      --bank v22b --arms direct,nomem --obs-per-day rand3 --distractors $D
  $PY -m dynbelief.reflect.report --bank v22b --label $L --obs-per-day rand3 \
      > reports/reflect/report_v22b_${L}.txt 2>&1 || echo "report $L failed"
  echo "=== [$(date +%H:%M:%S)] v22b surprise level $D ==="
  $PY -m dynbelief.reflect.surprise --endpoint $EP --model $MODEL --label "surprise_d${D}" \
      --bank v22b --obs-per-day rand3 --distractors $D
  echo "=== [$(date +%H:%M:%S)] v22b level $D done ==="
done
echo "V22B SWEEPS COMPLETE"
