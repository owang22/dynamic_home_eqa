"""Render every snapshot of household A, resumable: snapshots whose truth.json exists are skipped.

    ~/miniconda3/envs/dynamic_eqa/bin/python run_all.py [--workers 2] [--days 4-14,1-3]

Each snapshot runs in its own process (render_snapshot.py), so a crash loses one snapshot only.
Per-snapshot output goes to logs/snapshots/day_XX_HHMM.log; one line per snapshot is added to
logs/run_all.log, and render_snapshot.py adds its timings to logs/render_times.jsonl.
"""
import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import lib

PY = "/home/oliver/miniconda3/envs/dynamic_eqa/bin/python"


def parse_days(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def one(day, hhmm):
    if (lib.PICS / f"day_{day:02d}" / hhmm / "truth.json").exists():
        return day, hhmm, "already done", 0.0
    log = lib.CODE / "logs" / "snapshots" / f"day_{day:02d}_{hhmm}.log"
    t0 = time.time()
    with open(log, "w") as fh:
        r = subprocess.run([PY, str(lib.CODE / "render_snapshot.py"), str(day), hhmm],
                           stdout=fh, stderr=subprocess.STDOUT, cwd=lib.CODE)
    return day, hhmm, "ok" if r.returncode == 0 else f"FAILED exit {r.returncode} (see {log.name})", time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--days", default="4-14,1-3")
    a = ap.parse_args()
    (lib.CODE / "logs" / "snapshots").mkdir(parents=True, exist_ok=True)
    have = set(lib.all_snapshots())
    todo = [(d, t) for d in parse_days(a.days) for (dd, t) in sorted(have) if dd == d]
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
