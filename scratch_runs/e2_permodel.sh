#!/bin/bash
cd "$(dirname "$0")/.."
PY=/home/oliver/miniconda3/envs/dynamic_eqa/bin/python
$PY -m dynbelief.e2.run --priors-dir results/e2/priors_mini  --out results/e2_mini  > scratch_runs/e2_mini.log  2>&1
$PY -m dynbelief.e2.run --priors-dir results/e2/priors_gpt55 --out results/e2_gpt55 > scratch_runs/e2_gpt55.log 2>&1
touch results/E2_PERMODEL_DONE.marker
