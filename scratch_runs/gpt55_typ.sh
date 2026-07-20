#!/bin/bash
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python -m dynbelief.experiments.e1 \
  --client openai --model gpt-5.5 --streams-rerun \
  --banks typ_v1 --n-per-cell 8 --max-tokens 1200 --reasoning low \
  > scratch_runs/gpt55_typ.log 2>&1
touch results/e1/GPT55_TYP_DONE.marker
