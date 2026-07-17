"""Stage 1c — multi-scene re-gate on calendar episodes (pre-Stage-2, round 2).

Adds to the stage1b battery:
  - multiple households (scene x persona), each its own 5-week calendar
    episode; per-scene b3-b2 displaced gaps (replication check) plus a
    pooled headline with clusters = (household, object);
  - the fremen_weekly tier (Section C) + per-class weekly-component report;
  - global-N discipline: every cell carries n_obj (the real n) and n_probe,
    heatmaps ship reliability-flagged (grey) thin cells;
  - Section D re-check: per-scene in-house p_elsewhere under the pinning fix.

Households whose generated days have a gap are TRUNCATED at the first
missing day: log_episode indexes days by list position, and a silent shift
would corrupt the calendar (day-of-week) alignment everything in Section C
depends on.

    python -m dynbelief.experiments.stage1c [--config .../stage1c.yaml]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

import numpy as np
import pandas as pd
import yaml

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief import ELSEWHERE_ID, MIN_PER_DAY
from dynbelief.beliefs import make_belief
from dynbelief.beliefs.base import object_class
from dynbelief.beliefs.fremen import constant_prior, weekly_component_report
from dynbelief.eqa.analysis import (bootstrap_ci, ece, predictability_table,
                                    volatility_table, volatility_summary)
from dynbelief.eqa.generate import make_question, validate_question_set
from dynbelief.eqa.probe import (accuracy_surface_n, plot_surface,
                                 probe_object, train_belief)
from dynbelief.experiments.stage1b import _reliability_plot, _tier_label
from dynbelief.logging import log_episode
from dynbelief.priors.schedule_prior import PerClassPrior, load_schedule_prior
from dynbelief.replay import ReplayWorld

TERCILES = ["static", "occasional", "dynamic"]


def _hh_folders(gen_dir: pathlib.Path, scene: str, profile: str) -> list[str]:
    """Ordered day folders for one household. Gaps (days that failed trace
    validation) are allowed: gt_logger now indexes days by folder suffix,
    not list position, so a gap no longer shifts the calendar. Both
    `<scene>_<profile>` (day 0, suffix-less) and `..._day<k>` occur."""
    pat = re.compile(rf"^{re.escape(scene)}_{re.escape(profile)}(?:_day(\d+))?$")
    by_day = {}
    for f in gen_dir.iterdir():
        m = pat.match(f.name)
        if m and (f / "manifest.json").exists():
            by_day[int(m.group(1) or 0)] = f.name
    return [by_day[d] for d in sorted(by_day)]


def _cluster_ci(recs: list[dict], n_boot: int, seed: int) -> dict:
    """Cluster bootstrap over (household, object)."""
    for r in recs:
        r.setdefault("cluster", f"{r['hh']}::{r['obj']}")
    m, lo, hi = bootstrap_ci(recs, "correct", "cluster", n_boot=n_boot, seed=seed)
    return {"acc": m, "lo": lo, "hi": hi, "n": len(recs),
            "n_obj": len({r["cluster"] for r in recs})}


def _fmt(c: dict) -> str:
    if not c["n"]:
        return "—"
    return (f"{c['acc']:.3f} [{c['lo']:.3f},{c['hi']:.3f}] "
            f"(n_obj={c['n_obj']}, n={c['n']})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(REPO_ROOT / "src/dynbelief/configs/stage1c.yaml"))
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    p = cfg["probe"]
    seed, n_boot = p["seed"], p["n_boot"]
    gen_dir = REPO_ROOT / cfg["episode"]["gen_dir"]
    report_dir = REPO_ROOT / cfg["report_dir"]
    cal_dir = report_dir / "calibration"
    cal_dir.mkdir(parents=True, exist_ok=True)

    tier_labels = [_tier_label(t) for t in p["tiers"]]
    all_recs: dict[tuple[str, str], list[dict]] = {(t, q): []
                                                   for t in tier_labels
                                                   for q in p["qtypes"]}
    hh_meta, weekly_rows, c1_qs = [], [], []
    pred_of_hh: dict[str, dict[int, float]] = {}

    for hh in cfg["episode"]["households"]:
        hh_key = f"{hh['scene']}_{hh['profile']}"
        folders = _hh_folders(gen_dir, hh["scene"], hh["profile"])
        if len(folders) < p["train_days_max"] + 2:
            hh_meta.append({"hh": hh_key, "days": len(folders),
                            "status": "SKIPPED (not enough contiguous days)"})
            continue
        ep_dir = REPO_ROOT / f"{cfg['episode']['out_root']}_{hh_key}"
        log_episode(gen_dir, folders, ep_dir)
        world = ReplayWorld(ep_dir)
        present = set(world.days)
        train_days = [d for d in range(min(p["train_days_max"], world.n_days))
                      if d in present]
        test_days = [d for d in p["test_days"] if d < world.n_days and d in present]
        rng = np.random.default_rng(seed)

        vol = volatility_table(world)
        pd.DataFrame(vol).to_csv(report_dir / f"volatility__{hh_key}.csv", index=False)
        pred = predictability_table(world)
        pd.DataFrame(pred).to_csv(report_dir / f"predictability__{hh_key}.csv", index=False)
        pred_of_hh[hh_key] = {r["obj_id"]: r["predictability"] for r in pred}
        tercile_of = {r["obj_id"]: r["tercile"] for r in vol}
        vs = volatility_summary(vol)

        test_set = set(test_days)
        moves_on_test = {o: sorted(t for t in world.change_times(o)
                                   if t // MIN_PER_DAY in test_set)
                         for o in world.objects()}
        targets, stratum_of = [], {}
        for terc in TERCILES:
            members = [o for o in world.objects() if tercile_of[o] == terc]
            movers = [o for o in members if moves_on_test[o]]
            rest = [o for o in members if not moves_on_test[o]]
            rng.shuffle(movers); rng.shuffle(rest)
            take = (movers + rest)[:p["per_stratum_cap"]]
            targets += take
            for o in take:
                stratum_of[o] = terc
        trans_tods = {(o, d): [t % MIN_PER_DAY for t in moves_on_test[o]
                               if t // MIN_PER_DAY == d]
                      for o in targets for d in test_days}
        hh_meta.append({"hh": hh_key, "days": len(folders), "status": "ok",
                        "n_objects": len(world.objects()),
                        "strata": {t: sum(1 for o in targets if stratum_of[o] == t)
                                   for t in TERCILES},
                        "test_days": test_days, **{f"vol_{k}": v for k, v in vs.items()}})

        # Section C report: per-class weekly structure (training days only)
        train_horizon = p["train_days_max"] * MIN_PER_DAY
        by_class: dict[str, list[int]] = {}
        for o in world.objects():
            cls = object_class(world.obj_label[o])
            by_class.setdefault(cls, []).extend(
                t for t in world.change_times(o) if t < train_horizon)
        for cls, times in sorted(by_class.items()):
            weekly_rows.append({"hh": hh_key, "class": cls,
                                **weekly_component_report(times, train_days)})

        # C1 spot-check continues on every new scene
        for day in test_days[:2]:
            d0 = day * MIN_PER_DAY
            for obj in targets[::4]:
                c1_qs.append(make_question(world, "room_now", obj,
                                           d0 + 300, d0 + 900, seed=seed))

        train_min = (max(train_days) + 1) * MIN_PER_DAY
        for tcfg in p["tiers"]:
            label = _tier_label(tcfg)
            if tcfg.get("f_source") == "schedule_prior":
                priors = load_schedule_prior(ep_dir, world, train_days)
                belief = make_belief(tcfg["name"], world,
                                     switching_prior=PerClassPrior(priors, constant_prior()))
            else:
                belief = make_belief(tcfg["name"], world,
                                     f_source=tcfg.get("f_source", "fremen"),
                                     train_horizon_min=train_min)
            train_belief(belief, world, train_days, feed_min=p["train_feed_min"])
            for qtype in p["qtypes"]:
                for day in test_days:
                    for obj in targets:
                        rs = probe_object(belief, world, obj, day, qtype,
                                          grid_min=p["grid_min"], seed=seed,
                                          transition_tods=trans_tods[(obj, day)])
                        for r in rs:
                            r["hh"] = hh_key
                            r["stratum"] = stratum_of[obj]
                        all_recs[(label, qtype)].extend(rs)
            print(f"[{hh_key}] {label}: done", flush=True)

    # ── persist records + heatmaps (pooled, uniform subset, n-flagged) ───────
    day_trans: list[int] = []
    for (label, qtype), recs in all_recs.items():
        if not recs:
            continue
        df = pd.DataFrame(recs)
        stem = f"probe__{label}__{qtype}__grid{p['grid_min']}__seed{seed}"
        try:
            df.to_parquet(report_dir / f"{stem}.parquet")
        except (ImportError, ValueError):
            df.to_csv(report_dir / f"{stem}.csv", index=False)
        g = p["grid_min"]
        uni = [r for r in recs
               if r["t_seen_tod"] % g == 0 and r["t_query_tod"] % g == 0]
        acc, n_probe, n_obj = accuracy_surface_n(uni, g)
        plot_surface(acc, day_trans, g,
                     f"A(t_seen,t_query) pooled {len(cfg['episode']['households'])} households "
                     f"— {label} — {qtype}",
                     report_dir / f"{stem}.png", n_probe=n_probe, n_obj=n_obj)

    val = validate_question_set(c1_qs) if c1_qs else {"n": 0}

    # ── gate tables ───────────────────────────────────────────────────────────
    def _split(recs):
        return {"all": recs,
                "displaced": [r for r in recs if r["displaced"]],
                "returned": [r for r in recs if r["returned"]],
                "stable": [r for r in recs if not r["displaced"] and not r["returned"]]}

    metrics, gate_rows = {}, []
    for (label, qtype), recs in all_recs.items():
        for stratum in ["ALL"] + TERCILES:
            sub = recs if stratum == "ALL" else [r for r in recs
                                                 if r["stratum"] == stratum]
            row = {"tier": label, "qtype": qtype, "stratum": stratum}
            for k, rs in _split(sub).items():
                c = _cluster_ci(rs, n_boot, seed)
                metrics[(label, qtype, stratum, k)] = c
                row[k] = _fmt(c)
            gate_rows.append(row)

    # replication: per-household displaced gap, b3 tiers vs b2
    b3s = [t for t in tier_labels if t.startswith("b3")]
    rep_rows = []
    hh_keys = [m["hh"] for m in hh_meta if m.get("status") == "ok"]
    for hh_key in hh_keys:
        for label in b3s:
            d3 = _cluster_ci([r for r in all_recs[(label, "location_now")]
                              if r["hh"] == hh_key and r["displaced"]], n_boot, seed)
            d2 = _cluster_ci([r for r in all_recs[("b2_classdecay", "location_now")]
                              if r["hh"] == hh_key and r["displaced"]], n_boot, seed)
            rep_rows.append({"hh": hh_key, "tier": label,
                             "b3_displaced": _fmt(d3), "b2_displaced": _fmt(d2),
                             "gap": (f"{d3['acc'] - d2['acc']:+.3f}"
                                     if d3["n"] and d2["n"] else "—")})

    # B1 replication pooled: within-dynamic predictability split
    b1c = {}
    for label in b3s:
        recs3 = [r for r in all_recs[(label, "location_now")]
                 if r["stratum"] == "dynamic" and r["displaced"]]
        recs2 = [r for r in all_recs[("b2_classdecay", "location_now")]
                 if r["stratum"] == "dynamic" and r["displaced"]]
        keys = sorted({(r["hh"], r["obj"]) for r in recs3})
        pv = {k: pred_of_hh[k[0]].get(k[1], 0.0) for k in keys}
        if not keys:
            continue
        med = float(np.median(list(pv.values())))
        out = {}
        for half, sel in [("low", {k for k in keys if pv[k] <= med}),
                          ("high", {k for k in keys if pv[k] > med})]:
            s3 = _cluster_ci([r for r in recs3 if (r["hh"], r["obj"]) in sel], n_boot, seed)
            s2 = _cluster_ci([r for r in recs2 if (r["hh"], r["obj"]) in sel], n_boot, seed)
            out[half] = {"b3": _fmt(s3), "b2": _fmt(s2),
                         "lead": round(s3["acc"] - s2["acc"], 4) if s3["n"] and s2["n"] else None,
                         "n_obj": len(sel)}
        b1c[label] = {"median_pred_dynamic": round(med, 4), **out}

    # D: calibration — pooled + per-scene ECE and in-house p_elsewhere
    d_rows = {}
    for label in tier_labels:
        recs = all_recs[(label, "location_now")]
        if not recs:
            continue
        entry = {"ece_pooled": ece(recs, conf_key="p_chosen")["ece"],
                 "n": len(recs)}
        e = ece(recs, conf_key="p_chosen")
        _reliability_plot(e["curve"], f"reliability — {label} — location_now "
                          f"(ECE={e['ece']:.3f}, n={len(recs)})",
                          cal_dir / f"reliability__{label}__location_now.png")
        if label.startswith("b3"):
            for hh_key in hh_keys:
                sub = [r for r in recs if r["hh"] == hh_key]
                entry[f"p_elsewhere__{hh_key}"] = round(
                    float(np.mean([r["p_elsewhere"] for r in sub])), 4) if sub else None
        d_rows[label] = entry

    # ── write gate report ─────────────────────────────────────────────────────
    def _tbl(rows, cols):
        out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
        return out

    weekly_df = pd.DataFrame(weekly_rows)
    weekly_df.to_csv(report_dir / "weekly_components.csv", index=False)
    n_weekly_sel = int(weekly_df["selected"].sum()) if len(weekly_df) else 0

    lines = ["# Stage 1c re-gate (multi-scene, calendar episodes)", "",
             "Households: " + json.dumps(hh_meta, default=str), "",
             f"C1 room_now spot-check: n={val.get('n')} (validator hard-asserts "
             "distinct options + truth presence).", "",
             "## Per-stratum accuracy — headline = displaced; "
             "clusters = (household, object)", "",
             *_tbl(gate_rows, ["tier", "qtype", "stratum", "all", "displaced",
                               "returned", "stable"]),
             "", "## Replication: per-household displaced gap (location_now)", "",
             *_tbl(rep_rows, ["hh", "tier", "b3_displaced", "b2_displaced", "gap"]),
             "", "## B1 (pooled within-dynamic predictability split)", "",
             "```json", json.dumps(b1c, indent=1), "```",
             "", f"## Section C: weekly components (weekly_components.csv; "
             f"{n_weekly_sel}/{len(weekly_df)} class-streams selected)", "",
             "", "## Section D: calibration + pinning generalization", "",
             "```json", json.dumps(d_rows, indent=1), "```"]
    (report_dir / "stage1c_gate.md").write_text("\n".join(lines) + "\n")
    print(f"report -> {report_dir / 'stage1c_gate.md'}")


if __name__ == "__main__":
    main()
