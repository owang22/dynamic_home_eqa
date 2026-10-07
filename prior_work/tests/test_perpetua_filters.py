"""Numerics of the Perpetua port: closed-form single-component checks,
regression against outputs captured from montrealrobotics/perpetua-code
(JAX, float32; ``tests/fixtures/perpetua_reference_targets.json``), an
underflow check over a 30-day gap, EM recovery on synthetic
two-component data, and segment extraction. Times are plain floats."""

from __future__ import annotations

import json
import math
import pathlib

import numpy as np
import pytest

from baselines.beliefs import perpetua_filters as pfl

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "perpetua_reference_targets.json"
F32 = dict(rtol=2e-5, atol=1e-6)     # the reference computes in float32


@pytest.fixture(scope="module")
def targets() -> dict:
    return json.loads(FIXTURE.read_text())


def _mixture(family: str, params: dict, pi: list) -> pfl.SurvivalMixture:
    return pfl.SurvivalMixture(family, params, pi)


# ------------------------------------------------------- closed forms

def test_single_exponential_prior_is_the_survival_function() -> None:
    lam = 1.0 / 400.0
    state = pfl.FilterState.create(pfl.SurvivalMixture.exponential([lam], [1.0]), 0.0)
    for t in (0.0, 100.0, 1000.0):
        expected = min(math.exp(-lam * t), pfl.P_CEIL)
        assert pfl.persistence_predict(state, t)[0] == pytest.approx(expected, rel=1e-12)


def test_single_observation_posterior_matches_bayes_rule() -> None:
    # One y=1 at t1: p(X_t=1 | y) = (1-PM) S(t) / [(1-PM) S(t1) + PF (1-S(t1))]
    lam, pm, pf, t1, t = 1.0 / 400.0, 0.1, 0.2, 50.0, 120.0
    state = pfl.FilterState.create(pfl.SurvivalMixture.exponential([lam], [1.0]), 0.0)
    state = pfl.persistence_update(state, True, t1, pm, pf)
    s1, s = math.exp(-lam * t1), math.exp(-lam * t)
    expected = (1 - pm) * s / ((1 - pm) * s1 + pf * (1 - s1))
    assert pfl.persistence_predict(state, t)[0] == pytest.approx(expected, rel=1e-6)


def test_emergence_filter_is_the_mirror_image() -> None:
    lam, pm, pf = 1.0 / 300.0, 0.1, 0.1
    prior = pfl.SurvivalMixture.exponential([lam], [1.0])
    p_state = pfl.FilterState.create(prior, 0.0)
    e_state = pfl.FilterState.create(prior, 0.0)
    for t, y in [(10.0, True), (40.0, False), (90.0, False)]:
        p_state = pfl.persistence_update(p_state, y, t, pm, pf)
        e_state = pfl.emergence_update(e_state, not y, t, pm, pf)
    p_pred = pfl.persistence_predict(p_state, 150.0)[0]
    e_pred = pfl.emergence_predict(e_state, 150.0)[0]
    assert e_pred == pytest.approx(1.0 - p_pred, abs=1e-9)


def test_uninitialised_emergence_filter_is_inert() -> None:
    state = pfl.FilterState.create(pfl.SurvivalMixture.exponential([0.01], [1.0]), math.inf)
    updated = pfl.emergence_update(state, True, 5.0, 0.1, 0.1)
    assert updated is state
    assert pfl.emergence_predict(state, 5.0)[0] == 0.0


def test_lognormal_log_survival_matches_normal_sf() -> None:
    mix = pfl.SurvivalMixture.lognormal([math.log(500.0)], [0.3], [1.0])
    t = 700.0
    z = (math.log(t) - math.log(500.0)) / 0.3
    expected = math.log(0.5 * math.erfc(z / math.sqrt(2)))
    assert mix.log_survival(t)[0] == pytest.approx(expected, rel=1e-12)
    assert mix.log_survival(0.0)[0] == pfl.LOG_CEIL


# ------------------------------------------------------- regression

def test_regression_single_persistence(targets: dict) -> None:
    A = targets["A_single_persistence_exp"]
    state = pfl.FilterState.create(pfl.SurvivalMixture.exponential([A["lambda"]], [1.0]), 0.0)
    for tr in A["trace"]:
        state = pfl.persistence_update(state, bool(tr["y"]), tr["t"], A["PM"], A["PF"])
        assert state.log_likelihood == pytest.approx(tr["log_likelihood"], rel=2e-5, abs=1e-6)
        np.testing.assert_allclose(state.log_lower, tr["log_lower_evidence_sum"], **F32)
        np.testing.assert_allclose(state.log_cond_evidence,
                                   tr["log_conditional_evidence"], **F32)
        np.testing.assert_allclose(pfl.persistence_predict(state, tr["t"] + 50.0),
                                   np.array(tr["posterior_at_t_plus_50"]).ravel(), **F32)
    np.testing.assert_allclose(
        pfl.persistence_predict(state, np.array(A["final_predict_times"])).ravel(),
        np.array(A["final_predict"]).ravel(), **F32)


@pytest.mark.parametrize("key,kind", [
    ("B_mixture_persistence_exp", "persistence"),
    ("B_mixture_persistence_lognorm", "persistence"),
    ("C_mixture_emergence_exp", "emergence"),
    ("C_mixture_emergence_lognorm", "emergence")])
def test_regression_mixtures(targets: dict, key: str, kind: str) -> None:
    B = targets[key]
    family = "exponential" if key.endswith("exp") else "lognormal"
    state = pfl.FilterState.create(_mixture(family, B["params"], B["pi"]), 0.0)
    update = pfl.persistence_update if kind == "persistence" else pfl.emergence_update
    for tr in B["trace"]:
        state = update(state, bool(tr["y"]), tr["t"], B["PM"], B["PF"])
        np.testing.assert_allclose(state.log_tau, tr["log_tau"], rtol=1e-4, atol=1e-5)
        mode, comps = pfl.mixture_predict(state, tr["t"] + 50.0, kind)
        np.testing.assert_allclose(comps, np.array(tr["components_at_t_plus_50"]).ravel(),
                                   rtol=2e-5, atol=1e-7)
        assert mode == pytest.approx(np.array(tr["mode_at_t_plus_50"]).ravel()[0],
                                     rel=2e-5, abs=1e-7)
    mode, comps = pfl.mixture_predict(state, np.array(B["final_predict_times"]), kind)
    # float32 error in a sharp (std 0.025) lognormal transition reaches 1e-4
    np.testing.assert_allclose(comps.T, np.array(B["final_components"]), rtol=5e-4, atol=1e-7)


def _run_perpetua_like_reference(D: dict, family: str):
    """``filter_test_utils.run_perpetua``: predict every query time from
    the state holding the observations strictly before it."""
    pp = _mixture(family, D["params_persistence"], D["pi_persistence"])
    pe = _mixture(family, D["params_emergence"], D["pi_emergence"])
    state = pfl.PerpetuaState.create(pp, pe, 0.0, D["delta_low"], D["delta_high"],
                                     D["num_steps"], D["eps"])
    obs_t, obs_y = np.array(D["obs_t"]), np.array(D["obs_y"], dtype=bool)
    qt = np.array(D["query_times"])
    belief = np.full(qt.size, np.nan)
    states = np.full((qt.size, len(D["weights"][0])), -1)

    def predict(mask: np.ndarray) -> None:
        if mask.any():
            b, s, w = state.simulate(qt[mask])
            belief[mask] = b[int(np.argmax(w))]
            states[mask] = s.T

    predict(qt < obs_t[0])
    state.update(bool(obs_y[0]), float(obs_t[0]), D["PM"], D["PF"])
    for i in range(len(obs_t) - 1):
        predict((qt >= obs_t[i]) & (qt < obs_t[i + 1]))
        state.update(bool(obs_y[i + 1]), float(obs_t[i + 1]), D["PM"], D["PF"])
    predict(qt >= obs_t[-1])
    return belief, states


@pytest.mark.parametrize("key", ["D_perpetua_exp_steps1", "D_perpetua_exp_steps10",
                                 "D_perpetua_lognorm_steps1", "D_perpetua_lognorm_steps10"])
def test_regression_perpetua_state_machine(targets: dict, key: str) -> None:
    D = targets[key]
    family = "exponential" if "_exp_" in key else "lognormal"
    belief, states = _run_perpetua_like_reference(D, family)
    np.testing.assert_array_equal(states, np.array(D["states"]))
    np.testing.assert_allclose(belief, np.array(D["belief"]), rtol=2e-5, atol=1e-5)


def _reference_segments(E: dict):
    return [pfl.Segment(E["grid"], y) for y in E["seqs_y"]]


def test_regression_em_exponential(targets: dict) -> None:
    E = targets["E_em_exponential_persistence"]
    batch = pfl._Batch(_reference_segments(E), "persistence", E["PM"], E["PF"])
    prior = pfl.SurvivalMixture.exponential(E["lambda_init"], E["pi_init"])
    for it in E["iters"]:
        prior, _ = pfl.em_step(batch, prior)
        ev = float(pfl.logsumexp(batch.log_joint(prior), axis=1).sum())
        # the slow component's rate drifts in float32 over 30 iterations
        np.testing.assert_allclose(prior.params["lambda_"], it["lambda"], rtol=5e-3)
        np.testing.assert_allclose(prior.weights, it["pi"], rtol=2e-4)
        assert ev == pytest.approx(it["log_evidence"], abs=1e-3)


def test_regression_em_lognormal(targets: dict) -> None:
    E = targets["E_em_exponential_persistence"]
    L = targets["E_em_lognormal_persistence"]
    batch = pfl._Batch(_reference_segments(E), "persistence", E["PM"], E["PF"])
    prior = pfl.SurvivalMixture.lognormal(L["mu_init"], L["sigma_init"], L["pi_init"])
    for it in L["iters"]:
        prior, _ = pfl.em_step(batch, prior)
        ev = float(pfl.logsumexp(batch.log_joint(prior), axis=1).sum())
        np.testing.assert_allclose(prior.params["logmu"], it["logmu"], rtol=2e-4)
        np.testing.assert_allclose(prior.params["std"], it["std"], rtol=5e-3)
        np.testing.assert_allclose(prior.weights, it["pi"], rtol=1e-4)
        assert ev == pytest.approx(it["log_evidence"], abs=1e-3)


def test_regression_em_exponential_emergence(targets: dict) -> None:
    E = targets["E_em_exponential_persistence"]
    M = targets["E_em_exponential_emergence"]
    segs = [pfl.Segment(E["grid"], [not v for v in y]) for y in E["seqs_y"]]
    batch = pfl._Batch(segs, "emergence", E["PM"], E["PF"])
    prior = pfl.SurvivalMixture.exponential(M["lambda_init"], M["pi_init"])
    for it in M["iters"]:
        prior, _ = pfl.em_step(batch, prior)
        np.testing.assert_allclose(prior.params["lambda_"], it["lambda"], rtol=5e-3)
        np.testing.assert_allclose(prior.weights, it["pi"], rtol=2e-4)


# ------------------------------------------------------ robustness

def test_thirty_day_gap_does_not_underflow() -> None:
    # Hour-scale survival, then a query 30 days later: every quantity
    # must stay finite and the belief a valid probability.
    day = 86_400.0
    prior = pfl.SurvivalMixture.lognormal([math.log(4 * 3600.0), math.log(12 * 3600.0)],
                                          [0.5, 0.5], [0.6, 0.4])
    state = pfl.FilterState.create(prior, 0.0)
    for k in range(20):
        state = pfl.persistence_update(state, True, 600.0 * k, 0.01, 0.01)
    assert np.isfinite(state.log_cond_evidence).all()
    assert np.isfinite(state.log_tau).all()
    p = pfl.persistence_predict(state, 30 * day)
    assert np.isfinite(p).all() and (p >= pfl.P_FLOOR).all() and (p <= pfl.P_CEIL).all()
    machine = pfl.PerpetuaState.create(prior, prior, 0.0, num_steps=10)
    for k in range(20):
        machine.update(True, 600.0 * k, 0.01, 0.01)
    belief = machine.predict([30 * day, 31 * day])
    assert np.isfinite(belief).all() and (belief >= 0).all() and (belief <= 1).all()
    star = pfl.PerpetuaStarState.create(prior, prior, 0.0)
    for k in range(20):
        star.update(True, 600.0 * k, 0.01, 0.01, 0.5)
    b, parts = star.predict(30 * day, 0.5)
    assert 0.0 <= b <= 1.0 and all(math.isfinite(v) for v in parts.values())


def test_perpetua_state_machine_switches_and_resets() -> None:
    prior_p = pfl.SurvivalMixture.exponential([1 / 400.0, 1 / 700.0], [0.7, 0.3])
    prior_e = pfl.SurvivalMixture.exponential([1 / 400.0, 1 / 800.0], [0.6, 0.4])
    m = pfl.PerpetuaState.create(prior_p, prior_e, 0.0, num_steps=10)
    events = []
    for t in np.arange(0.0, 3000.0, 25.0):
        events += m.update(bool((t % 800) < 400), float(t), 0.01, 0.01)
    directions = [d for _, d in events]
    assert "to_emergence" in directions and "to_persistence" in directions
    assert math.isfinite(m.ef.t0)          # the emergence mixture got initialised
    assert m.switch_counter > 1


def test_perpetua_predict_does_not_mutate_state() -> None:
    prior = pfl.SurvivalMixture.exponential([1 / 400.0], [1.0])
    m = pfl.PerpetuaState.create(prior, prior, 0.0, num_steps=5)
    for t in (10.0, 20.0, 30.0):
        m.update(True, t, 0.05, 0.05)
    before = (m.current_state, m.pf.log_likelihood, m.ef.t0, m.last_t)
    m.predict([2000.0, 4000.0])
    assert (m.current_state, m.pf.log_likelihood, m.ef.t0, m.last_t) == before


# ------------------------------------------------------------- Perpetua*

def test_perpetua_star_model_posterior_follows_the_prior_when_annealed() -> None:
    prior = pfl.SurvivalMixture.exponential([1 / 3600.0], [1.0])
    star = pfl.PerpetuaStarState.create(prior, prior, 0.0, alpha0=1.0)
    for t in (10.0, 20.0):
        star.update(True, t, 0.05, 0.05, 0.5)
    # alpha(t) ~ 0 far from the last observation: posterior = prior
    log_p, log_e = star.log_model_posterior(1e6, 0.8)
    assert math.exp(log_e) == pytest.approx(0.8, abs=1e-6)
    assert math.exp(log_p) == pytest.approx(0.2, abs=1e-6)
    # at the last observation alpha = 1: the likelihood matters
    log_p, log_e = star.log_model_posterior(20.0, 0.5)
    assert math.exp(log_p) + math.exp(log_e) == pytest.approx(1.0)


def test_perpetua_star_reset_modes() -> None:
    prior = pfl.SurvivalMixture.exponential([1 / 300.0], [1.0])
    stream = [(t, (t % 800) < 400) for t in np.arange(0.0, 2400.0, 25.0)]
    star = pfl.PerpetuaStarState.create(prior, prior, 0.0, alpha0=0.0)
    events = []
    for t, y in stream:
        events += star.update(bool(y), float(t), 0.01, 0.01, 0.5)
    # the belief rule flips exactly at the observed transitions: at the
    # first absence (t=400) into emergence, at the first presence (800)
    # back, and so on; both mixtures restart together
    assert [(t, d) for t, d in events][:4] == [
        (400.0, "to_emergence"), (800.0, "to_persistence"),
        (1200.0, "to_emergence"), (1600.0, "to_persistence")]
    assert star.pf.t0 == star.ef.t0 == events[-1][0]
    posterior = pfl.PerpetuaStarState.create(prior, prior, 0.0, alpha0=0.0,
                                             reset_mode="model_posterior")
    ev2 = []
    for t, y in stream:
        ev2 += posterior.update(bool(y), float(t), 0.01, 0.01, 0.5)
    assert ev2 and {d for _, d in ev2} <= {"to_emergence", "to_persistence"}
    literal = pfl.PerpetuaStarState.create(prior, prior, 0.0, alpha0=0.0,
                                           reset_mode="none")
    for t, y in stream:
        assert literal.update(bool(y), float(t), 0.01, 0.01, 0.5) == []
    assert literal.pf.t0 == 0.0 and literal.ef.t0 == 0.0
    with pytest.raises(ValueError):
        pfl.PerpetuaStarState.create(prior, prior, 0.0, reset_mode="bogus")


def test_forgetting_factor_scales_the_log_likelihood() -> None:
    prior = pfl.SurvivalMixture.exponential([1 / 300.0], [1.0])
    s0 = pfl.FilterState.create(prior, 0.0)
    s1 = pfl.persistence_update(s0, True, 10.0, 0.1, 0.1, forgetting=0.5)
    s2 = pfl.persistence_update(s1, True, 20.0, 0.1, 0.1, forgetting=0.5)
    assert s2.log_likelihood == pytest.approx(0.5 * s1.log_likelihood + math.log(0.9))


# ---------------------------------------------------------------- EM

def test_em_recovers_two_exponential_components() -> None:
    # Deterministic two-mode data: survival 300 s (2/3 of segments) and
    # 3000 s, noise-free observations every 20 s over 6000 s.
    # Two modes far enough apart that a single exponential cannot fit
    # both: survival ~100 s (8 segments) and ~5000 s (6 segments),
    # noise-free observations every 20 s over 12 000 s.
    grid = np.arange(0.0, 12000.0, 20.0)
    cuts = [95, 110, 100, 4900, 105, 90, 5100, 98, 102, 5000, 4950, 5050, 107, 93]
    segs = [pfl.Segment(grid, grid <= cut) for cut in cuts]
    fit = pfl.select_mixture(segs, "persistence", "exponential", 0.05, 0.05,
                             k_range=(1, 2, 3))
    assert fit.mixture.n_components >= 2
    means = np.sort(1.0 / fit.mixture.params["lambda_"])
    assert abs(means[0] - 100) < 30          # the fast mode
    assert abs(means[-1] - 5000) < 1000      # the slow mode
    assert fit.mixture.weights.sum() == pytest.approx(1.0)


def test_em_recovers_two_lognormal_components() -> None:
    grid = np.arange(0.0, 6000.0, 20.0)
    segs = [pfl.Segment(grid, grid <= cut)
            for cut in [290, 310, 300, 2900, 320, 280, 3100, 305, 295, 3000, 315, 285]]
    fit = pfl.select_mixture(segs, "persistence", "lognormal", 0.05, 0.05,
                             k_range=(2,), max_iter=100)
    medians = np.sort(np.exp(fit.mixture.params["logmu"]))
    assert abs(medians[0] - 300) < 60 and abs(medians[-1] - 3000) < 600


def test_fit_is_deterministic() -> None:
    grid = np.arange(0.0, 3000.0, 30.0)
    segs = [pfl.Segment(grid, grid <= c) for c in (400, 1200, 450, 1300)]
    a = pfl.select_mixture(segs, "persistence", "exponential", 0.1, 0.1)
    b = pfl.select_mixture(segs, "persistence", "exponential", 0.1, 0.1)
    np.testing.assert_array_equal(a.mixture.params["lambda_"], b.mixture.params["lambda_"])
    assert a.log_evidence == b.log_evidence


# -------------------------------------------------------- segments

def test_extract_segments_cuts_at_flips_with_observation_time_origin() -> None:
    times = [0, 10, 20, 30, 40, 50, 60, 70]
    y = [1, 1, 0, 0, 1, 1, 1, 0]
    pers, emer = pfl.extract_segments(times, y)
    # blocks: [1,1] [0,0] [1,1,1] [0]; heads: the first three blocks
    assert len(pers) == 2 and len(emer) == 1
    np.testing.assert_array_equal(pers[0].times, [0, 10, 20, 30])
    np.testing.assert_array_equal(pers[0].y, [1, 1, 0, 0])
    np.testing.assert_array_equal(emer[0].times, [0, 10, 20, 30, 40])     # from t=20
    np.testing.assert_array_equal(emer[0].y, [0, 0, 1, 1, 1])
    np.testing.assert_array_equal(pers[1].times, [0, 10, 20, 30])         # from t=40
    np.testing.assert_array_equal(pers[1].y, [1, 1, 1, 0])


def test_extract_segments_needs_a_completed_head() -> None:
    assert pfl.extract_segments([0, 10, 20], [1, 1, 1]) == ([], [])
    pers, emer = pfl.extract_segments([0, 10], [1, 0])
    assert len(pers) == 1 and emer == []
    assert pfl.extract_segments([], []) == ([], [])
