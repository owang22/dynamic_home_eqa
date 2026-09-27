#!/usr/bin/env python3
"""Generate households and banks for a scenario whose events live in THIS directory.

The simulator's own loaders already take a path (`load_events(path)`,
`load_activities(path)`), so a new scenario needs no change to any shared file: this
script points them at `scenario/events.yaml` and `scenario/activities.yaml` and leaves
`src/situation_sim/*.yaml` and `configs/regime/*` exactly as the other paper's frozen
runs found them.

    python3 results/self_improve/make_scenario.py --config results/self_improve/scenario/illness_v1.yaml --seeds 0-9

Writes the simulations under the config's `sim_dir` and the banks under
`<out>/banks/hh_s<seed>_<label>.jsonl`, then you run check_scenario.py on `<out>`.
No classical beliefs are run and no model is called: this is world generation only.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))

import yaml  # noqa: E402


def parse_seeds(spec: str):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def simulate(cfg, seed: int, sim_dir: pathlib.Path, events_path, activities_path):
    """situation_sim.run.generate, but with our own events and activities files."""
    from situation_sim.household import sample_household
    from situation_sim.placement import compute_allowed
    from situation_sim.schedule import load_activities
    from situation_sim.simulate import Simulator
    from situation_sim.situation import load_episodes, load_events, sample_situations
    from situation_sim.trace import (write_events, write_hidden_state, write_trace,
                                     write_trace_json)

    out = sim_dir / f"hh_s{seed}"
    out.mkdir(parents=True, exist_ok=True)
    events = load_events(events_path)
    episodes = load_episodes()
    acts = load_activities(activities_path)

    # the p_day rates the config asks for, applied in memory only - never written back
    for name, rates in (cfg.get("events") or {}).items():
        if name in events:
            events[name]["p_day"] = dict(rates)

    hh = sample_household(seed, acts)
    calendar = cfg["calendar"]
    extra_roles = {}
    for st in calendar:
        for who, role in (st.get("roles") or {}).items():
            r = next((r for r in hh.residents.values()
                      if r.id == who or r.name.lower() == str(who).lower()), None)
            if r is not None:
                extra_roles.setdefault(r.id, [])
                if role not in extra_roles[r.id]:
                    extra_roles[r.id].append(role)
    compute_allowed(hh, acts, events, extra_roles=extra_roles or None)
    sits = sample_situations(hh, seed, cfg["days"], events, episodes,
                             day0=cfg.get("day0", "Monday"), calendar=calendar)
    episode_id = f"{hh.id}_situation_seed{seed}"
    res = Simulator(hh, sits, events, acts, seed, episode_id).run()
    write_trace(out / "trace.md", hh, res, events)
    write_events(out / "events.jsonl", hh, res, cfg["days"], episode_id)
    write_hidden_state(out / "hidden_state.json", hh, sits, res, events, seed, episodes)
    write_trace_json(out / "trace.json", hh, res)
    return out


def bank(cfg, run_dir: pathlib.Path, out_path: pathlib.Path, activities_path=None):
    """The question builder reads the activity list to turn a trace line back into an
    activity name, and it hard-codes the default file. A scenario with its own
    activities would therefore have every one of its new activities silently ignored -
    no question is ever drawn from them, so the very hours the disruption lives in end
    up nearly empty. We point it at the same file the simulation used. Nothing on disk
    changes; the substitution lasts for this call."""
    import baselines.patrol.bank as bankmod
    from baselines.patrol.bank import build_bank
    if activities_path is not None:
        import yaml as _yaml
        acts = _yaml.safe_load(pathlib.Path(activities_path).read_text())["activities"]
        bankmod.load_activities = lambda: acts
    os.environ["PATROL_QUESTION_MOMENT"] = str(cfg.get("question_moment", "during"))
    os.environ["PATROL_QUESTION_MIN_GAP_MIN"] = str(int(cfg.get("question_min_gap_min", 30)))
    owners = cfg.get("question_owners") or []
    os.environ["PATROL_QUESTION_OWNERS"] = ",".join(owners)
    if cfg.get("question_hours"):
        os.environ["PATROL_QUESTION_HOURS"] = str(cfg["question_hours"])
    else:
        os.environ.pop("PATROL_QUESTION_HOURS", None)
    times = [t.strip() for t in str(cfg.get("patrol_times", "03:00")).split(",") if t.strip()]
    minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
    return build_bank(run_dir, out_path,
                      patrol_hours=int(cfg.get("patrol_hours", 0)),
                      patrol_times=minutes,
                      questions=cfg.get("questions", "activity"),
                      classes=cfg.get("classes"),
                      per_day=int(cfg.get("per_day", 24)),
                      oversample=int(cfg.get("oversample", 1024)),
                      shift_focus=float(cfg.get("shift_focus", 0.0)),
                      feedback_delay_min=cfg.get("feedback_delay_min"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=pathlib.Path, required=True)
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--out", type=pathlib.Path, default=None)
    ap.add_argument("--fresh", action="store_true", help="delete the simulations first")
    a = ap.parse_args(argv)

    cfg = yaml.safe_load(a.config.read_text())
    base = a.config.parent
    sim_dir = (base / cfg["sim_dir"]).resolve() if not pathlib.Path(cfg["sim_dir"]).is_absolute() \
        else pathlib.Path(cfg["sim_dir"])
    out = a.out or (HERE / "runs" / cfg["name"])
    events_path = (base / cfg.get("events_file", "events.yaml")).resolve()
    activities_path = (base / cfg.get("activities_file", "activities.yaml")).resolve()
    label = "t" + str(cfg.get("patrol_times", "03:00")).split(",")[0].split(":")[0]

    if a.fresh and sim_dir.exists():
        shutil.rmtree(sim_dir)
    (out / "banks").mkdir(parents=True, exist_ok=True)
    (out / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=True))

    for seed in parse_seeds(a.seeds):
        run_dir = sim_dir / f"hh_s{seed}"
        if not (run_dir / "events.jsonl").exists():
            simulate(cfg, seed, sim_dir, events_path, activities_path)
        bank_path = out / "banks" / f"hh_s{seed}_{label}.jsonl"
        bank(cfg, run_dir, bank_path, activities_path)
        print(f"  seed {seed}: {bank_path}")
    print(f"banks in {out}/banks")
    print(f"now run: python3 results/self_improve/check_scenario.py {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
