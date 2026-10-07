"""Build every bank and run every classical agent, in parallel processes.

    python3 -m baselines.patrol.sweep --runs ../data/situation_sim/week8 --seeds 0-19 \
        --patrol-hours 1 2 4 8 --looks off voi top --out ../results/overnight_2026-09-20

Writes ``banks/hh_s<seed>_p<hours>.jsonl`` and
``classical/hh_s<seed>_p<hours>_<look>.jsonl``. A log that already exists
is skipped, so the sweep can be resumed.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple

from baselines.patrol.bank import build_bank
from baselines.patrol.run import BELIEFS, run_bank


def parse_seeds(s: str) -> List[int]:
    out: List[int] = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def one(job: Tuple[pathlib.Path, str, pathlib.Path, tuple]) -> str:
    bank, look, out, beliefs = job
    recs = run_bank(bank, look, beliefs)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    with open(tmp, "w") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    tmp.rename(out)
    return str(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=pathlib.Path, required=True, help="dir of situation_sim runs (hh_s<seed>)")
    ap.add_argument("--seeds", default="0-19")
    ap.add_argument("--patrol-hours", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--looks", nargs="+", default=["off", "voi", "top"])
    ap.add_argument("--beliefs", nargs="*", default=None)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--suffix", default="", help="log-name suffix, e.g. _perpetua for a belief subset")
    a = ap.parse_args(argv)
    beliefs = tuple(b for b in BELIEFS if a.beliefs is None or b["name"] in a.beliefs)
    jobs = []
    for seed in parse_seeds(a.seeds):
        for ph in a.patrol_hours:
            bank = build_bank(a.runs / f"hh_s{seed}", a.out / "banks" / f"hh_s{seed}_p{ph}.jsonl", ph)
            for look in a.looks:
                out = a.out / "classical" / f"hh_s{seed}_p{ph}_{look}{a.suffix}.jsonl"
                if out.exists():
                    continue
                jobs.append((bank, look, out, beliefs))
    print(f"{len(jobs)} jobs", file=sys.stderr, flush=True)
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(one, j) for j in jobs]
        for i, f in enumerate(as_completed(futs), 1):
            print(f"[{i}/{len(jobs)}] done {f.result()}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
