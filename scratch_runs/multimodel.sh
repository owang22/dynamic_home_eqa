#!/bin/bash
# Multi-model replication of the two BEST arms (never the raw-log baseline):
#   llm_scaffold    — persona memory rebuilt nightly from self-gathered observations
#   scaffold_fusion — that belief + Tier-3 precision fusion with classical C3g
# tau is frozen from the DeepSeek dev sweep and applied unchanged to every model.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
TAU="$1"     # frozen scaffold_fusion tau

run_model () {   # run_model <hf_id> <tag> [extra serve args]
  local MODEL="$1"; local TAG="$2"; shift 2
  echo "=== [$(date +%H:%M)] serving $MODEL ==="
  bash scratch_runs/serve_model.sh "$MODEL" "$@" || { echo "SKIP $TAG (serve failed)"; return 1; }
  echo "=== [$(date +%H:%M)] $TAG : llm_scaffold ==="
  $PY -m dynbelief.two_capacities.run2 --bank conf --arm llm_scaffold \
      --model "$MODEL" --tag "frozen_$TAG" || echo "FAIL $TAG llm_scaffold"
  echo "=== [$(date +%H:%M)] $TAG : scaffold_fusion ==="
  $PY -m dynbelief.two_capacities.run2 --bank conf --arm scaffold_fusion --tau "$TAU" \
      --model "$MODEL" --tag "frozen_$TAG" || echo "FAIL $TAG scaffold_fusion"
  echo "=== [$(date +%H:%M)] $TAG DONE ==="
}

run_model "Qwen/Qwen3.6-35B-A3B-FP8" qwen36 --moe-backend triton --enforce-eager
run_model "zai-org/GLM-4.5-Air"      glm    --moe-backend triton --enforce-eager
echo MULTIMODEL_COMPLETE
