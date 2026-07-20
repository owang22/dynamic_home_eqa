#!/bin/bash
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python -m dynbelief.experiments.e1 \
  --client openai --model gpt-5.4-mini --streams-rerun > scratch_runs/e1_streams.log 2>&1
touch results/e1/E1_STREAMS_DONE.marker
