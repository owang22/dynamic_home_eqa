#!/bin/bash
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python -m dynbelief.experiments.e1 \
  --client openai --model gpt-5.4-mini > scratch_runs/e1v2b_summary.txt 2>&1
touch scratch_runs/E1V2B_DONE.marker
