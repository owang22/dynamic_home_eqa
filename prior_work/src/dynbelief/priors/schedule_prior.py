"""Stage 1.4 — offline schedule prior: the third f(t) source for
b3_perpetua_star, ablatable against `fremen` and `constant`.

Runs OFFLINE, once. The raw profile (per-class piecewise-constant relative
change rates over 24 hourly time-of-day bins) is produced by a single
cached LLM call — see the episode's schedule_prior_raw.json; when no LLM
endpoint is wired, a hand-written or uniform profile in the same JSON
schema is accepted so the interface is exercised either way:

  {"version": 1, "bins_per_day": 24, "source": "llm:..."|"uniform"|"hand",
   "classes": {"bowl": [r0..r23], ...}}

Calibration (mandatory): the raw profile is a PRIOR, never consumed as a
belief — a temperature map fitted on realized change events corrects it
toward observed change frequencies. With hourly class counts c_b from the
TRAINING days and prior shape r_b, we fit T in [0, 2] maximizing the
multinomial log-likelihood of counts under p_b ∝ r_b^T:
  T = 0 recovers uniform (prior ignored), T = 1 trusts the shape as-is,
  T > 1 sharpens it. Classes with no observed events keep T fitted on the
  pooled counts. The calibrated per-class profile is normalized to mean 1
  (a hazard MODULATOR, like fremen — absolute rate scale stays with the
  data-fitted per-edge MLEs) and cached alongside the raw file.

No model call ever happens per prediction; predict-time cost is a table
lookup inside SwitchingPrior.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.beliefs.base import object_class
from dynbelief.beliefs.fremen import SwitchingPrior


def _uniform_raw(classes: list[str]) -> dict:
    return {"version": 1, "bins_per_day": 24, "source": "uniform",
            "classes": {c: [1.0] * 24 for c in classes}}


def _fit_temperature(prior_shape: np.ndarray, counts: np.ndarray) -> float:
    """Grid-search T in [0,2] maximizing multinomial log-likelihood of the
    observed hourly counts under p ∝ shape^T."""
    shape = np.maximum(prior_shape, 1e-6)
    best_T, best_ll = 0.0, -np.inf
    for T in np.linspace(0.0, 2.0, 41):
        p = shape ** T
        p = p / p.sum()
        ll = float((counts * np.log(p)).sum())
        if ll > best_ll:
            best_T, best_ll = T, ll
    return best_T


def load_schedule_prior(episode_dir: str | pathlib.Path, world,
                        train_days: list[int]) -> dict[str, SwitchingPrior]:
    """{class: SwitchingPrior} — calibrated on the training days' realized
    change events, cached to schedule_prior_calibrated.json."""
    d = pathlib.Path(episode_dir)
    raw_path = d / "schedule_prior_raw.json"
    classes = sorted({object_class(l) for l in world.obj_label.values()})
    raw = (json.loads(raw_path.read_text()) if raw_path.exists()
           else _uniform_raw(classes))
    bins = raw["bins_per_day"]
    bin_min = MIN_PER_DAY // bins

    # observed hourly change counts per class, training days only
    counts: dict[str, np.ndarray] = {c: np.zeros(bins) for c in classes}
    pooled = np.zeros(bins)
    train = set(train_days)
    for e in world.events(moved_by="human"):
        if e["t_min"] // MIN_PER_DAY not in train:
            continue
        cls = object_class(world.obj_label[e["object_id"]])
        b = (e["t_min"] % MIN_PER_DAY) // bin_min
        counts.setdefault(cls, np.zeros(bins))[b] += 1
        pooled[b] += 1

    pooled_shape = np.array(raw["classes"].get(next(iter(raw["classes"])), [1.0] * bins))
    T_pooled = _fit_temperature(
        np.mean([np.array(v) for v in raw["classes"].values()], axis=0), pooled)

    calibrated = {"version": 1, "bins_per_day": bins, "source": raw["source"],
                  "temperature_pooled": T_pooled, "classes": {}, "temperatures": {}}
    priors: dict[str, SwitchingPrior] = {}
    for cls in classes:
        shape = np.array(raw["classes"].get(cls, [1.0] * bins), dtype=float)
        c = counts.get(cls, np.zeros(bins))
        T = _fit_temperature(shape, c) if c.sum() >= 5 else T_pooled
        prof = np.maximum(shape, 1e-6) ** T
        per_min = np.repeat(prof, bin_min)
        priors[cls] = SwitchingPrior(per_min)
        calibrated["classes"][cls] = [round(float(x), 5) for x in priors[cls].per_min[::bin_min]]
        calibrated["temperatures"][cls] = round(float(T), 3)
    (d / "schedule_prior_calibrated.json").write_text(json.dumps(calibrated, indent=1))
    return priors


class PerClassPrior:
    """Adapter giving B3PerpetuaStar a per-class f(t): callable+cumulative
    dispatching on the object's class (b3 threads the object id through
    predict; see perpetua.py)."""

    def __init__(self, priors: dict[str, SwitchingPrior], default: SwitchingPrior) -> None:
        self.priors = priors
        self.default = default

    def for_class(self, cls: str) -> SwitchingPrior:
        return self.priors.get(cls, self.default)
