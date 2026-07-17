"""Stage 0.6 — map-maintenance metrics over a runner dataframe.

map-maintenance error = fraction of (t, obj) grid cells where pred_argmax !=
true_parent — reported overall and restricted to MOVED objects (objects with
at least one human-moved event inside the evaluated window; the interesting
population, since never-moved objects are free accuracy). Plus log-loss,
Brier, and a 10-bin calibration curve on the probability assigned to the
true parent.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd


def compute_metrics(df: pd.DataFrame, world, t0: int, t1: int) -> dict:
    moved_objs = {e["object_id"] for e in world.events(moved_by="human")
                  if t0 <= e["t_min"] < t1}
    err = (df["pred_argmax"] != df["true_parent"]).astype(float)

    dists = df["pred_dist"].map(json.loads)
    p_true = np.array([d[t] if t < len(d) else 0.0
                       for d, t in zip(dists, df["true_parent"])])
    p_true_c = np.clip(p_true, 1e-12, 1.0)

    onehot_sq = []
    for d, t in zip(dists, df["true_parent"]):
        v = np.asarray(d)
        y = np.zeros_like(v)
        if t < len(y):
            y[t] = 1.0
        onehot_sq.append(float(((v - y) ** 2).sum()))

    moved_mask = df["obj_id"].isin(moved_objs)
    bins = np.linspace(0, 1, 11)
    which = np.clip(np.digitize(p_true, bins) - 1, 0, 9)
    correct = (df["pred_argmax"] == df["true_parent"]).to_numpy().astype(float)
    calib = []
    for b in range(10):
        m = which == b
        calib.append({
            "bin_lo": float(bins[b]), "bin_hi": float(bins[b + 1]),
            "n": int(m.sum()),
            "mean_conf": float(p_true[m].mean()) if m.any() else None,
            "frac_correct": float(correct[m].mean()) if m.any() else None,
        })

    placed = (df["true_parent"] != 0).to_numpy()
    return {
        "n_cells": int(len(df)),
        "n_moved_objects": len(moved_objs),
        "map_error_overall": float(err.mean()),
        "map_error_moved": float(err[moved_mask].mean()) if moved_mask.any() else None,
        # elsewhere/placed split: ~a third of truth-time in these episodes is
        # spent at ELSEWHERE (put-aways, not-yet-spawned items) and
        # perception is positive-only — the two populations measure very
        # different capabilities (staleness tracking vs. absence inference),
        # so the aggregate alone is misleading.
        "map_error_placed": float(err[placed].mean()) if placed.any() else None,
        "map_error_elsewhere": float(err[~placed].mean()) if (~placed).any() else None,
        "frac_truth_elsewhere": float((~placed).mean()),
        "log_loss": float(-np.log(p_true_c).mean()),
        "brier": float(np.mean(onehot_sq)),
        "calibration": calib,
    }
