#!/bin/bash
# Emit one line whenever something changes: an arm crosses a day boundary (64 answers), naive crosses a day,
# an arm process disappears, arms_fb.log grows, or a Traceback appears. Poll every 60 s.
R=/home/oliver/robot/dynamic_home_eqa/results/confidence_shift_2026-09-20
D=${1:-heldout_fb}; LABEL=${2:-t03}
prev=""
while true; do
  sig=""
  for d in $R/$D/hyp/study/*/arms/passive/*/; do
    [ -f "$d/live.jsonl" ] || continue
    hh=$(basename "$(echo $d | sed 's|/arms/.*||')" | sed "s/_${LABEL}__bank0//"); arm=$(basename "$d" | sed 's/.*__//')
    n=$(wc -l < "$d/live.jsonl"); rev=$(ls "$d/revisions" 2>/dev/null | wc -l)
    sig+="$hh/$arm:day$((n/64)):rev$rev "
  done
  for d in $R/$D/llm/*_naive_*/; do
    [ -f "$d/calls.jsonl" ] || continue
    sig+="$(basename $d | sed 's/_naive_/:/; s/_lookoff//'):d$(( $(wc -l < "$d/calls.jsonl") / 64 )) "
  done
  procs=$(pgrep -fc "run_tour_start --household hh_s[0-9]*_${LABEL}"); naive=$(pgrep -fc "patrol.llm --bank .*${D}")
  sig+="| arms=$procs naive=$naive"
  logn=$(wc -l < $R/$D/arms_fb.log 2>/dev/null); tb=$(grep -l Traceback $R/$D/arm_s*_*.log 2>/dev/null | wc -l)
  sig+=" exitlines=$logn tracebacks=$tb"
  if [ "$sig" != "$prev" ]; then echo "$(date +%H:%M) $sig"; prev="$sig"; fi
  sleep 60
done
