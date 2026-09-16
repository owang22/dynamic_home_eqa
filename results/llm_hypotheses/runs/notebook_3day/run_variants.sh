#!/bin/bash
# notebook_voi then notebook_llmDecide, 3 days each, hh_001 cold-start bank.
cd /home/oliver/robot/dynamic_home_eqa/src
OUT=../results/llm_hypotheses/runs/notebook_3day
for KIND in notebook_voi notebook_llmDecide; do
  echo "=== $KIND start $(date)" >> $OUT/run_variants.log
  PYTHONPATH=. python -m baselines.llm_hypotheses.run_tour_start \
      --household hh_001 --arm active:$KIND:named:f0 \
      --bank-dir ../banks/baselines/cold_start --out-dir $OUT --days 3 \
      >> $OUT/run_variants.log 2>&1
  echo "=== $KIND exit $? $(date)" >> $OUT/run_variants.log
done
echo ALL_DONE >> $OUT/run_variants.log
