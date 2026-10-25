"""Print a Claude Code stream-json session as it goes: the agent's words, its tool calls, results."""
import json, sys
for line in sys.stdin:
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if ev.get("type") == "assistant":
        for c in ev["message"].get("content", []):
            if c.get("type") == "text" and c["text"].strip():
                print(c["text"].strip(), flush=True)
            elif c.get("type") == "tool_use":
                name = c["name"].removeprefix("mcp__go2__")
                print(f"  → {name} {json.dumps(c.get('input') or {})}", flush=True)
    elif ev.get("type") == "user":
        for c in ev["message"].get("content", []):
            if isinstance(c, dict) and c.get("type") == "tool_result":
                parts = c.get("content")
                txt = parts if isinstance(parts, str) else " ".join(
                    p.get("text", "[image]") if p.get("type") == "text" else "[image]" for p in parts or [])
                print("    " + txt.replace("\n", " | ")[:300], flush=True)
    elif ev.get("type") == "result":
        print(f"\n[done: {ev.get('num_turns')} turns, {ev.get('duration_ms', 0) / 1000:.0f} s]", flush=True)
