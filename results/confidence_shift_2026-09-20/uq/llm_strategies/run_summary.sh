#!/bin/bash
cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
FM=/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory
B10=""; for s in 0 1 2; do B10="$B10 $FM/banks_f1/hh_s${s}_t03.jsonl"; done
python3 -m baselines.patrol.llm --bank $B10 --out $R/chain_person/nottold --cache $R/chain_person/cache \
  --memory summary --told not_told --look off --workers 3 --format conf \
 > $R/chain_person/summary10.log 2>&1
echo "$(date +%H:%M) summary 10hh no-message exit=$?" >> $R/chain_progress.log
