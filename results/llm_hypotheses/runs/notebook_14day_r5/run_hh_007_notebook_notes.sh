#!/bin/bash
cd /home/oliver/robot/dynamic_home_eqa/src
LOG=../results/llm_hypotheses/runs/notebook_14day_r5/run_hh_007_notebook_notes.log
echo "=== hh_007 notebook_notes start $(date)" >> $LOG
PYTHONPATH=. python -m baselines.llm_hypotheses.run_tour_start --household hh_007 --arm active:notebook_notes:named:f0 --bank-dir ../banks/baselines/cold_start --out-dir ../results/llm_hypotheses/runs/notebook_14day_r5 --days 14 >> $LOG 2>&1
echo "=== hh_007 notebook_notes exit $? $(date)" >> $LOG
