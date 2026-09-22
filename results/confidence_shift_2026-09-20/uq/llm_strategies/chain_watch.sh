#!/bin/bash
# every 5 min: per-arm progress sample + aggregate calls/min + STALLED verdicts into chain_progress.log
cd "$(dirname "$0")" || exit 1
while true; do
  python3 chain_watch.py 2>> chain_watch.err
  sleep 300
done
