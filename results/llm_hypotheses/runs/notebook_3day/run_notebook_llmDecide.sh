#!/bin/bash
cd /home/oliver/robot/dynamic_home_eqa/src
echo "=== notebook_llmDecide start $(date)" >> ../results/llm_hypotheses/runs/notebook_3day/run_notebook_llmDecide.log
PYTHONPATH=. python -m baselines.llm_hypotheses.run_tour_start --household hh_001 --arm active:notebook_llmDecide:named:f0 --bank-dir ../banks/baselines/cold_start --out-dir ../results/llm_hypotheses/runs/notebook_3day --days 3 >> ../results/llm_hypotheses/runs/notebook_3day/run_notebook_llmDecide.log 2>&1
echo "=== notebook_llmDecide exit $? $(date)" >> ../results/llm_hypotheses/runs/notebook_3day/run_notebook_llmDecide.log
