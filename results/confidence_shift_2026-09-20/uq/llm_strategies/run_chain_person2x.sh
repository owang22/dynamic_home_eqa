#!/bin/bash
# Two-spells regime (sick2x_owner, 42 days: lead 0-13, sick 14-20, back 21-27, sick 28-34, back 35-41): does a memory
# REUSE what it learned in the first spell? buffer(naive) / retrieval / routine table (routine7) x {no message, start
# message} on hh_s0-s2. The bank writes a "home sick today" hint on every sick day of both spells, so the start-message
# arm is told at both breaks. no-message first (populates the shared cache for days 1-13), then start message.
cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
OUT=$R/chain_person2x
LOG=$R/chain_progress.log
CACHE=$OUT/cache
mkdir -p "$OUT/nottold" "$OUT/told_entry"
BANKS=""; for s in 0 1 2; do BANKS="$BANKS ../results/regime_search/sick2x_owner/banks/hh_s${s}_t03.jsonl"; done
STRATS="${STRATS:-naive retrieval routine7}"
WORKERS=40
echo "$(date +%H:%M) person2x chain started (pid $$), workers=$WORKERS, households 0-2, $STRATS" >> "$LOG"
python3 -m baselines.patrol.llm --bank $BANKS --out "$OUT/nottold" --cache "$CACHE" --memory $STRATS --told not_told --look off --workers $WORKERS --format conf > "$OUT/nottold.log" 2>&1
ec=$?; echo "$(date +%H:%M) person2x chain no-message exit=$ec" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/nottold" --shift-days 14,15,28,29 >> "$LOG" 2>&1
python3 -m baselines.patrol.llm --bank $BANKS --out "$OUT/told_entry" --cache "$CACHE" --memory $STRATS --told told --look off --workers $WORKERS --format conf > "$OUT/told_entry.log" 2>&1
ec=$?; echo "$(date +%H:%M) person2x chain start-message exit=$ec" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/told_entry" --shift-days 14,15,28,29 >> "$LOG" 2>&1
echo "$(date +%H:%M) PERSON2X CHAIN FINISHED" >> "$LOG"
