"""Score an LLM arm's once-a-day self-report ("has the routine changed?") as a detector, against the classical
e-detector's own fire days (mart_tt72's side.json) on the same household/regime — same convention as the classical
detector: a household clears the shift day if it fires on day 14 or 15 (or the regime's own shift-day list), a fire
before that is a false alarm.

    python3 -m baselines.patrol.uq_llm_noticing --noticing uq/llm_strategies/wide/hh_s0_..._retrieval_.../noticing.jsonl \
        --classical-side uq/regime/sick10_all/mart_tt72/hh_s0_t03.side.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--noticing", type=pathlib.Path, required=True)
    ap.add_argument("--classical-side", type=pathlib.Path, default=None, help="a mart_tt72 .side.json for the same household, for comparison")
    ap.add_argument("--shift-days", default="14,15", help="days that count as 'on time' if the detector fires there")
    a = ap.parse_args(argv)
    shift_days = {int(x) for x in a.shift_days.split(",")}

    rows = [json.loads(l) for l in a.noticing.open() if l.strip()]
    fires = sorted({r["day"] for r in rows if r["changed"]})
    on_time = [d for d in fires if d in shift_days]
    early = [d for d in fires if d < min(shift_days, default=10**9)]
    late_lead = [d for d in fires if d not in shift_days and d >= min(shift_days, default=0)]
    who_said = [(r["day"], r.get("who")) for r in rows if r["changed"]]
    print(f"{a.noticing}: {len(rows)} days answered, fired on {fires}")
    print(f"  on-time (day in {sorted(shift_days)}): {bool(on_time)}  false alarms before the shift: {early}  other fires: {[d for d in fires if d not in on_time and d not in early]}")
    print(f"  who named on each fire day: {who_said}")

    if a.classical_side and a.classical_side.exists():
        side = json.load(open(a.classical_side))
        cfires = sorted({int(f["day"]) for f in side.get("fires", [])})
        print(f"  classical change alarm (mart_tt72) on the same household fired on: {cfires}")
        print(f"  agreement: LLM on-time {bool(on_time)} vs classical on-time {any(d in shift_days for d in cfires)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
