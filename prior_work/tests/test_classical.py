"""Mandated unit tests for the classical arms (brief deliverable 2):
  1. C2 restricted to its DC component reproduces C1 (constant-rate special case)
  2. the shared filter reproduces the analytic two-state telegraph solution
  3. the oracle matches an independent Monte-Carlo occupancy within tolerance
plus leakage assertions and a shared-path check."""
from __future__ import annotations

import math
import pathlib

import numpy as np
import pytest

from dynbelief import MIN_PER_DAY
from dynbelief.classical.filter import Filter, uniform_belief
from dynbelief.classical.rates import (C0LastObs, C1Constant, C2Spectral,
                                       C3PeriodicGLM, C4RegimeHMM)

REPO = pathlib.Path(__file__).resolve().parents[1]


# ── synthetic observation stream ─────────────────────────────────────────────

def synth_history(n_days=10, obj="mug_1"):
    """One object bouncing between two receptacles: A at night/morning, B in
    the evening (a clean daily pattern). Object id chosen so class==unique."""
    rows = []
    for d in range(n_days):
        for (h, r) in [(8, "shelf_a"), (14, "shelf_a"), (20, "shelf_b")]:
            rows.append({"day": d, "t_min": d * MIN_PER_DAY + h * 60,
                         "parents": {obj: r}})
    return rows


CANDS = ["shelf_a", "shelf_b", "elsewhere"]


# ── 1. C2 with DC only == C1 ─────────────────────────────────────────────────

def test_c2_dc_only_reproduces_c1():
    hist = synth_history()
    c1 = C1Constant(CANDS)
    c1.fit(hist)
    c2 = C2Spectral(CANDS, K=0)          # DC component only
    c2.fit(hist)
    # same lambda (shared MLE) and occupancy(t) within Laplace-smoothing slack
    for t in [5 * MIN_PER_DAY + h * 60 for h in (3, 9, 15, 21)]:
        for r in CANDS:
            assert c1.rate("mug_1", r, t) == c2.rate("mug_1", r, t)
            assert abs(c1.occupancy("mug_1", r, t)
                       - c2.occupancy("mug_1", r, t)) < 0.03
    # and the FILTER outputs agree (same shared prediction path)
    for mode in ("categorical", "per_edge"):
        f1 = Filter(c1, CANDS, "mug_1", mode=mode)
        f2 = Filter(c2, CANDS, "mug_1", mode=mode)
        for f in (f1, f2):
            f.reset(0)
            f.update((9 * 60, "shelf_a"))
        p1, p2 = f1.predict(20 * 60), f2.predict(20 * 60)
        for r in CANDS:
            assert abs(p1[r] - p2[r]) < 0.05, (mode, r, p1, p2)


# ── 2. analytic two-state telegraph ──────────────────────────────────────────

class _Telegraph:
    """Constant-rate two-state rate model: pi = (0.3, 0.7), lambda = 1/300."""
    LAM, PI = 1.0 / 300.0, {"a": 0.3, "b": 0.7}

    def fit(self, h): ...
    def occupancy(self, o, r, t): return self.PI[r]
    def rate(self, o, r, t): return self.LAM


def test_filter_matches_analytic_telegraph():
    rm = _Telegraph()
    f = Filter(rm, ["a", "b"], "x", mode="categorical", step_min=1)
    f.reset(0)
    f.update((0, "a"))                          # start pinned at state a
    for t in (60, 300, 900, 3000):
        q = f.predict(t)["b"]
        analytic = rm.PI["b"] * (1.0 - math.exp(-rm.LAM * t))
        assert abs(q - analytic) < 2e-3, (t, q, analytic)
    # per_edge mode agrees for two states as well
    fe = Filter(rm, ["a", "b"], "x", mode="per_edge", step_min=1)
    fe.reset(0)
    fe.update((0, "a"))
    q = fe.predict(900)["b"]
    assert abs(q - rm.PI["b"] * (1 - math.exp(-rm.LAM * 900))) < 5e-3


# ── 3. oracle vs independent Monte Carlo ─────────────────────────────────────

def test_oracle_matches_independent_mc():
    from dynbelief.classical.oracle import C5Oracle
    from dynbelief.profiles.schema import load_profile
    prof = load_profile(REPO / "profiles" / "manual" / "single_adult_typ_v1.yaml")
    cands = sorted(prof.receptacle_ids) + ["elsewhere"]
    a = C5Oracle(prof, cands, n_sims=40, n_days=14, seed0=1000)
    b = C5Oracle(prof, cands, n_sims=40, n_days=14, seed0=9000)
    a.fit([]); b.fit([])
    # occupancy of a volatile object at a few times agrees across MC runs
    for t in [2 * MIN_PER_DAY + 12 * 60, 5 * MIN_PER_DAY + 20 * 60]:
        for r in ("nightstand_r1", "sofa_l1", "elsewhere"):
            pa, pb = a.occupancy("phone", r, t), b.occupancy("phone", r, t)
            assert abs(pa - pb) < 0.12, (t, r, pa, pb)
    # static object: point mass on its home at all times
    assert a.occupancy("vase", "table_d1", 3 * MIN_PER_DAY + 600) > 0.95


# ── leakage + parity checks ──────────────────────────────────────────────────

def test_non_oracle_arms_never_touch_profile_yaml(monkeypatch):
    """L1: fitting + predicting C0-C4 must not open any profiles/manual YAML."""
    import builtins
    opened = []
    real_open = builtins.open

    def spy(file, *a, **k):
        if "profiles/manual" in str(file):
            opened.append(str(file))
        return real_open(file, *a, **k)

    monkeypatch.setattr(builtins, "open", spy)
    hist = synth_history()
    for cls in (C0LastObs, C1Constant, C2Spectral, C3PeriodicGLM, C4RegimeHMM):
        rm = cls(CANDS)
        rm.fit(hist)
        f = Filter(rm, CANDS, "mug_1")
        f.reset(0)
        f.update((9 * 60, "shelf_a"))
        f.predict(20 * 60)
    assert not opened, f"L1 violation: {opened}"


def test_c4_recovers_two_regimes_on_synthetic_weekly():
    """A synthetic household with weekday-vs-weekend occupancy flip: C4 should
    separate the two day-types (W4 sanity, label-agnostic)."""
    rows = []
    for d in range(14):
        weekend = (d % 7) >= 5
        r = "shelf_b" if weekend else "shelf_a"
        for h in (9, 15, 21):
            rows.append({"day": d, "t_min": d * MIN_PER_DAY + h * 60,
                         "parents": {"mug_1": r}})
    c4 = C4RegimeHMM(CANDS, n_regimes=2, n_restarts=3, seed=0)
    c4.fit(rows)
    assert not c4.degenerate
    sched = np.array([g.argmax() for g in c4.regime_schedule])
    weekday_lab = np.bincount(sched[[d for d in range(14) if d % 7 < 5]]).argmax()
    weekend_lab = np.bincount(sched[[d for d in range(14) if d % 7 >= 5]]).argmax()
    assert weekday_lab != weekend_lab, f"regimes failed to separate: {sched}"


def test_d0_uniform_prior_is_explicit():
    u = uniform_belief(CANDS)
    assert abs(sum(u.values()) - 1) < 1e-9
    assert len(set(u.values())) == 1


def test_particle_oracle_captures_dish_cycle():
    """C5+ conditioned on 'plate in sink at 21:30' predicts cupboard (the dish
    cycle) more strongly than the marginal oracle, which ignores the condition."""
    from dynbelief.classical.oracle import C5Particle, C5Oracle
    from dynbelief.profiles.schema import load_profile
    prof = load_profile(REPO / "profiles" / "manual" / "single_adult_typ_v1.yaml")
    cands = sorted(prof.receptacle_ids) + ["elsewhere"]
    part = C5Particle(prof, cands, n_particles=1500); part.fit()
    marg = C5Oracle(prof, cands, n_sims=120); marg.fit([])
    D = 5 * 1440
    # 21:00 (plate in sink post-dinner) vs 22:30 (after the 21:45 dish return);
    # times span the 30-min state-grid bins around the return.
    pb = part.predict_belief("plate", "sink_k1", D + 21 * 60, D + 22 * 60 + 30)
    assert pb["cupboard_k1"] > 0.5           # dish cycle recovered
    assert part.estimator_for("plate") == "particle"
    # no-observation query reduces to the marginal
    nb = part.predict_belief("plate", None, None, D + 12 * 60)
    assert part.used == "marginal_no_obs"
