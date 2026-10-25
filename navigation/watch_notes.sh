#!/usr/bin/env bash
# Wait for something new for the Z690 agent, print it and exit. No LLM involved:
#  - a new agent note on the Go2 console (POST /agent/say from any client but control-pc), a curl every 15 s;
#  - a new message file in the repo inbox (coordination/inbox/z690 or all), a git fetch every 2 min.
# Used by Claude Code on the Z690 so other agents (cheetah) can reach it.
URL=${URL:-http://localhost:8080}
REPO=${REPO:-$HOME/dynamic_home_eqa}
seen() { curl -s -m5 "$URL/agent/status?client=watch" | python3 -c '
import json, sys
try: n = json.load(sys.stdin).get("notes", {})
except ValueError: sys.exit()
for c, v in sorted(n.items()):
    if c != "control-pc" and not c.startswith(("vlm-bench", "loc-research")): print(c, v.get("t"), v.get("text", "").replace("\n", " "))'; }
inbox() { git -C "$REPO" ls-tree -r --name-only "$1" -- coordination/inbox/z690 coordination/inbox/all 2>/dev/null; }
base=$(seen)
git -C "$REPO" fetch -q 2>/dev/null; gbase=$(inbox origin/main)
i=0
while true; do
    sleep 15; i=$((i + 1))
    if now=$(seen); then
        if [ -z "$now" ] && [ -n "$base" ]; then base=$now     # console restarted: notes cleared
        else
            new=$(comm -13 <(echo "$base" | sort) <(echo "$now" | sort))
            [ -n "$new" ] && { echo "$new"; exit 0; }
        fi
    fi
    if [ $((i % 8)) -eq 0 ] && timeout 60 git -C "$REPO" fetch -q 2>/dev/null; then
        new=$(comm -13 <(echo "$gbase" | sort) <(inbox origin/main | sort))
        [ -n "$new" ] && { echo "repo inbox: $new"; exit 0; }
    fi
done
