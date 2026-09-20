#!/bin/sh
# Rerun the p4 arms that died on the cache-write race (replays from the cache where possible).
cd /home/oliver/robot/dynamic_home_eqa/src
R=../results/overnight_2026-09-20
B=$R/banks
python3 -m baselines.patrol.llm --bank $B/hh_s3_p4.jsonl --memory naive --told not_told --look on --out $R/llm --cache $R/llm_cache --workers 2 2>&1 | tee -a $R/llm_missing.log
python3 -m baselines.patrol.llm --bank $B/hh_s3_p4.jsonl --memory recent --told not_told --look off --out $R/llm --cache $R/llm_cache --workers 2 2>&1 | tee -a $R/llm_missing.log
python3 -m baselines.patrol.llm --bank $B/hh_s5_p4.jsonl --memory naive --told not_told --look on off --out $R/llm --cache $R/llm_cache --workers 2 2>&1 | tee -a $R/llm_missing.log
python3 -m baselines.patrol.llm --bank $B/hh_s5_p4.jsonl --memory recent summary --told told --look on off --out $R/llm --cache $R/llm_cache --workers 4 2>&1 | tee -a $R/llm_missing.log
python3 -m baselines.patrol.llm --bank $B/hh_s6_p4.jsonl --memory recent --told not_told --look on --out $R/llm --cache $R/llm_cache --workers 1 2>&1 | tee -a $R/llm_missing.log
python3 -m baselines.patrol.llm --bank $B/hh_s7_p4.jsonl $B/hh_s9_p4.jsonl --memory naive --told not_told --look off --out $R/llm --cache $R/llm_cache --workers 2 2>&1 | tee -a $R/llm_missing.log
echo "MISSING ARMS DONE $(date)" | tee -a $R/llm_missing.log
