#!/bin/sh
cd /home/oliver/robot/dynamic_home_eqa/src
R=../results/overnight_2026-09-20; B=$R/banks
python3 -m baselines.patrol.llm --bank $B/hh_s1_p1.jsonl $B/hh_s1_p8.jsonl --memory naive --told told --look on --out $R/llm --cache $R/llm_cache --workers 2 2>&1 | tee -a $R/llm_missing.log
python3 -m baselines.patrol.llm --bank $B/hh_s2_p8.jsonl --memory naive recent --told not_told --look on --out $R/llm --cache $R/llm_cache --workers 2 2>&1 | tee -a $R/llm_missing.log
python3 -m baselines.patrol.llm --bank $B/hh_s3_p8.jsonl --memory recent --told told --look on --out $R/llm --cache $R/llm_cache --workers 1 2>&1 | tee -a $R/llm_missing.log
python3 -m baselines.patrol.llm --bank $B/hh_s4_p8.jsonl --memory recent --told not_told --look on --out $R/llm --cache $R/llm_cache --workers 1 2>&1 | tee -a $R/llm_missing.log
echo "MISSING DENSITY DONE $(date)" | tee -a $R/llm_missing.log
