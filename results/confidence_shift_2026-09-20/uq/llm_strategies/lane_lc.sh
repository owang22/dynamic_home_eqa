#!/bin/bash
# long-context lane (03:33): waits for its running no-message pass (pid 1011686), then start, then start+end; 3 hh, 3 streams
source "$(dirname "$0")/lane_common.sh"
while kill -0 1011686 2>/dev/null; do sleep 60; done
echo "$(date +%H:%M) lane long-context: no-message pass exited; start-message next" >> "$LOG"
chk nottold 14,15
run told_entry longcontext3 "$B3" longcontext told 3; chk told_entry 14,15
run told_entryreturn longcontext3 "$B3R" longcontext told 3; chk told_entryreturn 14,15,24
echo "$(date +%H:%M) lane long-context DONE" >> "$LOG"
