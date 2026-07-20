#!/bin/bash
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python -m dynbelief.classical.run > scratch_runs/classical.log 2>&1
touch results/classical/CLASSICAL_DONE.marker
