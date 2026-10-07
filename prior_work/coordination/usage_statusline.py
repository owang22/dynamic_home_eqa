#!/home/oliver/miniconda3/bin/python
"""Claude Code status line hook.

Claude Code pipes a JSON object to the status line command on every refresh. This script
copies that object, with a timestamp, to coordination/usage.json so that agents can read
plan usage (the rate_limits field, when the running version provides it) without a UI,
and prints a one-line status for the terminal. Configured in ~/.claude/settings.json
under "statusLine".
"""
import json
import sys
import time

OUT = "/home/oliver/robot/dynamic_home_eqa/coordination/usage.json"

raw = sys.stdin.read()
try:
    d = json.loads(raw) if raw.strip() else {}
except json.JSONDecodeError:
    d = {"_unparsed": raw[:2000]}
d["_written_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
d["_written_epoch"] = time.time()
with open(OUT, "w") as f:
    json.dump(d, f, indent=1)

rl = d.get("rate_limits") or {}
parts = []
for k, v in rl.items() if isinstance(rl, dict) else []:
    if isinstance(v, dict) and "used_percentage" in v:
        parts.append(f"{k} {v['used_percentage']:.0f}%")
model = (d.get("model") or {}).get("display_name", "")
print((model + " | " if model else "") + (" | ".join(parts) if parts else "usage: no rate_limits field"))
