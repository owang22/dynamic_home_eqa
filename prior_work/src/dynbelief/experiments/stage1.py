"""Stage 1 gate: displacement-probe A(t_seen, t_query) heatmaps for
location_now and room_now across the belief tiers, with question-set
validation and the Δt-symmetry check.

    python -m dynbelief.experiments.stage1 [--config .../stage1.yaml]
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
from dynbelief.beliefs import make_belief
from dynbelief.eqa.generate import make_question, validate_question_set
from dynbelief.eqa.probe import (accuracy_surface, delta_t_symmetry,
                                 plot_surface, probe_object, train_belief)
from dynbelief.logging import log_episode
from dynbelief.priors.schedule_prior import PerClassPrior, load_schedule_prior
from dynbelief.beliefs.fremen import constant_prior
from dynbelief.replay import ReplayWorld
from dynbelief.experiments.stage0 import _discover_folders


def _tier_label(tcfg: dict) -> str:
    return tcfg["name"] + (f"({tcfg['f_source']})" if "f_source" in tcfg else "")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(REPO_ROOT / "src/dynbelief/configs/stage1.yaml"))
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))

    gen_dir = REPO_ROOT / cfg["episode"]["gen_dir"]
    folders = cfg["episode"]["folders"] or _discover_folders(gen_dir)
    ep_dir = REPO_ROOT / cfg["episode"]["out_dir"]
    log_episode(gen_dir, folders, ep_dir)
    world = ReplayWorld(ep_dir)

    p = cfg["probe"]
    train_days, test_days = p["train_days"], p["test_days"]
    assert not set(train_days) & set(test_days), "train/test days must be disjoint"
    assert max(test_days) < world.n_days, "test day beyond episode"

    # target objects: those that actually move on the test days
    if p["target_objects"] == "moved":
        targets = sorted({e["object_id"] for e in world.events(moved_by="human")
                          if e["t_min"] // MIN_PER_DAY in set(test_days)})
    else:
        targets = world.objects()

    report_dir = REPO_ROOT / cfg["report_dir"]
    report_dir.mkdir(parents=True, exist_ok=True)

    # ---- question-set validation (gate criterion) ---------------------------
    val_qs = []
    for day in test_days:
        d0 = day * MIN_PER_DAY
        for obj in targets[:8]:
            for qtype in p["qtypes"]:
                for s, q in [(d0 + 480, d0 + 720), (d0 + 540, d0 + 1200),
                             (d0 + 60, d0 + 600), (d0 + 900, d0 + 1380)]:
                    val_qs.append(make_question(world, qtype, obj, s, q, seed=p["seed"]))
    val = validate_question_set(val_qs)
    (report_dir / "question_validation.json").write_text(json.dumps(val, indent=1))

    # ---- probe sweep ---------------------------------------------------------
    train_min = (max(train_days) + 1) * MIN_PER_DAY
    summary_rows = []
    for tcfg in p["tiers"]:
        label = _tier_label(tcfg)
        if tcfg.get("f_source") == "schedule_prior":
            priors = load_schedule_prior(ep_dir, world, train_days)
            sp = PerClassPrior(priors, constant_prior())
            belief = make_belief(tcfg["name"], world, switching_prior=sp)
        else:
            belief = make_belief(tcfg["name"], world,
                                 f_source=tcfg.get("f_source", "fremen"),
                                 train_horizon_min=train_min)
        train_belief(belief, world, train_days, feed_min=p["train_feed_min"])

        for qtype in p["qtypes"]:
            records = []
            for day in test_days:
                for obj in targets:
                    records.extend(probe_object(belief, world, obj, day, qtype,
                                                grid_min=p["grid_min"], seed=p["seed"]))
            df = pd.DataFrame(records)
            stem = (f"probe__{label}__{qtype}__grid{p['grid_min']}"
                    f"__seed{p['seed']}")
            try:
                df.to_parquet(report_dir / f"{stem}.parquet")
            except (ImportError, ValueError):
                df.to_csv(report_dir / f"{stem}.csv", index=False)

            acc = accuracy_surface(records, p["grid_min"])
            transitions = sorted({e["t_min"] % MIN_PER_DAY
                                  for e in world.events(moved_by="human")
                                  if e["t_min"] // MIN_PER_DAY in set(test_days)})
            plot_surface(acc, transitions, p["grid_min"],
                         f"A(t_seen, t_query) — {label} — {qtype} "
                         f"(days {test_days})",
                         report_dir / f"{stem}.png")
            sym = delta_t_symmetry(records)
            moved = df[df["moved_between"] == 1]
            stable = df[df["moved_between"] == 0]
            summary_rows.append({
                "tier": label, "qtype": qtype,
                "mean_acc": float(df["correct"].mean()),
                "acc_moved_between": float(moved["correct"].mean()) if len(moved) else None,
                "acc_stable": float(stable["correct"].mean()) if len(stable) else None,
                "frac_moved": float(len(moved)) / max(1, len(df)),
                "mean_p_true": float(df["p_true"].mean()),
                "n": len(df), "delta_t_R2": round(sym, 4),
            })
            print(f"{stem}: acc={df['correct'].mean():.3f} dtR2={sym:.3f}")

    # ---- gate report ---------------------------------------------------------
    table = ["| tier | qtype | mean_acc | acc(moved) | acc(stable) | mean_p_true | delta_t_R2 |",
             "|---|---|---|---|---|---|---|"]
    for r in summary_rows:
        table.append(f"| {r['tier']} | {r['qtype']} | {r['mean_acc']:.4f} "
                     f"| {r['acc_moved_between']:.4f} | {r['acc_stable']:.4f} "
                     f"| {r['mean_p_true']:.4f} | {r['delta_t_R2']} |")
    lines = ["# Stage 1 gate report", "",
             f"question validation: n={val['n']} "
             f"index_counts={val['index_counts']} "
             f"max_skew={val['max_index_skew']:.3f}", "",
             *table, "",
             "## Δt-symmetry check",
             "delta_t_R2 near 1.0 would mean the surface collapses to Δt "
             "(no time-of-day structure) — values well below 1 confirm the "
             "pair (t_seen, t_query) carries information Δt alone does not."]
    (report_dir / "stage1_gate.md").write_text("\n".join(lines) + "\n")
    print(f"\nreport -> {report_dir / 'stage1_gate.md'}")


if __name__ == "__main__":
    main()
