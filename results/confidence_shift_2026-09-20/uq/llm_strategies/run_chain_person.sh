#!/bin/bash
# Person-regime LLM-strategy chain (Oliver's decision: get ONE suite clean before spreading further). Replaces
# run_chain.sh's sick10_all/sick10_partial passes, which were stopped at 23:34 (whatever they finished stays on
# disk, untouched, naturally marked incomplete by llm_live_extra.py's own progress accounting).
#
# retrieval/longcontext/reflect x {not-told, told-on-entry, told-on-entry+return}, hh_s0-s9, on the SAME bank
# files the workshop session's own F1 runs used (dynamic_home_eqa_fm/results/fm_memory/banks_f1 and
# banks_f1_return -- confirmed byte-identical to this study's sick10_owner banks except banks_f1_return's header
# adds a day-24 return hint_message; llm.py filters hint_rows by day_index <= current day before injecting them
# into any prompt, so days 1-23 are byte-identical across all three passes and the shared --cache dir replays them
# instead of paying twice: not-told populates days 1-13, told-entry reuses that then adds days 14-23 and its own
# day>=14 prompts, told-entry+return reuses ALL of that through day 23 and only pays for day 24 onward).
# told-entry and told-entry+return get SEPARATE --out dirs (same household_id + told=true would otherwise collide
# and the second pass would silently overwrite the first's run_log.jsonl).
#
# Crash-resilience: same as run_chain.sh -- llm.py's own ThreadPoolExecutor isolates each (bank,memory) arm in a
# try/except, and this script does not use `set -e`, so one failure does not stop the rest.

cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
OUT=$R/chain_person
LOG=$R/chain_progress.log
CACHE=$OUT/cache
mkdir -p "$OUT/nottold" "$OUT/told_entry" "$OUT/told_entryreturn"

FM=/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory
BANKS_F1=""; BANKS_F1_RET=""
for s in 0 1 2 3 4 5 6 7 8 9; do
  BANKS_F1="$BANKS_F1 $FM/banks_f1/hh_s${s}_t03.jsonl"
  BANKS_F1_RET="$BANKS_F1_RET $FM/banks_f1_return/hh_s${s}_t03.jsonl"
done
STRATS="retrieval longcontext reflect"
WORKERS=40

echo "$(date +%H:%M) person chain started (pid $$), workers=$WORKERS, households 0-9" >> "$LOG"

python3 -m baselines.patrol.llm --bank $BANKS_F1 --out "$OUT/nottold" --cache "$CACHE" \
  --memory $STRATS --told not_told --look off --workers $WORKERS --format conf \
  > "$OUT/nottold.log" 2>&1
ec=$?
echo "$(date +%H:%M) person chain no-message exit=$ec" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/nottold" --shift-days 14,15 >> "$LOG" 2>&1

python3 -m baselines.patrol.llm --bank $BANKS_F1 --out "$OUT/told_entry" --cache "$CACHE" \
  --memory $STRATS --told told --look off --workers $WORKERS --format conf \
  > "$OUT/told_entry.log" 2>&1
ec=$?
echo "$(date +%H:%M) person chain start-message exit=$ec" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/told_entry" --shift-days 14,15 >> "$LOG" 2>&1

python3 -m baselines.patrol.llm --bank $BANKS_F1_RET --out "$OUT/told_entryreturn" --cache "$CACHE" \
  --memory $STRATS --told told --look off --workers $WORKERS --format conf \
  > "$OUT/told_entryreturn.log" 2>&1
ec=$?
echo "$(date +%H:%M) person chain start-and-end-messages exit=$ec" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/told_entryreturn" --shift-days 14,15,24 >> "$LOG" 2>&1

echo "$(date +%H:%M) PERSON CHAIN FINISHED" >> "$LOG"
