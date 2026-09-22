#!/bin/bash
# reflection lane: waits for its own start-message process (pid 998611), then start+end on 5 hh
source "$(dirname "$0")/lane_common.sh"
while kill -0 998611 2>/dev/null; do sleep 60; done
echo "$(date +%H:%M) lane reflection: start-message pass exited; start+end pass launched" >> "$LOG"
chk told_entry 14,15
run told_entryreturn reflection5 "$B5R" reflect told 10; chk told_entryreturn 14,15,24
echo "$(date +%H:%M) lane reflection DONE" >> "$LOG"
