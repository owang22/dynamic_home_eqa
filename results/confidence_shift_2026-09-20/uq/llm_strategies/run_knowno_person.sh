#!/bin/bash
# Bounded MCQ token-probability channel + KnowNo conformal sets, buffer(naive) and retrieval, 3 households
# (hh_s0-2), day-list 13/14/15/20/24/25/30 (spans lead-end, shift entry, mid-sick, both return days). The only
# new-LLM-call item in this round (3 calls/question vs 1 for the plain arms) -- run sequentially, not fanned out
# across households, to keep it a modest addition on top of the main person-regime chain's 40 workers.
cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
OUT=$R/knowno_person
LOG=$R/chain_progress.log
FM=/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory
DAYS="13,14,15,20,24,25,30"
mkdir -p "$OUT"

echo "$(date +%H:%M) knowno_person started (pid $$)" >> "$LOG"
for mem in naive retrieval; do
  for s in 0 1 2; do
    hh=hh_s${s}
    codir=$OUT/${mem}_${hh}
    mkdir -p "$codir"
    python3 -m baselines.patrol.uq_llm --bank "$FM/banks_f1/${hh}_t03.jsonl" --out "$codir" --memory $mem \
      --day-list "$DAYS" --samples 5 \
      > "$codir/channels.log" 2>&1
    ec=$?
    echo "$(date +%H:%M) knowno_person $mem $hh exit=$ec" >> "$LOG"
    logf="$codir/${hh}.jsonl"
    if [ -f "$logf" ]; then
      python3 -m baselines.patrol.uq_llm_conformal --log "$logf" >> "$LOG" 2>&1
    else
      echo "$(date +%H:%M) knowno_person $mem $hh: no log written, skipping conformal" >> "$LOG"
    fi
  done
done
echo "$(date +%H:%M) KNOWNO_PERSON FINISHED" >> "$LOG"
