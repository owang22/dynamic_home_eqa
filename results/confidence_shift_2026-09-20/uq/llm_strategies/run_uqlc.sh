#!/bin/bash
cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
FM=/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory
for s in 0 1 2; do
  python3 -m baselines.patrol.uq_llm --bank $FM/banks_f1/hh_s${s}_t03.jsonl \
    --out $R/uqlc/longcontext_hh_s${s} --days 31 --samples 5 --memory longcontext \
    --endpoint http://127.0.0.1:8300/v1 > $R/uqlc/hh_s${s}.log 2>&1 &
done
wait
echo "$(date +%H:%M) uq_llm longcontext 3hh DONE" >> $R/chain_progress.log
