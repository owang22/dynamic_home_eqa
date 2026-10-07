"""Active displacement probe runner (brief Section 4). Runs only the
load-bearing cells by default; --all-cells runs the full tier×policy grid so a
reviewer's "what about X" is one flag away, without spending submission compute
on unreferenced cells.

    python -m dynbelief.experiments.active_probe [--config ...] [--all-cells]
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np
import pandas as pd
import yaml

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief import MIN_PER_DAY
from dynbelief.active import metrics as M
from dynbelief.active.episode import max_looks_for, run_episode
from dynbelief.active.policies import (answer_now, make_sense_until_confident,
                                       make_voi_predictive, sense_once)
from dynbelief.beliefs import make_belief
from dynbelief.beliefs.fremen import constant_prior
from dynbelief.eqa.analysis import volatility_table
from dynbelief.eqa.probe import train_belief
from dynbelief.priors.schedule_prior import PerClassPrior, load_schedule_prior
from dynbelief.replay import ReplayWorld

_POLICY_FACTORY = {
    "answer_now": lambda: answer_now,
    "sense_once": lambda: sense_once,
    "sense_until_confident": make_sense_until_confident,
    "voi_predictive": make_voi_predictive,
}
ALL_TIERS = ["b0_lastseen", "b2_classdecay",
             "b3_perpetua_star(fremen)", "b3_perpetua_star(schedule_prior)"]


def _make_tier(label, world, ep_dir, train_days, train_min):
    if label.startswith("b3_perpetua_star("):
        src = label[len("b3_perpetua_star("):-1]
        if src == "schedule_prior":
            priors = load_schedule_prior(ep_dir, world, train_days)
            return make_belief("b3_perpetua_star", world,
                               switching_prior=PerClassPrior(priors, constant_prior()))
        return make_belief("b3_perpetua_star", world, f_source=src,
                           train_horizon_min=train_min)
    return make_belief(label, world, train_horizon_min=train_min)


def _sample_targets(world, test_days, per_stratum, seed):
    """Deliberate volatility mix (stable objects = over-sensing control)."""
    vol = volatility_table(world)
    strat = {r["obj_id"]: r["tercile"] for r in vol}
    rng = np.random.default_rng(seed)
    test = set(test_days)
    movers = {o for o in world.objects()
              if any(t // MIN_PER_DAY in test for t in world.change_times(o))}
    picked, chosen_strat = [], {}
    for s in ("static", "occasional", "dynamic"):
        pool = [o for o in world.objects() if strat[o] == s]
        # prefer test-day movers within the stratum but keep it a MIX
        pool.sort(key=lambda o: (o not in movers, rng.random()))
        take = pool[:per_stratum.get(s, 0)]
        picked += take
        for o in take:
            chosen_strat[o] = s
    return picked, chosen_strat


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(REPO_ROOT / "src/dynbelief/configs/active_probe.yaml"))
    ap.add_argument("--all-cells", action="store_true",
                    help="run the full tier x policy grid, not just load-bearing cells")
    ap.add_argument("--distance-weight", type=float, default=0.0)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    p = cfg["probe"]
    seed, n_boot = p["seed"], p["n_boot"]
    report_dir = REPO_ROOT / cfg["report_dir"]
    report_dir.mkdir(parents=True, exist_ok=True)

    # expand cells
    if args.all_cells:
        run_cells = [(t, pol) for t in cfg["tiers"] for pol in _POLICY_FACTORY]
    else:
        run_cells = []
        for c in cfg["cells"]:
            tiers = cfg["tiers"] if c["tiers"] == "all" else c["tiers"]
            run_cells += [(t, c["policy"]) for t in tiers]

    all_rows: dict = {}          # (scene, tier, policy) -> [episode rows]
    scene_meta = {}
    for ep in cfg["episodes"]:
        ep_dir = REPO_ROOT / ep["dir"]
        world = ReplayWorld(ep_dir)
        train_days = list(range(ep["train_days"]))
        test_days = [d for d in ep["test_days"] if d < world.n_days]
        train_min = ep["train_days"] * MIN_PER_DAY
        targets, strat = _sample_targets(world, test_days, p["per_stratum"], seed)
        n_rooms = len(world.rooms())
        scene_meta[ep["name"]] = {"n_rooms": n_rooms, "max_looks": max_looks_for(world),
                                  "chance": round(1.0 / (n_rooms + 1), 4),
                                  "targets": len(targets),
                                  "strata": {s: sum(1 for o in targets if strat[o] == s)
                                             for s in ("static", "occasional", "dynamic")},
                                  "test_days": test_days}
        hrs = p["grid_hours"]
        for tier in {t for t, _ in run_cells}:
            belief = _make_tier(tier, world, ep_dir, train_days, train_min)
            train_belief(belief, world, train_days, feed_min=p["train_feed_min"])
            for _t, policy_name in [(t, pn) for t, pn in run_cells if t == tier]:
                pol = _POLICY_FACTORY[policy_name]()
                rows = []
                for day in test_days:
                    d0 = day * MIN_PER_DAY
                    for obj in targets:
                        for i, hs in enumerate(hrs):
                            for hq in hrs[i + 1:]:
                                # fresh belief per episode (self-contained)
                                b = _make_tier(tier, world, ep_dir, train_days, train_min)
                                train_belief(b, world, train_days, feed_min=p["train_feed_min"])
                                r = run_episode(world, b, obj, d0 + hs * 60, d0 + hq * 60,
                                                pol, distance_weight=args.distance_weight)
                                r["stratum"] = strat[obj]
                                rows.append(r)
                all_rows[(ep["name"], tier, policy_name)] = rows
                acc = np.mean([r["correct"] for r in rows])
                lk = np.mean([r["looks_spent"] for r in rows])
                print(f"[{ep['name']}] {tier} / {policy_name}: "
                      f"acc={acc:.3f} looks={lk:.2f} n={len(rows)}", flush=True)

    # persist raw episodes
    flat = []
    for (scene, tier, policy), rows in all_rows.items():
        for r in rows:
            flat.append({**{k: v for k, v in r.items() if k != "sense_trace"},
                         "scene": scene, "tier": tier, "policy": policy,
                         "sense_trace": json.dumps(r["sense_trace"])})
    df = pd.DataFrame(flat)
    try:
        df.to_parquet(report_dir / "episodes.parquet")
    except Exception:
        df.to_csv(report_dir / "episodes.csv", index=False)

    _write_report(cfg, scene_meta, all_rows, report_dir, n_boot, seed)
    print(f"\nreport -> {report_dir / 'active_probe_gate.md'}")


def _fmt(s):
    return f"{s['mean']:.3f} [{s['lo']:.3f},{s['hi']:.3f}]" if s and s.get("n") else "—"


def _write_report(cfg, scene_meta, all_rows, report_dir, n_boot, seed):
    strat_by_scene = {}
    for (scene, tier, policy), rows in all_rows.items():
        strat_by_scene.setdefault(scene, {}).update({r["obj"]: r["stratum"] for r in rows})

    L = ["# Active probe — per-scene gate", ""]
    for scene, meta in scene_meta.items():
        L += [f"## {scene}  (n_rooms={meta['n_rooms']}, chance={meta['chance']}, "
              f"max_looks={meta['max_looks']}, targets={meta['targets']} "
              f"{meta['strata']})", "",
              "| tier | policy | acc [95% CI] | looks | looks: stable/occ/dyn | absten P/R/F1 |",
              "|---|---|---|---|---|---|"]
        so = strat_by_scene.get(scene, {})
        for (sc, tier, policy), rows in all_rows.items():
            if sc != scene:
                continue
            acc = M.summarize(rows, "correct", n_boot, seed)
            looks = M.summarize(rows, "looks_spent", n_boot, seed)
            ls = M.looks_by_stratum(rows, so)
            ab = M.abstention(rows, n_boot, seed)
            L.append(f"| {tier} | {policy} | {_fmt(acc)} | {looks['mean']:.2f} "
                     f"| {ls.get('static','-')}/{ls.get('occasional','-')}/{ls.get('dynamic','-')} "
                     f"| {ab['precision']}/{ab['recall']}/{ab['f1']} |")
        L.append("")
        # named-cell gaps (C2)
        def R(tier, pol):
            return all_rows.get((scene, tier, pol))
        b3f, b3s, b2 = "b3_perpetua_star(fremen)", "b3_perpetua_star(schedule_prior)", "b2_classdecay"
        gaps = []
        def addgap(name, a, b, key="correct"):
            if a and b:
                g = M.gap(a, b, key, n_boot, seed)
                gaps.append(f"- **{name}**: {g['gap']:+.3f} [{g['lo']:+.3f},{g['hi']:+.3f}]"
                            f"{' (CI-sep)' if g['sig'] else ''} (n_obj={g['n_obj']})")
        addgap("voi_b3f − sense_until_conf_b3f (re-prediction vs elimination)",
               R(b3f, "voi_predictive"), R(b3f, "sense_until_confident"))
        addgap("voi_b3f − answer_now_b3f (value of acting)",
               R(b3f, "voi_predictive"), R(b3f, "answer_now"))
        addgap("voi_b3f − voi_b2 (does predictive belief matter)",
               R(b3f, "voi_predictive"), R(b2, "voi_predictive"))
        addgap("answer_now_b3f − answer_now_b2 (routine vs decay, passive)",
               R(b3f, "answer_now"), R(b2, "answer_now"))
        addgap("answer_now_b3s − answer_now_b3f (LLM prior, passive)",
               R(b3s, "answer_now"), R(b3f, "answer_now"))
        addgap("voi_b3s − voi_b3f (LLM prior, active)",
               R(b3s, "voi_predictive"), R(b3f, "voi_predictive"))
        if gaps:
            L += ["**Named-cell gaps (paired per-object, C2):**", *gaps, ""]
    (report_dir / "active_probe_gate.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
