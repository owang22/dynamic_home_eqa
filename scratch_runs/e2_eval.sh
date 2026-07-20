#!/bin/bash
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python -m dynbelief.e2.run > scratch_runs/e2_eval.log 2>&1
touch results/e2/E2_EVAL_DONE.marker
