#!/bin/bash
source "$(dirname "$0")/lane_common.sh"
echo "$(date +%H:%M) lane long-context: start+end pass launched in parallel with start-message (6 LC streams total)" >> "$LOG"
run told_entryreturn longcontext3 "$B3R" longcontext told 3; chk told_entryreturn 14,15,24
echo "$(date +%H:%M) lane long-context start+end DONE" >> "$LOG"
