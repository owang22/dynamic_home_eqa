"""Day-budget active probe runner (day-budget brief Sections 2-5).

21 + scene-days across 3 scenes; policies are ONE family (order-by-belief,
stop-by-threshold) differing in stopping/allocation; day-level accuracy vs
shared budget B is the headline; cluster bootstrap at the (scene, day) level
(sequential coupling within a day makes the day the independence unit).

    python -m dynbelief.experiments.day_budget [--config ...] [--p4-budget B]
"""
from __future__ import annotations

import argparse
import copy
import json
import math

import numpy as np
import pandas as pd
import yaml

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief import MIN_PER_DAY
from dynbelief.active.day_loop import (day_answer_now, make_day_checklist,
                                       make_day_oracle, make_day_voi_adaptive,
                                       make_day_voi_fixed, make_schedule,
                                       oracle_allocation, run_day)
from dynbelief.active.room_belief import true_room_at
from dynbelief.beliefs import make_belief
from dynbelief.eqa.analysis import volatility_table
from dynbelief.eqa.probe import train_belief
from dynbelief.replay import ReplayWorld


def _policies():
    return {
        "answer_now": day_answer_now,
        "greedy_checklist": make_day_checklist(None),
        "rationed_checklist": make_day_checklist("ration"),
        "voi_fixed_0.02": make_day_voi_fixed(0.02),
        "voi_fixed_0.05": make_day_voi_fixed(0.05),
        "voi_fixed_0.15": make_day_voi_fixed(0.15),
        "voi_adaptive": make_day_voi_adaptive(),
        "oracle_allocator": None,   # built per (day, B) from true difficulties
    }


def _train_base(world, ep_dir, tier, train_days, feed):
    if tier == "b3_fremen":
        b = make_belief("b3_perpetua_star", world, f_source="fremen",
                        train_horizon_min=(max(train_days) + 1) * MIN_PER_DAY)
    elif tier == "b2":
        b = make_belief("b2_classdecay", world,
                        train_horizon_min=(max(train_days) + 1) * MIN_PER_DAY)
    else:
        raise ValueError(tier)
    train_belief(b, world, train_days, feed_min=feed)
    return b


def day_cluster_ci(rows, key="correct", n_boot=1000, seed=0, stat=np.mean):
    """Cluster bootstrap over (scene, day) — the independence unit."""
    by = {}
    for r in rows:
        by.setdefault((r["scene"], r["day"]), []).append(float(r[key]))
    keys = list(by)
    flat = [v for vs in by.values() for v in vs]
    if not flat:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n_days": 0}
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(n_boot):
        pick = rng.choice(len(keys), size=len(keys), replace=True)
        vs = [v for i in pick for v in by[keys[i]]]
        draws.append(stat(vs))
    return {"mean": float(stat(flat)), "lo": float(np.percentile(draws, 2.5)),
            "hi": float(np.percentile(draws, 97.5)), "n_days": len(keys),
            "n": len(flat)}


def run_all(cfg, elsewhere_excluded=False, budgets=None):
    """Full sweep. elsewhere_excluded=True is the P4 ablation: schedules are
    resampled (seeded) until no query's true answer is ELSEWHERE, isolating
    predictive abstention's contribution to the day-level margin."""
    run = cfg["run"]
    seed = run["seed"]
    budgets = budgets or run["budgets"]
    all_rows = []
    for sc in cfg["scenes"]:
        world = ReplayWorld(REPO_ROOT / sc["dir"])
        train_days = [d for d in sc["train_days"] if d in set(world.days)]
        test_days = [d for d in sc["test_days"] if d in set(world.days)]
        vol = {r["obj_id"]: r["tercile"] for r in volatility_table(world)}
        targets = list(world.objects())
        schedules = {}
        for d in test_days:
            s = make_schedule(world, d, targets, vol, seed,
                              q_per_day=run["q_per_day"],
                              frac_transition=run["frac_transition"])
            if elsewhere_excluded:
                # resample times/targets until no truly-elsewhere query (seeded walk)
                tries = 0
                while any(true_room_at(world, o, t) == "elsewhere" for t, o in s):
                    tries += 1
                    s = make_schedule(world, d, targets, vol, seed + 1000 + tries,
                                      q_per_day=run["q_per_day"],
                                      frac_transition=run["frac_transition"])
                    if tries > 200:
                        s = [(t, o) for t, o in s
                             if true_room_at(world, o, t) != "elsewhere"]
                        break
            schedules[d] = s
        base_b3 = _train_base(world, sc["dir"], "b3_fremen", train_days, run["train_feed_min"])
        base_b2 = _train_base(world, sc["dir"], "b2", train_days, run["train_feed_min"])
        pols = _policies()
        for B in budgets:
            for pname, pol in pols.items():
                for d in test_days:
                    sched = schedules[d]
                    if pname == "oracle_allocator":
                        ob = copy.deepcopy(base_b3)
                        ob.reset(world.objects(), world.receptacles(), d * MIN_PER_DAY)
                        ob.observe(d * MIN_PER_DAY, world.state_at(d * MIN_PER_DAY))
                        alloc = oracle_allocation(world, ob, sched, B)
                        pol_d = make_day_oracle(alloc)
                    else:
                        pol_d = pol
                    rows = run_day(world, copy.deepcopy(base_b3), d, sched, pol_d, B)
                    for r in rows:
                        r.update(scene=sc["name"], policy=pname, tier="b3_fremen",
                                 B=B, stratum=vol[r["obj"]])
                    all_rows += rows
            # anti-hollowing: voi_fixed(0.05) on b2 at the single mid budget
            if B == run["b2_cell_budget"]:
                for d in test_days:
                    rows = run_day(world, copy.deepcopy(base_b2), d, schedules[d],
                                   make_day_voi_fixed(0.05), B)
                    for r in rows:
                        r.update(scene=sc["name"], policy="voi_fixed_0.05",
                                 tier="b2", B=B, stratum=vol[r["obj"]])
                    all_rows += rows
        print(f"[{sc['name']}] done ({len(test_days)} days)", flush=True)
    return all_rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(REPO_ROOT / "src/dynbelief/configs/day_budget.yaml"))
    ap.add_argument("--p4-budget", type=int, default=None,
                    help="run ONLY the P4 elsewhere-excluded ablation at this budget")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    out = REPO_ROOT / cfg["report_dir"]
    out.mkdir(parents=True, exist_ok=True)

    if args.p4_budget is not None:
        rows = run_all(cfg, elsewhere_excluded=True, budgets=[args.p4_budget])
        pd.DataFrame(rows).to_parquet(out / f"queries_p4_B{args.p4_budget}.parquet")
        print(f"P4 ablation rows -> queries_p4_B{args.p4_budget}.parquet")
        return

    rows = run_all(cfg)
    df = pd.DataFrame(rows)
    df.to_parquet(out / "queries.parquet")

    nb, seed = cfg["run"]["n_boot"], cfg["run"]["seed"]
    lines = ["# Day-budget gate — day-level accuracy vs shared budget B",
             "", "Cluster bootstrap at the (scene, day) level. Tier b3_fremen unless noted.", ""]
    Q = cfg["run"]["q_per_day"]
    late_cut = math.ceil(0.7 * Q)
    for B in sorted(df.B.unique()):
        lines += [f"## B = {B}", "",
                  "| policy | day acc [95% CI] | late-30% acc | looks/day | forced | exhaust freq |",
                  "|---|---|---|---|---|---|"]
        for pol in ["answer_now", "greedy_checklist", "rationed_checklist",
                    "voi_fixed_0.02", "voi_fixed_0.05", "voi_fixed_0.15",
                    "voi_adaptive", "oracle_allocator"]:
            d = df[(df.B == B) & (df.policy == pol) & (df.tier == "b3_fremen")]
            if not len(d):
                continue
            rs = d.to_dict("records")
            acc = day_cluster_ci(rs, "correct", nb, seed)
            late = day_cluster_ci([r for r in rs if r["q_index"] >= late_cut],
                                  "correct", nb, seed)
            lpd = d.groupby(["scene", "day"]).looks_spent.sum().mean()
            forced = d.was_forced_answer_now.mean()
            exh = d.groupby(["scene", "day"]).B_remaining_after.min().eq(0).mean()
            lines.append(f"| {pol} | {acc['mean']:.3f} [{acc['lo']:.3f},{acc['hi']:.3f}] "
                         f"| {late['mean']:.3f} | {lpd:.1f} | {forced:.2f} | {exh:.2f} |")
        b2 = df[(df.B == B) & (df.tier == "b2")]
        if len(b2):
            a = day_cluster_ci(b2.to_dict("records"), "correct", nb, seed)
            lines.append(f"| voi_fixed_0.05 **on b2** | {a['mean']:.3f} "
                         f"[{a['lo']:.3f},{a['hi']:.3f}] | — | "
                         f"{b2.groupby(['scene','day']).looks_spent.sum().mean():.1f} | "
                         f"{b2.was_forced_answer_now.mean():.2f} | — |")
        lines.append("")
    (out / "day_budget_gate.md").write_text("\n".join(lines) + "\n")
    print(f"gate -> {out / 'day_budget_gate.md'}")


if __name__ == "__main__":
    main()
