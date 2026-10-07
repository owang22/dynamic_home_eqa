"""Quick check of an llm.py run directory against the written expectation: per-arm accuracy, fallback/parse-status
rate, prompt-token distribution (the longcontext question), and the noticing self-report's false-alarm rate on days
that should show no change.

    python3 -m baselines.patrol.llm_strategy_check --dir uq/llm_strategies/smoke
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
import sys


def load(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=pathlib.Path, required=True)
    ap.add_argument("--shift-days", default="", help="comma-separated days the noticing question SHOULD fire on (blank = none, i.e. every fire so far is a false alarm)")
    a = ap.parse_args(argv)
    shift_days = {int(x) for x in a.shift_days.split(",") if x}

    for run_dir in sorted(a.dir.glob("hh_s*_*_*_look*")):
        log = run_dir / "run_log.jsonl"
        if not log.exists():
            continue
        rows = load(log)
        n = len(rows)
        ok = sum(r["correct"] for r in rows)
        fallback = sum(r["fallback"] for r in rows)
        status = collections.Counter(r.get("status", "?") for r in rows)
        tok = [r["prompt_tokens"] for r in rows if r.get("prompt_tokens")]
        by_day = collections.defaultdict(list)
        for r in rows:
            by_day[r["day_index"]].append(r)
        day_acc = " ".join(f"d{d}:{100*sum(x['correct'] for x in rs)/len(rs):.0f}%" for d, rs in sorted(by_day.items()))
        print(f"\n== {run_dir.name} ==")
        print(f"  overall {ok}/{n} ({100*ok/n:.0f}%)  fallback {fallback} ({100*fallback/n:.0f}%)  status {dict(status)}")
        print(f"  per day: {day_acc}")
        if tok:
            print(f"  prompt_tokens: min {min(tok)} mean {sum(tok)/len(tok):.0f} max {max(tok)} (n={len(tok)})")
        # cold/warm split: first question about an object each day (before that day's feedback) vs later ones
        cold, warm = [], []
        seen_today: dict = {}
        for r in sorted(rows, key=lambda r: (r["day_index"], r["t_query"])):
            key = (r["day_index"], r["object_id"])
            (cold if key not in seen_today else warm).append(r)
            seen_today[key] = True
        if cold:
            print(f"  cold (first Q/object/day): {sum(r['correct'] for r in cold)}/{len(cold)} ({100*sum(r['correct'] for r in cold)/len(cold):.0f}%)"
                  f"   warm (later same day): {sum(r['correct'] for r in warm)}/{len(warm)} ({100*sum(r['correct'] for r in warm)/len(warm):.0f}%)" if warm else "  (no warm questions in this window)")

        nlog = run_dir / "noticing.jsonl"
        if nlog.exists():
            nrows = load(nlog)
            fires = [r for r in nrows if r["changed"]]
            false_alarms = [r for r in fires if r["day"] not in shift_days]
            print(f"  noticing: {len(nrows)} days answered, fired on days {[r['day'] for r in fires]}"
                  f" ({len(false_alarms)} false alarm{'s' if len(false_alarms) != 1 else ''} outside {sorted(shift_days) or '{}'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
