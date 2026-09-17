#!/bin/bash
cd /home/oliver/robot/dynamic_home_eqa/src
LOG=../results/llm_hypotheses/runs/notebook_14day/run_hh_009_notebook_fixed.log
echo "=== hh_009 notebook_fixed start $(date)" >> $LOG
PYTHONPATH=. python -m baselines.llm_hypotheses.run_tour_start --household hh_009 --arm active:notebook_fixed:named:f0 --bank-dir ../banks/baselines/cold_start --out-dir ../results/llm_hypotheses/runs/notebook_14day --days 14 >> $LOG 2>&1
echo "=== hh_009 notebook_fixed exit $? $(date)" >> $LOG
