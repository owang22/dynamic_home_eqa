"""Render every snapshot with the third version (lib_v3, render_snapshot_v3.py). Resumable:
snapshots whose truth.json exists are skipped. Same set of times as run_all_v2.py.

    ~/miniconda3/envs/dynamic_eqa/bin/python run_all_v3.py [--workers 2] [--days 1-14] [--times 0800,...,2200]

    household A2 (another run of the generator):
    RUN_V3=/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/lived_home/hssd_a2 \
    PICS_V3=/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a2_v3 RUN_V3_LOGS=hssd_a2 \
        ~/miniconda3/envs/dynamic_eqa/bin/python run_all_v3.py --workers 2

Logs: run_v3/<RUN_V3_LOGS, default hssd_a>/logs/run_all.log, render_times.jsonl, snapshots/.
"""
import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import lib_v3
import lib
from run_all import PY, parse_days


def one(day, hhmm):
    if (lib.PICS / f"day_{day:02d}" / hhmm / "truth.json").exists():
        return day, hhmm, "already done", 0.0
    log = lib.CODE / "logs" / "snapshots" / f"day_{day:02d}_{hhmm}.log"
    t0 = time.time()
    with open(log, "w") as fh:
        r = subprocess.run([PY, str(lib_v3.RENDER / "render_snapshot_v3.py"), str(day), hhmm],
                           stdout=fh, stderr=subprocess.STDOUT, cwd=lib_v3.RENDER)
    return day, hhmm, "ok" if r.returncode == 0 else f"FAILED exit {r.returncode} (see {log.name})", time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--days", default="1-14")
    ap.add_argument("--times", default="0800,1000,1200,1400,1600,1800,2000,2200")
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
