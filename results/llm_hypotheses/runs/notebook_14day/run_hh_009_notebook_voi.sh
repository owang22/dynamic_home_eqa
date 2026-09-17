#!/bin/bash
cd /home/oliver/robot/dynamic_home_eqa/src
LOG=../results/llm_hypotheses/runs/notebook_14day/run_hh_009_notebook_voi.log
echo "=== hh_009 notebook_voi start $(date)" >> $LOG
PYTHONPATH=. python -m baselines.llm_hypotheses.run_tour_start --household hh_009 --arm active:notebook_voi:named:f0 --bank-dir ../banks/baselines/cold_start --out-dir ../results/llm_hypotheses/runs/notebook_14day --days 14 >> $LOG 2>&1
echo "=== hh_009 notebook_voi exit $? $(date)" >> $LOG
for ARM in active:mostfreq72:search:f0 active:lastobs:search:f0 active:perpetua:search:f0; do
  PYTHONPATH=. python -m baselines.llm_hypotheses.run_tour_start --household hh_009 --arm $ARM --bank-dir ../banks/baselines/cold_start --out-dir ../results/llm_hypotheses/runs/notebook_14day --days 14 >> $LOG 2>&1
done
echo "=== hh_009 references done $(date)" >> $LOG
