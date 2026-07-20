#!/bin/bash
source "$(dirname "$0")/../env.sh" 2>/dev/null || true
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python -m dynbelief.experiments.e1 \
  --client openai --model gpt-5.4-mini
rc=$?
touch scratch_runs/E1_MINI_DONE.marker
exit $rc
