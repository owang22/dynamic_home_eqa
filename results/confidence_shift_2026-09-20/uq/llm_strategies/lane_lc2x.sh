#!/bin/bash
# long-context + two-spells lane (03:10): LC no message -> LC start -> two-spells no message -> LC start+end -> two-spells start
source "$(dirname "$0")/lane_common.sh"
echo "$(date +%H:%M) lane long-context/two-spells: started (3 hh, 3 streams; server had 0 waiting)" >> "$LOG"
run nottold longcontext3 "$B3" longcontext not_told 3
run told_entry longcontext3 "$B3" longcontext told 3
mkdir -p $R/chain_person2x/nottold $R/chain_person2x/told_entry
python3 -m baselines.patrol.llm --bank $B2X --out $R/chain_person2x/nottold --cache $R/chain_person2x/cache --memory naive retrieval --told not_told --look off --workers 6 --format conf > $R/chain_person2x/nottold.log 2>&1
echo "$(date +%H:%M) person2x chain no-message (buffer+retrieval, 3 hh) exit=$?" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir $R/chain_person2x/nottold --shift-days 14,15,28,29 >> "$LOG" 2>&1
run told_entryreturn longcontext3 "$B3R" longcontext told 3
python3 -m baselines.patrol.llm --bank $B2X --out $R/chain_person2x/told_entry --cache $R/chain_person2x/cache --memory naive retrieval --told told --look off --workers 6 --format conf > $R/chain_person2x/told_entry.log 2>&1
echo "$(date +%H:%M) person2x chain start-message (buffer+retrieval, 3 hh) exit=$?" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir $R/chain_person2x/told_entry --shift-days 14,15,28,29 >> "$LOG" 2>&1
echo "$(date +%H:%M) lane long-context/two-spells DONE" >> "$LOG"
