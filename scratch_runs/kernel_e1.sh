#!/bin/bash
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python -m dynbelief.classical.kernel_run > scratch_runs/kernel_e1.log 2>&1
touch results/kernel/KERNEL_E1_DONE.marker
