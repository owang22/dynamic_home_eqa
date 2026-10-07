#!/usr/bin/env python3
"""Re-realize built households under extra simulator seeds. No LLM.

A household's LLM-authored half (persona, story, object rules) is fixed;
L4 realization is seeded, so a new seed re-runs the SAME home with
different jitter, skip, fragmentation and misplacement draws. That gives
repeats for variance — the same household, a different history — at zero
API cost.

Measured on the 20-household set: work departures move by minutes, but
only ~40% of (object, destination, hour) events recur across seeds and
12 of 34 objects end the month somewhere else. So a single-seed number
carries real seed noise (see reports/baselines/bakeoff_multiseed.md);
evaluate across seeds and report the spread.

Seeds other than 0 are NOT tracked in git (see .gitignore): they are
byte-deterministic from the tracked program.yaml plus the seed, so this
command rebuilds them exactly rather than the repo carrying ~40 MB per
seed.

Usage:
  python -m households.reseed --seeds 1 2 3 4          # every household
  python -m households.reseed --seeds 1 --household hh_001
  python -m households.reseed --seeds 1 2 --spatialize # + viewer traces
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

import yaml

from . import generate as g
from . import grid

DEFAULT_MODEL_DIR = grid.DATA_DIR / "generated" / "gpt-5.6-terra"


def reseed_household(hh_dir: pathlib.Path, seeds, days: int,
                     model: str) -> list:
    program = yaml.safe_load((hh_dir / "program.yaml").read_text())
    story = yaml.safe_load((hh_dir / "story.yaml").read_text())["days"]
    rules = yaml.safe_load(
        (hh_dir / "object_movement.yaml").read_text())["object_rules"]
    out = []
    for seed in seeds:
        meta = g.realize(hh_dir, program, story, rules, model, days, seed)
        out.append((seed, meta["n_events"]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--household", default=None, help="e.g. hh_001")
    ap.add_argument("--model-dir", type=pathlib.Path,
                    default=DEFAULT_MODEL_DIR)
    ap.add_argument("--days", type=int, default=None,
                    help="default: the control file's own `days`")
    ap.add_argument("--spatialize", action="store_true",
                    help="also write each seed's trace.json for the viewer")
    args = ap.parse_args()

    control = yaml.safe_load(
        (grid.DATA_DIR / "control.yaml").read_text())
    days = args.days or int(control["days"])
    model = args.model_dir.name
    hh_dirs = sorted(d for d in args.model_dir.glob("hh_*")
                     if (d / "program.yaml").exists())
    if args.household:
        hh_dirs = [d for d in hh_dirs if d.name == args.household]
    if not hh_dirs:
        raise SystemExit(f"no built households under {args.model_dir}")

    for hh_dir in hh_dirs:
        for seed, n in reseed_household(hh_dir, args.seeds, days, model):
            print(f"{hh_dir.name} seed {seed}: {n} events")
    if args.spatialize:
        for seed in args.seeds:
            cmd = [sys.executable, "-m", "households.make_viewer_configs",
                   "--seed", str(seed), "--spatialize"]
            if args.household:
                cmd += ["--household", args.household]
            subprocess.run(cmd, check=True,
                           cwd=grid.REPO_ROOT, stdout=subprocess.DEVNULL)
        print(f"spatialized seeds {args.seeds}")


if __name__ == "__main__":
    main()
