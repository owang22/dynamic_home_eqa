#!/bin/bash
# Per-model tau sweep for scaffold_fusion on the DEV bank, on the CORRECTED query
# design (kinds interleaved). Grid is shifted upward because Qwen/GLM fused
# confidence sits at p10~0.50 — tau=0.45 fired on only ~3% of queries.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
GRID="0.45 0.60 0.70 0.80"

sweep () {  # sweep <hf_id> <tag>
  local MODEL="$1"; local TAG="$2"
  for T in $GRID; do
    echo "=== [$(date +%H:%M)] $TAG tau=$T ==="
    $PY -m dynbelief.two_capacities.run2 --bank dev --arm scaffold_fusion --tau $T \
        --model "$MODEL" --tag "tausweep_${TAG}_$T" || echo "FAIL $TAG $T"
  done
}

# GLM server is already up
sweep "zai-org/GLM-4.5-Air" glm
# swap to Qwen
if bash scratch_runs/serve_model.sh "Qwen/Qwen3.6-35B-A3B-FP8" --moe-backend triton --enforce-eager; then
  sweep "Qwen/Qwen3.6-35B-A3B-FP8" qwen36
else
  echo "SKIP qwen (serve failed)"
fi
echo TAU_SWEEP_COMPLETE
