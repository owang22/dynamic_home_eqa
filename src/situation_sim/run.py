"""CLI: python -m situation_sim.run --seed 0 --out data/situation_sim/hh_s0_wed-sun

Writes trace.md, events.jsonl, hidden_state.json, then runs the checkpoint
checks (see checks.py) and prints their numbers.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from situation_sim.household import sample_household
from situation_sim.placement import compute_allowed
from situation_sim.schedule import load_activities
from situation_sim.simulate import Simulator
from situation_sim.situation import load_episodes, load_events, sample_situations
from situation_sim.trace import write_events, write_hidden_state, write_trace, write_trace_json


def generate(seed: int, out: pathlib.Path, n_days: int = 5) -> None:
    out.mkdir(parents=True, exist_ok=True)
    events = load_events()
    episodes = load_episodes()
    acts = load_activities()
    hh = sample_household(seed, acts)
    compute_allowed(hh, acts, events)
    sits = sample_situations(hh, seed, n_days, events, episodes)
    episode_id = f"{hh.id}_situation_seed{seed}"
    res = Simulator(hh, sits, events, acts, seed, episode_id).run()
    write_trace(out / "trace.md", hh, res, events)
    write_events(out / "events.jsonl", hh, res, n_days, episode_id)
    write_hidden_state(out / "hidden_state.json", hh, sits, res, events, seed, episodes)
    write_trace_json(out / "trace.json", hh, res)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--days", type=int, default=5)
    ap.add_argument("--no-checks", action="store_true")
    a = ap.parse_args(argv)
    generate(a.seed, a.out, a.days)
    print(f"wrote {a.out}/trace.md, events.jsonl, hidden_state.json, trace.json")
    if not a.no_checks:
        from situation_sim.checks import run_checks
        ok = run_checks(a.out, a.seed, a.days)
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
