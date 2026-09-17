#!/bin/bash
cd /home/oliver/robot/dynamic_home_eqa/src
echo "=== notebook_voi start $(date)" >> ../results/llm_hypotheses/runs/notebook_3day/run_notebook_voi.log
PYTHONPATH=. python -m baselines.llm_hypotheses.run_tour_start --household hh_001 --arm active:notebook_voi:named:f0 --bank-dir ../banks/baselines/cold_start --out-dir ../results/llm_hypotheses/runs/notebook_3day --days 3 >> ../results/llm_hypotheses/runs/notebook_3day/run_notebook_voi.log 2>&1
echo "=== notebook_voi exit $? $(date)" >> ../results/llm_hypotheses/runs/notebook_3day/run_notebook_voi.log
