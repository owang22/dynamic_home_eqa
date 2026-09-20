#!/bin/sh
# LLM arms, in order: seeds 0-4 at 4 h (resumes from the cache), seeds 5-9 at 4 h, then the density check.
cd /home/oliver/robot/dynamic_home_eqa/src
R=../results/overnight_2026-09-20
B=$R/banks
python3 -m baselines.patrol.llm --bank $B/hh_s0_p4.jsonl $B/hh_s1_p4.jsonl $B/hh_s2_p4.jsonl $B/hh_s3_p4.jsonl $B/hh_s4_p4.jsonl --out $R/llm --cache $R/llm_cache --workers 8 2>&1 | tee -a $R/llm_s0-4_p4.log
python3 -m baselines.patrol.llm --bank $B/hh_s5_p4.jsonl $B/hh_s6_p4.jsonl $B/hh_s7_p4.jsonl $B/hh_s8_p4.jsonl $B/hh_s9_p4.jsonl --out $R/llm --cache $R/llm_cache --workers 8 2>&1 | tee -a $R/llm_s5-9_p4.log
python3 -m baselines.patrol.llm --bank $B/hh_s0_p1.jsonl $B/hh_s1_p1.jsonl $B/hh_s2_p1.jsonl $B/hh_s3_p1.jsonl $B/hh_s4_p1.jsonl $B/hh_s0_p8.jsonl $B/hh_s1_p8.jsonl $B/hh_s2_p8.jsonl $B/hh_s3_p8.jsonl $B/hh_s4_p8.jsonl --look on --out $R/llm --cache $R/llm_cache --workers 8 2>&1 | tee -a $R/llm_density.log
echo "LLM QUEUE DONE $(date)" | tee -a $R/llm_density.log
