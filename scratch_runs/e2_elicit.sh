#!/bin/bash
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python -m dynbelief.e2.run --elicit \
  --models gpt-5.4-mini,gpt-5.5 > scratch_runs/e2_elicit.log 2>&1
touch results/e2/E2_ELICIT_DONE.marker
