#!/usr/bin/env bash
# Wait for a new agent note on the Go2 console (POST /agent/say from any client but control-pc),
# print it and exit. No LLM involved: a curl every 15 s. Used by Claude Code on the Z690 so other
# agents (cheetah) can ping it: "new post on the board / in the repo inbox".
URL=${URL:-http://localhost:8080}
seen() { curl -s -m5 "$URL/agent/status?client=watch" | python3 -c '
import json, sys
try: n = json.load(sys.stdin).get("notes", {})
except ValueError: sys.exit()
for c, v in sorted(n.items()):
    if c != "control-pc": print(c, v.get("t"), v.get("text", "").replace("\n", " "))'; }
base=$(seen)
while true; do
    sleep 15
    now=$(seen) || continue
    [ -z "$now" ] && [ -n "$base" ] && { base=$now; continue; }    # console restarted: notes cleared
    new=$(comm -13 <(echo "$base" | sort) <(echo "$now" | sort))
    [ -n "$new" ] && { echo "$new"; exit 0; }
done
