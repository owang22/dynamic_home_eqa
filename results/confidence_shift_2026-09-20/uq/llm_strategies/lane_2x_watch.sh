#!/bin/bash
# keeps the no-message two-spells pass's own check running when it exits (its old wrapper was replaced)
source "$(dirname "$0")/lane_common.sh"
while kill -0 1025994 2>/dev/null; do sleep 60; done
echo "$(date +%H:%M) person2x chain no-message pass exited" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir $R/chain_person2x/nottold --shift-days 14,15,28,29 >> "$LOG" 2>&1
