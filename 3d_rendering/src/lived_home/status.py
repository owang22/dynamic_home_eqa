"""One status line for a run in progress, for monitoring.

    python -m lived_home.status <run folder> [--since N]   (N: lines of responses.jsonl already read)
"""
from __future__ import annotations

import json
import pathlib
import sys


def jl(p: pathlib.Path) -> list:
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def main() -> None:
    run = pathlib.Path(sys.argv[1])
    calls, events = jl(run / "calls.jsonl"), jl(run / "events.jsonl")
    failed, resp = jl(run / "failed.jsonl"), jl(run / "responses.jsonl")
    live = [c for c in calls if not c["cached"]]
    cost = sum(c["cost"] or 0 for c in live)
    real = [e for e in events if not e.get("implied") and e["verb"] != "come_home"]
    last = events[-1] if events else None
    where = f"day {last['day']} {last['time']} {last['resident']} {last['verb']} {last.get('object') or last.get('to') or ''}" if last else "-"
    slow = max((c["seconds"] for c in live[-10:]), default=0)
    probs = sum(1 for c in calls if c.get("problem"))
    print(f"calls {len(live)} ${cost:.2f} | answers {len(resp)} | actions {len(real)} rejected {len(failed)} "
          f"({100 * len(failed) / max(1, len(real) + len(failed)):.0f}%) | check retries {probs} | "
          f"slowest of last 10 calls {slow}s | now: {where}", flush=True)


if __name__ == "__main__":
    main()
