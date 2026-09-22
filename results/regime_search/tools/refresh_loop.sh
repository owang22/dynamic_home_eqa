#!/bin/bash
# Keeps story.html current while the overnight chain runs: every 20 minutes, re-extract whatever's on disk
# (finished run_log.jsonl or still-streaming calls.jsonl, for every known LLM-arm source) and rebuild the page.
# Runs detached (nohup) so it survives independent of any interactive session; stop it with
# `kill $(cat refresh_loop.pid)`.
cd ~/robot/dynamic_home_eqa/results/regime_search || exit 1
LOG=tools/refresh_loop.log
echo "$(date +%H:%M) refresh loop started (pid $$), every 20 min" >> "$LOG"
while true; do
  python3 tools/llm_live_extra.py >> "$LOG" 2>&1
  python3 tools/story_page.py story.html >> "$LOG" 2>&1
  python3 tools/story_numbers.py >> "$LOG" 2>&1
  echo "$(date +%H:%M) refreshed" >> "$LOG"
  sleep 1200
done
