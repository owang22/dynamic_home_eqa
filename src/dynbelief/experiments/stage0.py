"""Stage 0 gate: run every belief tier under both schedules over >= 5
evaluated sim-days; write metrics + sanity ordering to reports/stage0/.

    python -m dynbelief.experiments.stage0 [--config src/dynbelief/configs/stage0.yaml]

Result filenames encode the full run config
(<tier>__<schedule>__seed<k>__train<d>__eval<d>.parquet/json).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

import yaml

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief import MIN_PER_DAY
from dynbelief.beliefs import make_belief, BELIEF_TIERS
from dynbelief.logging import log_episode
from dynbelief.perception import OraclePerceiver
from dynbelief.replay import ReplayWorld, Viewpoints
from dynbelief.replay.metrics import compute_metrics
from dynbelief.replay.runner import run_schedule, save_run
from dynbelief.replay.schedules import random_uniform, round_robin


def _discover_folders(gen_dir: pathlib.Path) -> list[str]:
    days = []
    for p in gen_dir.iterdir():
        m = re.search(r"_day(\d+)$", p.name)
        if m and (p / "manifest.json").exists():
            days.append((int(m.group(1)), p.name))
    return [name for _, name in sorted(days)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(REPO_ROOT / "src/dynbelief/configs/stage0.yaml"))
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))

    gen_dir = REPO_ROOT / cfg["episode"]["gen_dir"]
    folders = cfg["episode"]["folders"] or _discover_folders(gen_dir)
    ep_dir = REPO_ROOT / cfg["episode"]["out_dir"]
    log_episode(gen_dir, folders, ep_dir)

    world = ReplayWorld(ep_dir)
    vps = Viewpoints.load(ep_dir, world)
    run = cfg["run"]
    perceiver = OraclePerceiver(world, **run["perceiver"])

    train_min = run["train_days"] * MIN_PER_DAY
    t1 = (run["train_days"] + run["eval_days"]) * MIN_PER_DAY
    assert t1 <= world.horizon_min(), (
        f"config needs {t1} min but episode has {world.horizon_min()}")

    report_dir = REPO_ROOT / cfg["report_dir"]
    report_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, dict]] = {}

    for sched_name, sched_cfg in run["schedules"].items():
        if sched_name == "round_robin":
            schedule = round_robin(vps, sched_cfg["period_min"], 0, t1)
        elif sched_name == "random_uniform":
            schedule = random_uniform(vps, sched_cfg["rate_per_hour"], 0, t1,
                                      seed=run["seed"])
        else:
            raise ValueError(sched_name)
        for tier in run["tiers"]:
            belief = make_belief(tier, world, f_source=run.get("b3_f_source", "fremen"),
                                 train_horizon_min=train_min)
            df = run_schedule(world, vps, perceiver, belief, schedule,
                              t0=0, t1=t1, grid_min=run["grid_min"],
                              log_from=train_min)
            stem = (f"{tier}__{sched_name}__seed{run['seed']}"
                    f"__train{run['train_days']}__eval{run['eval_days']}")
            save_run(df, report_dir / f"{stem}.parquet")
            m = compute_metrics(df, world, train_min, t1)
            (report_dir / f"{stem}.metrics.json").write_text(json.dumps(m, indent=1))
            results.setdefault(sched_name, {})[tier] = m
            print(f"{stem}: map_err={m['map_error_overall']:.3f} "
                  f"(moved {m['map_error_moved']}) logloss={m['log_loss']:.3f}")

    # ---- gate report: sanity ordering b3 >= b2 >= b1 >= b0 (lower error) ----
    lines = ["# Stage 0 gate report", "",
             f"episode: {cfg['episode']['out_dir']} ({world.n_days} days, "
             f"{len(world.objects())} objects, "
             f"{len(world.receptacles()) - 1} receptacles)", "",
             "| schedule | tier | map_err | moved | placed | elsewhere | log_loss | brier |",
             "|---|---|---|---|---|---|---|---|"]
    deviations = []
    for sched_name, tiers in results.items():
        for tier in run["tiers"]:
            m = tiers[tier]
            lines.append(f"| {sched_name} | {tier} | {m['map_error_overall']:.4f} "
                         f"| {m['map_error_moved']:.3f} | {m['map_error_placed']:.3f} "
                         f"| {m['map_error_elsewhere']:.3f} | {m['log_loss']:.3f} "
                         f"| {m['brier']:.3f} |")
        order = [tiers[t]["map_error_overall"] for t in BELIEF_TIERS if t in tiers]
        for hi, lo in zip(order, order[1:]):
            if lo > hi + 1e-9:
                deviations.append(sched_name)
                break
    lines += ["", "## Sanity ordering (b3 <= b2 <= b1 <= b0 map error)",
              "PASS on all schedules" if not deviations else
              f"DEVIATION on: {sorted(set(deviations))} — recorded, see metrics."]
    (report_dir / "stage0_gate.md").write_text("\n".join(lines) + "\n")
    print(f"\nreport -> {report_dir / 'stage0_gate.md'}")


if __name__ == "__main__":
    main()
