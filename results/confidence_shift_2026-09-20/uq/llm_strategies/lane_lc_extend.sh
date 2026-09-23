#!/bin/bash
# Extend long-context on the one-person regime to more households, for the paper's section-3 figure.
#
# Household by household, each household's FULL TRIPLE finished before the next one starts, so whatever the
# clock allows, every household we have is usable and the told/untold comparison is always matched. Running
# seven no-message arms first and then discovering there is no time for their told arms would leave nothing
# comparable.
#
# Within a household the order is no-message, then start-message, then start+end, against a warm cache: the
# told arms are identical to the untold run until the day they are told, so they only pay for day 14 onward and
# day 24 onward. The three arms of one household are therefore NEVER run in parallel -- that throws the cache
# benefit away. Parallelism goes across households instead, STREAMS at a time.
cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
OUT=$R/chain_person; CACHE=$OUT/cache; LOG=$R/lc_extend.log
FM=/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory
STREAMS=${STREAMS:-3}
# hh_s5 first: its no-message arm already exists, so its triple is two arms rather than three and it is the
# cheapest household to make usable.
QUEUE=${QUEUE:-"5 3 4 6 7 8 9"}

arm(){ # sub bankdir told hh
  local sub=$1 bankdir=$2 told=$3 hh=$4
  local d="$OUT/$sub/hh_s${hh}_t03_longcontext_$([ "$told" = told ] && echo told || echo nottold)_lookoff"
  if [ -s "$d/run_log.jsonl" ] && [ "$(wc -l < "$d/run_log.jsonl")" -gt 100 ]; then
    echo "$(date +%H:%M) hh_s$hh $sub already present, skipping" >> "$LOG"; return 0; fi
  mkdir -p "$OUT/$sub"
  local t0=$(date +%s)
  python3 -m baselines.patrol.llm --bank "$FM/$bankdir/hh_s${hh}_t03.jsonl" --out "$OUT/$sub" \
    --cache "$CACHE" --memory longcontext --told "$told" --look off --workers 1 --format conf \
    > "$OUT/${sub}_lcx_hh${hh}.log" 2>&1
  echo "$(date +%H:%M) hh_s$hh $sub exit=$? in $(( ($(date +%s)-t0)/60 ))m" >> "$LOG"
}

triple(){ local hh=$1
  echo "$(date +%H:%M) hh_s$hh triple START" >> "$LOG"
  arm nottold          banks_f1        not_told "$hh"
  arm told_entry       banks_f1        told     "$hh"
  arm told_entryreturn banks_f1_return told     "$hh"
  echo "$(date +%H:%M) hh_s$hh triple DONE" >> "$LOG"
}

echo "$(date +%H:%M) lc extend START, $STREAMS streams, queue: $QUEUE" >> "$LOG"
for hh in $QUEUE; do
  while [ "$(jobs -rp | wc -l)" -ge "$STREAMS" ]; do sleep 20; done
  triple "$hh" &
done
wait
echo "$(date +%H:%M) lc extend ALL DONE" >> "$LOG"
