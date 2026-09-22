#!/bin/bash
# two-spells lane (03:33): buffer + retrieval, 3 hh — no message now (in parallel with long-context), then start message
source "$(dirname "$0")/lane_common.sh"
mkdir -p $R/chain_person2x/nottold $R/chain_person2x/told_entry
echo "$(date +%H:%M) lane two-spells: no-message pass launched (buffer+retrieval, 3 hh)" >> "$LOG"
python3 -m baselines.patrol.llm --bank $B2X --out $R/chain_person2x/nottold --cache $R/chain_person2x/cache --memory naive retrieval --told not_told --look off --workers 6 --format conf > $R/chain_person2x/nottold.log 2>&1
echo "$(date +%H:%M) person2x chain no-message (buffer+retrieval, 3 hh) exit=$?" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir $R/chain_person2x/nottold --shift-days 14,15,28,29 >> "$LOG" 2>&1
python3 -m baselines.patrol.llm --bank $B2X --out $R/chain_person2x/told_entry --cache $R/chain_person2x/cache --memory naive retrieval --told told --look off --workers 6 --format conf > $R/chain_person2x/told_entry.log 2>&1
echo "$(date +%H:%M) person2x chain start-message (buffer+retrieval, 3 hh) exit=$?" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir $R/chain_person2x/told_entry --shift-days 14,15,28,29 >> "$LOG" 2>&1
echo "$(date +%H:%M) lane two-spells DONE" >> "$LOG"
