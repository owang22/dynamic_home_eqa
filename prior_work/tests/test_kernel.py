"""Transition-kernel arm unit tests (K1/K2/K3 deliverable 2):
  - kappa=0 equals pure counting (no prior influence)
  - a zero-count row returns exactly q
  - a row with kappa observed transitions returns the q/data midpoint
  - deterministic-cycle kernel recovery (D3): the learned kernel concentrates on
    the true destination for a class with a fixed cycle."""
from __future__ import annotations

import pathlib

import numpy as np
import pytest

from dynbelief import MIN_PER_DAY
from dynbelief.classical.kernel import KernelModel

REPO = pathlib.Path(__file__).resolve().parents[1]
CANDS = ["A", "B", "C", "elsewhere"]


def _obs(day, hour, obj, r):
    return {"day": day, "t_min": day * MIN_PER_DAY + hour * 60, "parents": {obj: r}}


def deterministic_cycle(n_days=20, bin_hours=4):
    """mug_1 is at A at the start of the evening bin and ALWAYS at B one bin
    later (a fixed cycle), every day."""
    rows = []
    for d in range(n_days):
        rows.append(_obs(d, 18, "mug_1", "A"))    # evening bin
        rows.append(_obs(d, 22, "mug_1", "B"))    # next bin (4h later)
    return rows


def test_kappa0_equals_pure_counting():
    hist = deterministic_cycle()
    k1 = KernelModel(CANDS, bin_hours=4)
    k1.fit(hist)
    q = {("mug", k1._daypart(18 * 60), 0, "A"): np.array([0.9, 0.1, 0.0, 0.0])}
    k2_k0 = KernelModel(CANDS, bin_hours=4, prior_q=q, kappa=0.0)
    k2_k0.fit(hist)
    # kappa=0 => the injected q has zero weight => identical to K1
    for src in CANDS:
        r1, _ = k1._row("mug", 18 * 60, src)
        r2, _ = k2_k0._row("mug", 18 * 60, src)
        assert np.allclose(r1, r2), src


def test_zero_count_row_returns_q():
    """A (class,daypart,source) with no observed transitions returns exactly q."""
    q = {("mug", 3, 0, "C"): np.array([0.2, 0.3, 0.5, 0.0])}   # daypart 3 = 12-16h
    k2 = KernelModel(CANDS, bin_hours=4, prior_q=q, kappa=10.0)
    k2.fit(deterministic_cycle())                 # no C-source transitions exist
    row, level = k2._row("mug", 13 * 60, "C")     # 13:00 -> daypart 3, source C
    assert np.allclose(row, [0.2, 0.3, 0.5, 0.0]), row
    assert level == "prior_injected"


def test_midpoint_at_kappa_equals_count():
    """kappa observed transitions => row is the midpoint of q and the data MLE."""
    q = {("mug", 4, 0, "A"): np.array([0.0, 0.0, 1.0, 0.0])}   # daypart 4 (16-20h)=C
    # weekday-only cycle so all A->B transitions land in ONE (weekday) bin
    hist = [r for r in deterministic_cycle(n_days=40) if (r["day"] % 7) < 5]
    k0 = KernelModel(CANDS, bin_hours=4); k0.fit(hist)
    count = k0._n0[("mug", k0._cyclic_bin(18 * 60), "A")].sum()
    k2 = KernelModel(CANDS, bin_hours=4, prior_q=q, kappa=count)   # kappa == observed
    k2.fit(hist)
    n0 = k2._n0[("mug", k2._cyclic_bin(18 * 60), "A")]
    row, _ = k2._row("mug", 18 * 60, "A")
    data_mle = n0 / n0.sum()                        # all mass on B
    midpoint = 0.5 * q[("mug", 4, 0, "A")] + 0.5 * data_mle
    assert np.allclose(row, midpoint, atol=1e-6), (row, midpoint)


def test_deterministic_cycle_recovery():
    """D3: the learned kernel row (mug at A, evening) concentrates on B."""
    k1 = KernelModel(CANDS, bin_hours=4)
    k1.fit(deterministic_cycle(n_days=28))
    row, level = k1._row("mug", 18 * 60, "A")
    assert row[CANDS.index("B")] > 0.8, row
    assert level in ("L0_bin", "L1_daypart")


def test_predict_belief_propagates_from_source():
    k1 = KernelModel(CANDS, bin_hours=4)
    k1.fit(deterministic_cycle(n_days=28))
    # observed at A at 18:00 on a fresh day -> predict at 22:00 -> B
    belief, lvl = k1.predict_belief("mug_9", "A", 30 * MIN_PER_DAY + 18 * 60,
                                    30 * MIN_PER_DAY + 22 * 60)
    assert max(belief, key=belief.get) == "B"
    # no observation -> uniform
    b2, lv2 = k1.predict_belief("mug_9", None, None, 30 * MIN_PER_DAY + 22 * 60)
    assert lv2 == "no_obs" and abs(b2["A"] - 0.25) < 1e-9


def test_dish_cycle_recovery_on_real_bank():
    """D3 on the real generator: learn the kernel from a long observation stream
    and confirm the plate's evening-bin kernel moves mass toward the cupboard."""
    import json
    from dynbelief.experiments.streams import load_gt
    by_obj, init, obs, targets, reg = load_gt(REPO / "banks" / "typ_v1" / "single_adult_typ_v1")
    recep = {int(v): k for k, v in reg["receptacles"].items()}
    cands = sorted(r for r in recep.values() if r != "elsewhere") + ["elsewhere"]
    k1 = KernelModel(cands, bin_hours=4)
    k1.fit([r for r in obs if r["day"] < 28])
    # plate observed in the sink in the evening -> next bin should favor cupboard
    row, level = k1._row("plate", 20 * 60, "sink_k1")
    assert row[cands.index("cupboard_k1")] >= row[cands.index("sink_k1")], \
        f"kernel did not move plate sink->cupboard: {dict(zip(cands, row.round(2)))}"
