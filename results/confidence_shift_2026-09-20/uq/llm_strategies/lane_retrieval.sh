#!/bin/bash
# retrieval lane (03:10): start+end pass, 10 hh, right after its start-message pass -- no waiting on other memories
source "$(dirname "$0")/lane_common.sh"
echo "$(date +%H:%M) lane retrieval: start+end pass launched" >> "$LOG"
run told_entryreturn retrieval "$B10R" retrieval told 30; chk told_entryreturn 14,15,24
echo "$(date +%H:%M) lane retrieval DONE" >> "$LOG"
