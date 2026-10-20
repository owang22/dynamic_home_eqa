"""Run methods through simulated labs, one lab day at a time, saving after every day (rerun resumes).

    python run.py --methods last_seen,notes --seeds 0-9 [--tag _rerun] [--days 30] [--workers 48]

Writes runs/<method><tag>/seed_<k>.json: {"days": [per-day record], "state": method state after the last day}.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import world as W  # noqa: E402
from methods import METHODS  # noqa: E402

RUNS = HERE / "runs"


def run_day(world, m, day):
    fc, finfo = m.forecast(day)
    searches, seen = {}, {}
    for p in world.questions[day]:
        plan = fc[p]["plan"]
        found, n = None, 0
        for place in plan:
            n += 1
            seen[place] = W.look(world, day, place)
            if p in seen[place]:
                found = place
                break
        searches[p] = {"plan": plan, "found_at": found, "looks": n if found else len(plan)}
    for place in world.patrol[day]:
        seen[place] = W.look(world, day, place)
    report = {"day": day, "searches": searches, "seen": seen, "patrol": world.patrol[day], "forecast": fc}
    einfo = m.evening(day, report)
    return {"day": day, "forecast": fc, "searches": searches, "seen": seen,
            "forecast_info": finfo, "evening_info": einfo, "memory_after": m.state().get("memory")}


def run_chain(name, seed, tag, n_days):
    out = RUNS / f"{name}{tag}" / f"seed_{seed}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    world = W.make_world(seed)
    m = METHODS[name](world)
    days = []
    if out.exists():
        saved = json.loads(out.read_text())
        days = saved["days"]
        m.load(saved["state"])
    t0 = time.time()
    for day in range(len(days) + 1, n_days + 1):
        days.append(run_day(world, m, day))
        tmp = out.with_suffix(".tmp")
        tmp.write_text(json.dumps({"method": name, "seed": seed, "days": days, "state": m.state()}))
        os.replace(tmp, out)
        if m.llm:
            print(f"{time.strftime('%H:%M:%S')} {name}{tag} seed {seed} day {day} ({time.time() - t0:.0f} s)", flush=True)
    return name, seed, len(days)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", required=True)
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--tag", default="")
    ap.add_argument("--days", type=int, default=W.N_DAYS)
    ap.add_argument("--workers", type=int, default=48)
    a = ap.parse_args()
    lo, _, hi = a.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))
    jobs = [(n, s) for n in a.methods.split(",") for s in seeds]
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(run_chain, n, s, a.tag, a.days): (n, s) for n, s in jobs}
        for f in as_completed(futs):
            try:
                print("done", f.result(), flush=True)
            except Exception:  # noqa: BLE001 - e.g. ServerDown: the chain stops; its saved days stay, rerun resumes
                print("FAILED", futs[f], traceback.format_exc()[-1500:], flush=True)


if __name__ == "__main__":
    main()
