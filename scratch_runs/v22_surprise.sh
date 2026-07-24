#!/bin/bash
# VERSION22 surprise experiment ("surprise"): classical-engine-gated reflection
# (LLM woken only when the day's observations significantly contradict the C3g
# belief model) on the version22 conf bank, same obs (rand3) + distractor
# levels as the "distractor" nightly runs, so rows merge into those tables.
set -e
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
EP=http://127.0.0.1:8400
MODEL=deepseek-ai/DeepSeek-V4-Flash

for D in 0 3 6 12; do
  L="surprise_d${D}"
  echo "=== [$(date +%H:%M:%S)] surprise level $D (label $L) ==="
  $PY -m dynbelief.reflect.surprise --endpoint $EP --model $MODEL --label $L \
      --bank v22 --obs-per-day rand3 --distractors $D
  echo "=== [$(date +%H:%M:%S)] $L done ==="
done
echo "SURPRISE SWEEP COMPLETE"
