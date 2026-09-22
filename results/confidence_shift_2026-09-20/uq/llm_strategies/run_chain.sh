#!/bin/bash
# Unattended overnight LLM-strategy chain against the shared local vLLM server at :8300 (workshop session
# dynamic-home-eqa-5a shares it). Originally written to sleep until 23:30 before spending worker budget, per the
# pre-23:30 <=20-stream agreement; started at 23:17 instead on Oliver's direct instruction once the server showed
# 15/64 slots running (5a notified it's taking ~40 slots from then on, 14 minutes early).
#
# Structure, per regime (sick10_all then sick10_partial), not-told before told (so told's shared pre-hint days
# replay from cache instead of paying twice): one baselines.patrol.llm invocation covers all 3 households x all
# 3 strategies at once (llm.py's own ThreadPoolExecutor already isolates each (bank,memory,told,look) arm in a
# try/except -- "ARM FAILED ..." printed and the pool continues -- so a single household or strategy blowing up
# cannot stop its regime, let alone the chain). Each invocation's own exit code is ALSO captured and logged, and
# this script is not run with `set -e`, so even a whole invocation dying outright does not stop the next line.
# After every invocation, llm_strategy_check.py appends a numeric verdict to the progress log, to be read against
# uq/llm_strategies/EXPECTATIONS.md (a written bar, not yet an automated pass/fail -- see STATUS.md).
#
# KnowNo/conformal + the 3 confidence channels (verbalized / sample-agreement / token-probability) are a SEPARATE,
# smaller pass: uq_llm.py makes 3 calls/question (vs 1 for the plain arms above), so it is bounded to retrieval
# memory only, not-told only, and a fixed 14-day list spanning all four stages (lead-up, shift entry, mid-sick,
# return) rather than all 32 days, to keep its cost in proportion to how much it actually adds to the paper.

cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
OUT=$R/chain
LOG=$R/chain_progress.log
mkdir -p "$OUT"

BANKS_ALL="../results/regime_search/sick10_all/banks/hh_s0_t03.jsonl ../results/regime_search/sick10_all/banks/hh_s1_t03.jsonl ../results/regime_search/sick10_all/banks/hh_s2_t03.jsonl"
BANKS_PARTIAL="../results/regime_search/sick10_partial/banks/hh_s0_t03.jsonl ../results/regime_search/sick10_partial/banks/hh_s1_t03.jsonl ../results/regime_search/sick10_partial/banks/hh_s2_t03.jsonl"
STRATS="retrieval longcontext reflect"
WORKERS=40
CHANNEL_DAYS="9,10,11,12,13,14,15,16,17,20,24,25,28,31"

echo "$(date +%H:%M) chain script started (pid $$), starting immediately (Oliver: server had 15/64 slots running, no need to wait for 23:30) at workers=$WORKERS" >> "$LOG"

run_regime() {
  name=$1; banks=$2; outdir=$OUT/$name
  mkdir -p "$outdir"
  for told in not_told told; do
    python3 -m baselines.patrol.llm --bank $banks --out "$outdir" --cache "$outdir/cache" \
      --memory $STRATS --told "$told" --look off --workers $WORKERS --format conf \
      > "$outdir/${told}.log" 2>&1
    ec=$?
    echo "$(date +%H:%M) chain $name $told exit=$ec" >> "$LOG"
    python3 -m baselines.patrol.llm_strategy_check --dir "$outdir" --shift-days 14,15 >> "$LOG" 2>&1
  done
  echo "$(date +%H:%M) chain $name done" >> "$LOG"
}

run_regime sick10_all "$BANKS_ALL"
run_regime sick10_partial "$BANKS_PARTIAL"

# --- KnowNo/conformal channels, retrieval-only, not-told-only, bounded day list ---
CHOUT=$R/knowno_channels
mkdir -p "$CHOUT"
for regime_dir in sick10_all:$BANKS_ALL sick10_partial:$BANKS_PARTIAL; do
  regime=${regime_dir%%:*}; banks=${regime_dir#*:}
  for bank in $banks; do
    hh=$(basename "$bank" .jsonl)
    codir=$CHOUT/${regime}_${hh}
    mkdir -p "$codir"
    python3 -m baselines.patrol.uq_llm --bank "$bank" --out "$codir" --memory retrieval \
      --day-list "$CHANNEL_DAYS" --samples 5 \
      > "$codir/channels.log" 2>&1
    ec=$?
    echo "$(date +%H:%M) chain knowno $regime $hh exit=$ec" >> "$LOG"
    logf="$codir/${hh}.jsonl"
    if [ -f "$logf" ]; then
      python3 -m baselines.patrol.uq_llm_conformal --log "$logf" >> "$LOG" 2>&1
    else
      echo "$(date +%H:%M) chain knowno $regime $hh: no log written, skipping conformal" >> "$LOG"
    fi
  done
done

echo "$(date +%H:%M) CHAIN FINISHED" >> "$LOG"
