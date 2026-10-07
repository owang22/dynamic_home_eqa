#!/bin/bash
# Claude Code status line hook: copies the JSON Claude Code hands it to a file with a timestamp,
# so agents can read plan usage (rate_limits) without a UI. Prints a one-line status.
IN=$(cat)
OUT=/home/oliver/robot/dynamic_home_eqa/coordination/usage.json
printf '%s' "$IN" | /home/oliver/miniconda3/bin/python -c '
import sys,json,time
d=json.load(sys.stdin); d["_written_at"]=time.strftime("%Y-%m-%dT%H:%M:%S%z"); d["_written_epoch"]=time.time()
json.dump(d,open(sys.argv[1],"w"),indent=1)
rl=d.get("rate_limits") or {}
parts=[]
for k in ("five_hour","seven_day","seven_day_opus"):
    v=rl.get(k)
    if isinstance(v,dict) and "used_percentage" in v: parts.append(f"{k} {v[\"used_percentage\"]:.0f}%")
print(" | ".join(parts) if parts else "usage: no rate_limits field")
' "$OUT"
