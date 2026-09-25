#!/usr/bin/env python3
"""Is any run actually stuck? Reads the progress records, not the formatted table.

Two earlier versions of this check were wrong, both for the same reason: they
parsed a markdown table whose columns moved, and they keyed records by job name
so a restarted job inherited the record of the process it replaced. This reads
heartbeats.jsonl, keys on the process number, and asks the operating system
whether that process is alive.

A job counts as stuck only if it has no live process AND no newer process has
started for it. Prints one line; exits 1 if anything is stuck.
"""
import collections
import json
import pathlib
import subprocess
import sys
import time

BEATS = pathlib.Path("results/self_improve/three_prompts/heartbeats.jsonl")
QUIET_MINUTES = 15


def live_pids():
    out = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True).stdout
    alive = set()
    for line in out.splitlines():
        if "three_prompts" in line or "run_one_arm" in line or "search_driven" in line:
            try:
                alive.add(int(line.split(None, 1)[0]))
            except ValueError:
                pass
    return alive


def main():
    if not BEATS.exists():
        print("no progress records yet")
        return 0
    now, alive = time.time(), live_pids()
    newest = {}                       # (arm, home) -> newest record
    pids_per_job = collections.defaultdict(set)
    for line in BEATS.open():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        job = (d.get("arm"), d.get("household"))
        pids_per_job[job].add(d.get("pid"))
        if job not in newest or d.get("epoch", 0) > newest[job].get("epoch", 0):
            newest[job] = d

    stuck, waiting, running = [], [], []
    for job, rec in newest.items():
        quiet = (now - rec.get("epoch", 0)) / 60
        job_alive = bool(pids_per_job[job] & alive)
        if job_alive:
            (running if quiet <= QUIET_MINUTES else stuck).append((job, rec, quiet, True))
        elif quiet <= QUIET_MINUTES:
            waiting.append((job, rec, quiet, False))    # just restarted, not yet reported
        else:
            stuck.append((job, rec, quiet, False))

    print(f"{len(running)} running · {len(waiting)} restarted and not yet reporting · "
          f"{len(stuck)} STUCK · {len(alive)} live processes on the machine")
    for job, rec, quiet, was_alive in sorted(stuck, key=lambda z: -z[2]):
        print(f"  STUCK  {job[0]} / {job[1]}: day {rec.get('day')} of {rec.get('last_day')}, "
              f"quiet {quiet:.0f} min, process "
              f"{'alive but not progressing' if was_alive else 'gone'}")
    return 1 if stuck else 0


if __name__ == "__main__":
    sys.exit(main())
