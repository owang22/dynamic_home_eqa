#!/bin/bash
source "$(dirname "$0")/lane_common.sh"
mkdir -p $R/chain_person2x/told_entry
echo "$(date +%H:%M) lane two-spells: start-message pass launched in parallel with no-message" >> "$LOG"
python3 -m baselines.patrol.llm --bank $B2X --out $R/chain_person2x/told_entry --cache $R/chain_person2x/cache --memory naive retrieval --told told --look off --workers 6 --format conf > $R/chain_person2x/told_entry.log 2>&1
echo "$(date +%H:%M) person2x chain start-message (buffer+retrieval, 3 hh) exit=$?" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir $R/chain_person2x/told_entry --shift-days 14,15,28,29 >> "$LOG" 2>&1
echo "$(date +%H:%M) lane two-spells start-message DONE" >> "$LOG"
