"""Stage 0.6 — schedule runner.

Steps a (t_min, vp_id) schedule; at each visit calls Perceiver.observe from
the viewpoint's pose and feeds the observations to the belief model. On a
fixed grid (default 10 min) calls predict() for all objects and logs one row
per (t, object):

    [t, obj_id, true_parent, pred_argmax, pred_dist, entropy, last_seen_age]

to parquet (pandas). pred_dist is stored as a JSON list so calibration can
be computed later without re-running.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

from dynbelief.perception.base import Pose


def run_schedule(world, viewpoints, perceiver, belief,
                 schedule: list[tuple[int, str]],
                 t0: int, t1: int, grid_min: int = 10,
                 log_from: int | None = None) -> pd.DataFrame:
    """Run [t0, t1). Prediction rows are logged from `log_from` (default t0)
    — set it to the evaluation-period start so training feeds don't dilute
    the metric."""
    log_from = t0 if log_from is None else log_from
    belief.reset(world.objects(), world.receptacles(), t0)
    sched = sorted((t, vp) for t, vp in schedule if t0 <= t < t1)
    si = 0
    rows = []
    for t in range(t0, t1, grid_min):
        while si < len(sched) and sched[si][0] <= t:
            ts, vp_id = sched[si]
            vp = viewpoints.get(vp_id)
            pose = Pose(vp["position"][0], vp["position"][2], vp["yaw"])
            belief.observe(ts, perceiver.observe(pose, ts))
            si += 1
        if t < log_from:
            continue
        truth = world.state_at(t)
        preds = belief.predict(t)
        ents = belief.entropy(t)
        for obj in world.objects():
            true_parent = truth.get(obj, (0, {}))[0]
            dist = preds[obj]
            seen = belief.last_seen.get(obj)
            rows.append({
                "t": t, "obj_id": obj, "true_parent": true_parent,
                "pred_argmax": int(np.argmax(dist)),
                "pred_dist": json.dumps(np.round(dist, 5).tolist()),
                "entropy": float(ents[obj]),
                "last_seen_age": (t - seen[0]) if seen else -1,
            })
    return pd.DataFrame(rows)


def save_run(df: pd.DataFrame, out_path: str | pathlib.Path) -> None:
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(out_path)
    except (ImportError, ValueError):
        # no parquet engine in the env — CSV fallback, same schema
        df.to_csv(out_path.with_suffix(".csv"), index=False)
