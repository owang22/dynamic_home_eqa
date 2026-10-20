# Go2 dog-height copy (2026-10-19 evidence-memory study), made from the 1p4 files with 1.4 -> 0.4.
"""Render the 0.4 m set. Default: days 4-14 at 10:00, 14:00, 18:00, 22:00 (44 snapshots).
Resumable: snapshots whose truth.json exists are skipped.

    ~/miniconda3/envs/dynamic_eqa/bin/python run_all_0p4.py [--workers 2] [--days 4-14] [--times 1000,1400,1800,2200]

What exists (2026-10-19, for go2/evidence_memory): days 3-7, every 2 h from 08:00 to 22:00
(40 snapshots), i.e. --days 3-7 --times 0800,1000,1200,1400,1600,1800,2000,2200.

Logs: run_0p4/logs/run_all.log, run_0p4/logs/render_times.jsonl, run_0p4/logs/snapshots/.
"""
import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import lib_0p4
import lib
from run_all import PY, parse_days


def one(day, hhmm):
    if (lib.PICS / f"day_{day:02d}" / hhmm / "truth.json").exists():
        return day, hhmm, "already done", 0.0
    log = lib.CODE / "logs" / "snapshots" / f"day_{day:02d}_{hhmm}.log"
    t0 = time.time()
    with open(log, "w") as fh:
        r = subprocess.run([PY, str(lib_0p4.RENDER / "render_snapshot_0p4.py"), str(day), hhmm],
                           stdout=fh, stderr=subprocess.STDOUT, cwd=lib_0p4.RENDER)
    return day, hhmm, "ok" if r.returncode == 0 else f"FAILED exit {r.returncode} (see {log.name})", time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--days", default="4-14")
    ap.add_argument("--times", default="1000,1400,1800,2200")
    a = ap.parse_args()
    have = set(lib.all_snapshots())
    todo = [(d, t) for d in parse_days(a.days) for t in a.times.split(",") if (d, t) in have]
    missing = [(d, t) for d in parse_days(a.days) for t in a.times.split(",") if (d, t) not in have]
    if missing:
        print("no snapshot file for", missing, flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool, open(lib.CODE / "logs" / "run_all.log", "a") as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} start: {len(todo)} snapshots, {a.workers} workers\n")
        log.flush()
        for day, hhmm, status, secs in pool.map(lambda x: one(*x), todo):
            line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} day {day:02d} {hhmm}: {status} {secs:.1f}s"
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} end: {time.time() - t0:.0f}s\n")


if __name__ == "__main__":
    sys.exit(main())
