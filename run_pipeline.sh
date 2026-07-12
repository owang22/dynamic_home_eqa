#!/usr/bin/env bash
# run_pipeline.sh — end-to-end smoke test of the dynamic_home_eqa pipeline.
#
# Runs the four stages in order, all from one conda env (default: dynamic_eqa,
# which has habitat_sim/habitat-lab, vllm, and the analysis stack — see the
# README's "Environment" section):
#   1. compute_anchor_admission_map.py  (receptacle geometry cache)
#   2. gen_dataset.py                   (vLLM day-trace generation)
#   3. build_realized_day.py            (realized-world artifact)
#   4. realism_render_job.py            (render eval media)
#
# No-arg default is a single-scene, single-folder smoke test; every stage's
# own no-arg default resolves to the same scene/folder. Real batch runs
# should invoke the stage scripts directly with --scenes/--n/--folders.
#
# Usage:
#   ./run_pipeline.sh                        # smoke test (default scene/profile)
#   ./run_pipeline.sh 102344022 single_retiree
#
# Env var override (conda env NAME, must already exist):
#   DYNAMIC_EQA_ENV   (default: dynamic_eqa)
set -euo pipefail

SCENE="${1:-102343992}"
PROFILE="${2:-family_with_kids_qwen32b_demo}"
FOLDER="${SCENE}_${PROFILE}"

DYNAMIC_EQA_ENV="${DYNAMIC_EQA_ENV:-dynamic_eqa}"

CONDA_BASE="$(conda info --base 2>/dev/null || echo "$HOME/miniconda3")"
PY="$CONDA_BASE/envs/$DYNAMIC_EQA_ENV/bin/python"

echo "=== dynamic_home_eqa pipeline: scene=$SCENE profile=$PROFILE folder=$FOLDER (env: $DYNAMIC_EQA_ENV) ==="
echo

echo "--- [1/4] anchor admission map ---"
"$PY" -m dynamic_home_eqa.scripts.compute_anchor_admission_map --scenes "$SCENE"
echo

echo "--- [2/4] generate day trace ---"
"$PY" -m dynamic_home_eqa.scripts.gen_dataset --scenes "$SCENE" --profile "$PROFILE"
echo

echo "--- [3/4] build realized-world artifact ---"
"$PY" -m dynamic_home_eqa.scripts.build_realized_day --folders "$FOLDER"
echo

echo "--- [4/4] render eval media ---"
"$PY" -m dynamic_home_eqa.scripts.realism_render_job --folders "$FOLDER"
echo

echo "=== done — serve the rating webapp with:"
echo "    $PY -m uvicorn dynamic_home_eqa.webapp.realism_eval.app:app --host 127.0.0.1 --port 8000"
echo "    (loopback only by design; from another machine use ssh -L 8000:localhost:8000)"
