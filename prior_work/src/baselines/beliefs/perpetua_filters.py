"""Perpetua numerics: survival mixtures, persistence and emergence filters,
the Perpetua state machine, the Perpetua* Bayesian model selection, and
EM parameter learning. Pure numpy/stdlib; no repo imports.

This is a port of montrealrobotics/perpetua-code (JAX) -- the files
``src/filters/PersistenceFilter.py``, ``EmergenceFilter.py``,
``Mixture{Persistence,Emergence}Filters.py``, ``SinglePerpetua.py``,
``Perpetua.py`` and ``src/learning/mixture_{exponential,lognormal}.py`` --
plus the Perpetua* equations 2-15 of arXiv 2605.00121, which has no public
code. The JAX code is the numerical ground truth for everything Perpetua:
``tests/test_perpetua_filters.py`` checks this module against outputs
captured from it (``tests/fixtures/perpetua_reference_targets.json``,
produced by ``third_party/perpetua_reference/ref_targets.py``). Its
numerical conventions are therefore mirrored on purpose, including the
ones that look odd:

* log-probabilities are clipped to ``[log 1e-10, log 0.999999]`` and
  probabilities to ``[1e-10, 0.999999]`` (``math_utils.clip_*``), so a
  survival function evaluated at 0 is 0.999999, not 1;
* ``logdiff(a, b)`` returns the floor when ``exp(b - a)`` is within
  ``isclose`` tolerance of 1, i.e. a zero-length interval carries mass
  1e-10 rather than 0;
* the reference runs in float32, so the regression tolerances are float32
  tolerances; this module computes in float64.

Time is a plain float everywhere here; the belief layer feeds seconds.

Notation follows the Perpetua paper (arXiv 2507.18808): a feature is
present (``X_t = 1``) until its survival time ``T`` elapses (persistence
model) or absent until its emergence time elapses (emergence model, the
mirror image); observations ``y`` are noisy with false-negative rate
``P_M`` and false-positive rate ``P_F``; a mixture over ``T`` with
``K`` components carries posterior component weights ``tau``; the
component with the largest weight makes the prediction (eq. 14).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from functools import wraps
from typing import (Callable, Dict, List, Optional, Sequence, Tuple, TypeVar,
                    Union, cast)

import numpy as np
import numpy.typing as npt

_F = TypeVar("_F", bound=Callable[..., object])
Array = npt.NDArray[np.float64]
ArrayLike = Union[float, npt.NDArray[np.float64], Sequence[float]]


def _quiet(fn: _F) -> _F:
    """Silence numpy's floating-point warnings inside an entry point: the
    recursions deliberately push through exp underflow, log(0) and
    inf - inf, and clip or floor the results afterwards."""
    @wraps(fn)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        with np.errstate(all="ignore"):
            return fn(*args, **kwargs)
    return wrapper  # type: ignore[return-value]

# --------------------------------------------------------- clip conventions

LOG_FLOOR = math.log(1e-10)
LOG_CEIL = math.log(0.999999)
P_FLOOR = 1e-10
P_CEIL = 0.999999

FAMILIES = ("exponential", "lognormal")
FILTER_KINDS = ("persistence", "emergence")
RESET_MODES = ("belief", "model_posterior", "none")

_ERFC = np.frompyfunc(math.erfc, 1, 1)
_ERF = np.frompyfunc(math.erf, 1, 1)


def clip_log(x: ArrayLike) -> Array:
    """``math_utils.clip_log_prob``: clip a log-probability to the bounds.
    NaN stays NaN, like ``jnp.clip``."""
    return np.asarray(np.clip(np.asarray(x, dtype=float), LOG_FLOOR, LOG_CEIL),
                      dtype=float)


def clip_prob(p: ArrayLike) -> Array:
    """``math_utils.clip_prob``."""
    return np.asarray(np.clip(np.asarray(p, dtype=float), P_FLOOR, P_CEIL),
                      dtype=float)


def ntn_pspace(p: ArrayLike) -> Array:
    """``math_utils.ntn_pspace``: NaN / -inf -> floor, +inf -> ceiling."""
    return np.asarray(np.nan_to_num(np.asarray(p, dtype=float), nan=P_FLOOR,
                                    neginf=P_FLOOR, posinf=P_CEIL), dtype=float)


def ntn_logspace(x: ArrayLike) -> Array:
    return np.asarray(np.nan_to_num(np.asarray(x, dtype=float), nan=LOG_FLOOR,
                                    neginf=LOG_FLOOR, posinf=LOG_CEIL), dtype=float)


@_quiet
def logdiff(logx: ArrayLike, logy: ArrayLike) -> Array:
    """``log(exp(logx) - exp(logy))`` with the reference's floor rule:
    where ``exp(logy - logx)`` is within ``isclose`` tolerance of 1 the
    result is the log floor (mass 1e-10), not -inf. Elementwise."""
    logx = np.asarray(logx, dtype=float)
    logy = np.asarray(logy, dtype=float)
    if True:
        ratio = np.exp(logy - logx)
        close = np.isclose(ratio, 1.0, rtol=1e-5, atol=1e-8)
        safe_ratio = np.where(close, 0.0, ratio)
        out = ntn_logspace(logx + np.log1p(-safe_ratio))
    return np.asarray(np.where(close, LOG_FLOOR, out), dtype=float)


@_quiet
def logsumexp2(a: ArrayLike, b: ArrayLike) -> Array:
    """Stable elementwise ``log(exp(a) + exp(b))`` (``jax_utils.logsumexp``)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = np.maximum(a, b)
    return np.asarray(np.log(np.exp(a - m) + np.exp(b - m)) + m, dtype=float)


@_quiet
def logsumexp(x: ArrayLike, axis: int = -1) -> Array:
    x = np.asarray(x, dtype=float)
    m = np.max(x, axis=axis, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)
    out = np.log(np.sum(np.exp(x - m), axis=axis)) + np.squeeze(m, axis)
    return np.asarray(out, dtype=float)


@_quiet
def _log_norm_sf(z: ArrayLike) -> Array:
    """log of the standard normal survival function, elementwise."""
    z = np.asarray(z, dtype=float)
    return np.asarray(np.log(0.5 * _ERFC(z / math.sqrt(2.0)).astype(float)),
                      dtype=float)


# ------------------------------------------------------- survival mixtures

@dataclass(frozen=True)
class SurvivalMixture:
    """A ``K``-component mixture prior over a survival time.

    ``family`` is ``exponential`` (``params["lambda_"]``, rates) or
    ``lognormal`` (``params["logmu"]``, ``params["std"]`` of ``log T``).
    ``weights`` are the prior mixing coefficients ``pi``.
    """

    family: str
    params: Dict[str, Array]
    weights: Array

    def __post_init__(self) -> None:
        if self.family not in FAMILIES:
            raise ValueError(f"SurvivalMixture: family {self.family!r} "
                             f"not in {FAMILIES}")
        object.__setattr__(self, "weights",
                           np.asarray(self.weights, dtype=float))
        object.__setattr__(self, "params", {
            k: np.asarray(v, dtype=float) for k, v in self.params.items()})
        keys = ("lambda_",) if self.family == "exponential" else ("logmu", "std")
        for k in keys:
            if k not in self.params or self.params[k].shape != self.weights.shape:
                raise ValueError(f"SurvivalMixture({self.family}): param "
                                 f"{k!r} must have shape {self.weights.shape}")
        if self.weights.ndim != 1 or self.weights.size == 0:
            raise ValueError("SurvivalMixture: weights must be a 1-d vector")

    @property
    def n_components(self) -> int:
        return int(self.weights.size)

    @staticmethod
    def exponential(rates: ArrayLike,
                    weights: ArrayLike) -> "SurvivalMixture":
        return SurvivalMixture("exponential", {"lambda_": np.asarray(rates)},
                               np.asarray(weights))

    @staticmethod
    def lognormal(logmu: ArrayLike, std: ArrayLike,
                  weights: ArrayLike) -> "SurvivalMixture":
        return SurvivalMixture("lognormal", {"logmu": np.asarray(logmu),
                                             "std": np.asarray(std)},
                               np.asarray(weights))

    def component(self, k: int) -> "SurvivalMixture":
        return SurvivalMixture(self.family,
                               {n: v[k:k + 1] for n, v in self.params.items()},
                               np.ones(1))

    @_quiet
    def log_survival(self, t: ArrayLike) -> Array:
        """Clipped ``log S_k(t)`` for every component; ``t`` broadcasts
        against a trailing component axis: the result has shape
        ``t.shape + (K,)``. Non-positive ``t`` gives the ceiling (survival
        1) for both families, which is the reference's value for the
        exponential family at t <= 0 and at t == 0 for the lognormal."""
        t = np.asarray(t, dtype=float)[..., None]
        if True:
            if self.family == "exponential":
                raw = -self.params["lambda_"] * t
            else:
                z = (np.log(np.where(t > 0, t, 1.0)) - self.params["logmu"]) \
                    / self.params["std"]
                raw = _log_norm_sf(z)
            raw = np.where(t <= 0, LOG_CEIL, raw)
        return clip_log(raw)

    def median_survival_s(self) -> Array:
        if self.family == "exponential":
            return np.asarray(math.log(2.0) / self.params["lambda_"], dtype=float)
        return np.asarray(np.exp(self.params["logmu"]), dtype=float)

    def as_dict(self) -> Dict[str, List[float]]:
        out = {k: v.tolist() for k, v in self.params.items()}
        out["pi"] = self.weights.tolist()
        return out


def single_component_prior(family: str, median_s: float) -> SurvivalMixture:
    """The fallback prior used before an edge has enough segments to fit:
    one component with the given median survival time (seconds). The
    lognormal spread is the EM initialisation value ``std = 1``."""
    if median_s <= 0:
        raise ValueError(f"single_component_prior: median {median_s} <= 0")
    if family == "exponential":
        return SurvivalMixture.exponential([math.log(2.0) / median_s], [1.0])
    return SurvivalMixture.lognormal([math.log(median_s)], [1.0], [1.0])


# --------------------------------------------------- filters (one mixture)

@dataclass
class FilterState:
    """The recursive state of a mixture of persistence filters (or, with
    the emergence update rule, a mixture of emergence filters).

    ``prior`` supplies ``S_k``; ``t0`` is the filter's initialisation time
    (survival is measured from it); ``last_t`` the last observation time.
    ``log_likelihood`` is ``log p(Y_1:N | T >= t_N)`` (paper eq. 4, shared
    by all components); ``log_lower`` the per-component lower partial
    evidence ``L`` (eq. 11); ``log_cond_evidence`` the per-component
    conditional evidence (eq. 6); ``pi`` the current mixing weights and
    ``pi_init`` the ones a reset falls back on (eq. 18).
    """

    prior: SurvivalMixture
    t0: float
    last_t: float
    log_likelihood: float = 0.0
    log_lower: Array = field(default_factory=lambda: np.zeros(1))
    lower_is_none: bool = True
    log_cond_evidence: Array = field(default_factory=lambda: np.zeros(1))
    pi: Array = field(default_factory=lambda: np.ones(1))
    pi_init: Array = field(default_factory=lambda: np.ones(1))

    @staticmethod
    def create(prior: SurvivalMixture, t0: float,
               pi: Optional[ArrayLike] = None) -> "FilterState":
        weights = (prior.weights.copy() if pi is None
                   else np.asarray(pi, dtype=float))
        k = prior.n_components
        return FilterState(prior=prior, t0=float(t0), last_t=float(t0),
                           log_lower=np.zeros(k), log_cond_evidence=np.zeros(k),
                           pi=weights.copy(), pi_init=prior.weights.copy())

    @property
    def n_components(self) -> int:
        return self.prior.n_components

    def log_survival(self, t: ArrayLike) -> Array:
        return self.prior.log_survival(np.asarray(t, dtype=float) - self.t0)

    @property
    def log_joint_evidence(self) -> Array:
        with np.errstate(divide="ignore"):
            return np.asarray(self.log_cond_evidence + np.log(self.pi), dtype=float)

    @property
    def log_evidence(self) -> float:
        return float(logsumexp(self.log_joint_evidence))

    @property
    def log_tau(self) -> Array:
        """Posterior component weights ``log p(C_k | Y_1:N)`` (eq. 12-13)."""
        return self.log_joint_evidence - self.log_evidence

    @property
    def dominant(self) -> int:
        """Index of the heaviest posterior component (first on ties)."""
        return int(np.argmax(self.log_tau))

    def copy(self) -> "FilterState":
        return replace(self, log_lower=self.log_lower.copy(),
                       log_cond_evidence=self.log_cond_evidence.copy(),
                       pi=self.pi.copy(), pi_init=self.pi_init.copy())


@_quiet
def persistence_update(state: FilterState, y: bool, t: float,
                       p_m: float, p_f: float,
                       forgetting: float = 1.0) -> FilterState:
    """``PersistenceFilter.update``: fold one observation into the state.

    ``forgetting`` is Perpetua*'s ``gamma``: the running log-likelihood is
    scaled by it before the new term is added (1.0 = plain Perpetua).
    """
    t = float(t)
    log_pf_term = math.log(p_f if y else 1.0 - p_f)
    if state.lower_is_none:
        s = clip_prob(np.exp(clip_log(state.log_survival(t))))
        log_lower = log_pf_term + np.log1p(-s)
    else:
        log_df = logdiff(state.log_survival(state.last_t),
                         state.log_survival(t))
        log_lower = logsumexp2(state.log_lower,
                               state.log_likelihood + log_df) + log_pf_term
    log_likelihood = (forgetting * state.log_likelihood
                      + math.log(1.0 - p_m if y else p_m))
    log_cond = logsumexp2(log_lower, log_likelihood + state.log_survival(t))
    return replace(state, log_lower=log_lower, lower_is_none=False,
                   log_likelihood=log_likelihood, last_t=t,
                   log_cond_evidence=log_cond)


@_quiet
def persistence_predict(state: FilterState, t: ArrayLike) -> Array:
    """``PersistenceFilter.predict``: ``p(X_t = 1 | C_k, Y_1:N)`` for every
    component, clipped. ``t`` may be a scalar or a vector (``t >= last_t``
    by contract); the result has a trailing component axis."""
    if True:
        post = np.exp(state.log_likelihood - state.log_cond_evidence
                      + state.log_survival(np.asarray(t, dtype=float)))
    return clip_prob(post)


def emergence_update(state: FilterState, y: bool, t: float,
                     p_m: float, p_f: float,
                     forgetting: float = 1.0) -> FilterState:
    """``EmergenceFilter.update``: the persistence recursion with the
    measurement model mirrored (``P_M' = 1 - P_F``, ``P_F' = 1 - P_M``);
    a no-op while the filter is uninitialised (``t0 = inf``)."""
    if math.isinf(state.t0):
        return state
    return persistence_update(state, y, t, 1.0 - p_f, 1.0 - p_m, forgetting)


@_quiet
def emergence_predict(state: FilterState, t: ArrayLike) -> Array:
    """``EmergenceFilter.predict``: presence probability under the
    emergence model, ``1 - (persistence recursion)``; zero while the
    filter is uninitialised."""
    pred = ntn_pspace(1.0 - persistence_predict(state, t))
    if math.isinf(state.last_t):
        return np.zeros_like(pred)
    return np.asarray(pred, dtype=float)


@_quiet
def mixture_predict(state: FilterState, t: ArrayLike, kind: str
                    ) -> Tuple[Array, Array]:
    """``Mixture{Persistence,Emergence}Filters.predict``: the dominant
    component's posterior (paper eq. 14) and all components' posteriors."""
    if kind == "persistence":
        comps = persistence_predict(state, t)
    else:
        comps = emergence_predict(state, t)
    return comps[..., state.dominant], comps


@_quiet
def reset_with_mixed_weights(state: FilterState, t: float,
                             eps: float) -> FilterState:
    """Perpetua eq. 18: re-initialise the mixture at ``t`` with weights
    ``(1 - eps) * posterior + eps * prior``; ``pi_init`` keeps the prior."""
    weights = np.exp(state.log_tau) * (1.0 - eps) + state.pi_init * eps
    fresh = FilterState.create(state.prior, t, pi=weights)
    fresh.pi_init = state.pi_init.copy()
    return fresh


# ------------------------------------------- Perpetua pair state machine

@dataclass
class PairBatch:
    """``n`` single-component Perpetua machines run side by side, one per
    (emergence component i, persistence component j) pair
    (``Perpetua._init_filters``). Arrays are per pair. ``state`` is 1 in
    the persistence state, 0 in the emergence state."""

    pf_prior: SurvivalMixture      # persistence params, one per pair
    ef_prior: SurvivalMixture      # emergence params, one per pair
    pf_t0: Array
    pf_loglik: Array
    pf_log_lower: Array
    pf_lower_none: Array      # bool
    pf_log_cond: Array
    ef_t0: Array
    ef_last_t: Array
    ef_loglik: Array
    ef_log_lower: Array
    ef_lower_none: Array
    ef_log_cond: Array
    state: Array              # int
    weight: Array

    def copy(self) -> "PairBatch":
        return PairBatch(*(v.copy() if isinstance(v, np.ndarray) else v
                           for v in self.__dict__.values()))


def _pair_persistence_p(b: PairBatch, t: float) -> Array:
    log_s = _batched_log_survival(b.pf_prior, t - b.pf_t0)
    return clip_prob(np.exp(b.pf_loglik - b.pf_log_cond + log_s))


def _pair_emergence_p(b: PairBatch, t: float) -> Array:
    log_s = _batched_log_survival(b.ef_prior, t - b.ef_t0)
    if True:
        pred = ntn_pspace(1.0 - clip_prob(np.exp(b.ef_loglik - b.ef_log_cond
                                                 + log_s)))
    return np.asarray(np.where(np.isinf(b.ef_last_t), 0.0, pred), dtype=float)


@_quiet
def _batched_log_survival(prior: SurvivalMixture, dt: ArrayLike) -> Array:
    """``log S_i(dt_i)`` for pair-aligned params (diagonal of the
    ``(n, n)`` broadcast)."""
    dt = np.asarray(dt, dtype=float)
    if True:
        if prior.family == "exponential":
            raw = -prior.params["lambda_"] * dt
        else:
            z = (np.log(np.where(dt > 0, dt, 1.0)) - prior.params["logmu"]) \
                / prior.params["std"]
            raw = _log_norm_sf(z)
        raw = np.where(dt <= 0, LOG_CEIL, raw)
    return clip_log(raw)


@dataclass
class PerpetuaState:
    """The Perpetua state machine over two mixtures (``Perpetua.py``).

    ``pf`` is the mixture of persistence filters (initialised at ``t0``),
    ``ef`` the mixture of emergence filters (initialised at +inf until the
    first switch). ``current_state`` is 1 in the persistence state. The
    machine switches to emergence when the heaviest pair's belief drops
    to ``delta_low`` and back when it reaches ``delta_high``; each switch
    re-initialises the entered mixture at the switch time with eq. 18's
    ``eps``-mixed weights. ``num_steps`` interpolation points are placed
    between consecutive query/observation times when the switching is
    simulated (``create_interpolated_array``).
    """

    pf: FilterState
    ef: FilterState
    t0: float
    last_t: float
    delta_low: float = 0.05
    delta_high: float = 0.95
    num_steps: int = 10
    eps: float = 0.1
    current_state: int = 1
    switch_counter: int = 1

    @staticmethod
    def create(pf_prior: SurvivalMixture, ef_prior: SurvivalMixture,
               t0: float, delta_low: float = 0.05, delta_high: float = 0.95,
               num_steps: int = 10, eps: float = 0.1) -> "PerpetuaState":
        return PerpetuaState(pf=FilterState.create(pf_prior, t0),
                             ef=FilterState.create(ef_prior, math.inf),
                             t0=float(t0), last_t=float(t0),
                             delta_low=delta_low, delta_high=delta_high,
                             num_steps=int(num_steps), eps=eps)

    # -- the k^2 pair machines -----------------------------------------

    def pairs(self) -> PairBatch:
        """``Perpetua._init_filters``: one single-component machine per
        (emergence i, persistence j) pair, weight ``tau_e[i] + tau_p[j]``,
        all in the mixture's current switching state."""
        ke, kp = self.ef.n_components, self.pf.n_components
        ii, jj = np.meshgrid(np.arange(ke), np.arange(kp), indexing="ij")
        ii, jj = ii.ravel(), jj.ravel()
        tau_e, tau_p = np.exp(self.ef.log_tau), np.exp(self.pf.log_tau)
        n = ii.size
        pf_prior = SurvivalMixture(
            self.pf.prior.family,
            {k: v[jj] for k, v in self.pf.prior.params.items()}, np.ones(n))
        ef_prior = SurvivalMixture(
            self.ef.prior.family,
            {k: v[ii] for k, v in self.ef.prior.params.items()}, np.ones(n))
        return PairBatch(
            pf_prior=pf_prior, ef_prior=ef_prior,
            pf_t0=np.full(n, self.pf.t0), pf_loglik=np.full(n, self.pf.log_likelihood),
            pf_log_lower=self.pf.log_lower[jj].copy(),
            pf_lower_none=np.full(n, self.pf.lower_is_none),
            pf_log_cond=self.pf.log_cond_evidence[jj].copy(),
            ef_t0=np.full(n, self.ef.t0), ef_last_t=np.full(n, self.ef.last_t),
            ef_loglik=np.full(n, self.ef.log_likelihood),
            ef_log_lower=self.ef.log_lower[ii].copy(),
            ef_lower_none=np.full(n, self.ef.lower_is_none),
            ef_log_cond=self.ef.log_cond_evidence[ii].copy(),
            state=np.full(n, self.current_state, dtype=int),
            weight=tau_e[ii] + tau_p[jj])

    @_quiet
    def simulate(self, query_times: Sequence[float]
                 ) -> Tuple[Array, Array, Array]:
        """``Perpetua.simulate_switching``: run every pair machine from
        ``last_t`` through the interpolated query times without touching
        this state. Returns ``(belief[n_pairs, m], states[n_pairs, m],
        weights[n_pairs])`` with weights normalised."""
        points = np.concatenate([[self.last_t],
                                 np.asarray(query_times, dtype=float)])
        # Two levels of interpolation, as in the reference: the mixture
        # machine interpolates the query times, and each pair machine
        # (``SinglePerpetua.predict``) interpolates that grid again.
        outer = interpolate_points(points, self.num_steps)
        inner = interpolate_points(outer, self.num_steps)
        batch = self.pairs()
        beliefs = np.empty((batch.weight.size, inner.size))
        states = np.empty((batch.weight.size, inner.size), dtype=int)
        for g, q in enumerate(inner):
            beliefs[:, g], states[:, g] = _pair_step(batch, float(q), self)
        at_outer = collect_indices(len(outer), self.num_steps)   # outer[1:]
        pick = collect_indices(len(points), self.num_steps) - 1  # into outer[1:]
        keep = at_outer[pick]
        weights = batch.weight / batch.weight.sum()
        return beliefs[:, keep], states[:, keep], weights

    def predict(self, query_times: Sequence[float]) -> Array:
        """``Perpetua.predict`` reduced to the heaviest pair (eq. 14 over
        pairs): presence belief at each query time."""
        beliefs, _, weights = self.simulate(query_times)
        return np.asarray(beliefs[int(np.argmax(weights))], dtype=float)

    # -- update ----------------------------------------------------------

    @_quiet
    def update(self, y: bool, t: float, p_m: float, p_f: float
               ) -> List[Tuple[float, str]]:
        """``Perpetua.update``: simulate the switching from ``last_t`` to
        ``t`` (resetting the mixtures on switches), then fold the
        observation into both mixtures. Returns the switch events
        ``(time, direction)`` for logging."""
        t = float(t)
        grid = interpolate_points(np.array([self.last_t, t]), self.num_steps)
        events: List[Tuple[float, str]] = []
        batch = self.pairs()      # fixed for the whole scan, as in the reference
        for q in grid:
            q = float(q)
            sim = batch.copy()
            inner = interpolate_points(np.array([self.last_t, q]), self.num_steps)
            for r in inner:
                belief, _ = _pair_step(sim, float(r), self)
            weights = sim.weight / sim.weight.sum()
            prediction = belief[int(np.argmax(weights))]
            if self.current_state == 1 and prediction <= self.delta_low:
                self.ef = reset_with_mixed_weights(self.ef, q, self.eps)
                self.current_state = 0
                events.append((q, "to_emergence"))
            if self.current_state == 0 and prediction >= self.delta_high:
                self.pf = reset_with_mixed_weights(self.pf, q, self.eps)
                self.current_state = 1
                self.switch_counter += 1
                events.append((q, "to_persistence"))
        self.pf = persistence_update(self.pf, y, t, p_m, p_f)
        self.ef = emergence_update(self.ef, y, t, p_m, p_f)
        self.last_t = t
        return events


@_quiet
def _pair_step(b: PairBatch, q: float, cfg: PerpetuaState
               ) -> Tuple[Array, Array]:
    """``SinglePerpetua.step_simulate_switching`` over a batch of pairs,
    in place. Returns the belief of each pair's (post-switch) state and
    the states."""
    e_p = _pair_emergence_p(b, q)
    p_p = _pair_persistence_p(b, q)
    case1 = (b.state == 1) & (p_p <= cfg.delta_low)
    if case1.any():
        _reset_pair_filter(b, "ef", case1, q)
        e_p = _pair_emergence_p(b, q)
        p_p = _pair_persistence_p(b, q)
        b.state = np.where(case1, 0, b.state)
    case3 = (b.state == 0) & (e_p >= cfg.delta_high)
    if case3.any():
        _reset_pair_filter(b, "pf", case3, q)
        e_p = _pair_emergence_p(b, q)
        p_p = _pair_persistence_p(b, q)
        b.state = np.where(case3, 1, b.state)
    belief = np.asarray(np.where(b.state == 1, p_p, e_p), dtype=float)
    return belief, b.state.copy()


def _reset_pair_filter(b: PairBatch, which: str, mask: ArrayLike,
                       q: float) -> None:
    """Fresh single filter at ``q`` for the masked pairs."""
    for name, value in (("t0", q), ("loglik", 0.0), ("log_lower", 0.0),
                        ("lower_none", True), ("log_cond", 0.0)):
        key = f"{which}_{name}"
        arr = getattr(b, key)
        setattr(b, key, np.where(mask, value, arr))
    if which == "ef":
        b.ef_last_t = np.asarray(np.where(mask, q, b.ef_last_t), dtype=float)


def interpolate_points(points: ArrayLike, num_steps: int) -> Array:
    """``math_utils.create_interpolated_array``: ``num_steps`` points
    linearly spaced from each point to the next (start inclusive, end
    exclusive), followed by the final point."""
    points = np.asarray(points, dtype=float)
    pieces = [np.linspace(a, b, num_steps, endpoint=False)
              for a, b in zip(points[:-1], points[1:])]
    return np.concatenate(pieces + [points[-1:]])


def collect_indices(n_points: int, num_steps: int) -> npt.NDArray[np.int_]:
    """Indices into :func:`interpolate_points`' output that fall on the
    original points 1..n-1 (the reference's ``collect``)."""
    idx = [k * num_steps for k in range(1, n_points - 1)]
    idx.append((n_points - 1) * num_steps)
    return np.asarray(idx, dtype=int)


# --------------------------------------------- Perpetua* (arXiv 2605.00121)

@dataclass
class PerpetuaStarState:
    """Perpetua* for one feature: both mixtures updated on every
    observation, Bayesian model selection between them (eq. 11-13).

    Deviation from the paper (2026-09-03). The paper never says whether
    the mixtures are ever re-initialised. Run literally from a fixed
    origin (``reset_mode="none"``), a persistence mixture whose survival
    prior lives on the hour scale has prior mass ``1 - F(t)`` that
    vanishes within days, and its posterior collapses to "absent" no
    matter what is observed (the emergence mixture fails the mirror way).
    So Perpetua's resets are kept, without its simulation steps:

    * ``reset_mode="belief"`` (default): after each observation is folded
      into both mixtures, the eq. 13 presence belief at the observation
      time (``alpha = 1``) is the MAP estimate of the current phase; when
      it crosses 0.5 against the current phase, BOTH mixtures restart at
      that time with eq. 18's ``eps``-mixed weights and are seeded with
      the observation. Both restart so that the two evidences compared
      in eq. 12 always cover the same observation window; a reset of the
      entered mixture alone leaves a fresh model's evidence over a few
      observations against a stale model's over many, which is not a
      model comparison at all.
    * ``reset_mode="model_posterior"``: the first proposal, kept as a
      diagnostic: when the eq. 12 model posterior (``alpha = 1``, after
      the observation) flips, the newly dominant mixture alone restarts,
      seeded with the observation. On our sparse streams it ping-pongs:
      the model posterior names the story that explains the window that
      just ended, not the phase that begins, so the entered model is
      contradicted by the very observation that triggered the flip.
    * ``reset_mode="none"``: the literal fixed-origin recursion.

    Every reset is returned by :meth:`update` as ``(time, direction)``.

    ``gamma`` is the forgetting factor on the measurement likelihood
    (eq. 4); ``alpha0`` the annealing rate, per second, of
    ``alpha(t) = exp(-alpha0 (t - t_N))`` (eq. 12).
    """

    pf: FilterState
    ef: FilterState
    t0: float
    last_t: float
    gamma: float = 0.99
    alpha0: float = 0.01 / 3600.0
    eps: float = 0.1
    reset_mode: str = "belief"
    dominant_model: str = "persistence"

    @staticmethod
    def create(pf_prior: SurvivalMixture, ef_prior: SurvivalMixture,
               t0: float, gamma: float = 0.99, alpha0: float = 0.01 / 3600.0,
               eps: float = 0.1, reset_mode: str = "belief"
               ) -> "PerpetuaStarState":
        if reset_mode not in RESET_MODES:
            raise ValueError(f"PerpetuaStarState: reset_mode {reset_mode!r} "
                             f"not in {RESET_MODES}")
        return PerpetuaStarState(pf=FilterState.create(pf_prior, t0),
                                 ef=FilterState.create(ef_prior, t0),
                                 t0=float(t0), last_t=float(t0), gamma=gamma,
                                 alpha0=alpha0, eps=eps, reset_mode=reset_mode)

    @_quiet
    def log_model_posterior(self, t: float, prior_presence: float
                            ) -> Tuple[float, float]:
        """Eq. 12: ``(log p(M_P | Y), log p(M_E | Y))`` at time ``t`` given
        the switching prior ``f(t) = p_t(M_E) = prior_presence``."""
        alpha = math.exp(-self.alpha0 * max(0.0, float(t) - self.last_t))
        f = min(max(float(prior_presence), 1e-12), 1.0 - 1e-12)
        log_p = alpha * self.pf.log_evidence + math.log(1.0 - f)
        log_e = alpha * self.ef.log_evidence + math.log(f)
        norm = float(logsumexp2(np.asarray(log_p), np.asarray(log_e)))
        return float(log_p - norm), float(log_e - norm)

    @_quiet
    def predict(self, t: float, prior_presence: float) -> Tuple[float, Dict[str, float]]:
        """Eq. 13: model-posterior-weighted average of the two dominant
        components' presence posteriors. Also returns the pieces."""
        log_p, log_e = self.log_model_posterior(t, prior_presence)
        p_pers = float(mixture_predict(self.pf, np.asarray(float(t)), "persistence")[0])
        p_emer = float(mixture_predict(self.ef, np.asarray(float(t)), "emergence")[0])
        w_p, w_e = math.exp(log_p), math.exp(log_e)
        belief = w_p * p_pers + w_e * p_emer
        return belief, {"p_persistence_model": w_p, "belief_persistence": p_pers,
                        "belief_emergence": p_emer}

    @_quiet
    def update(self, y: bool, t: float, p_m: float, p_f: float,
               prior_presence: float) -> List[Tuple[float, str]]:
        """Fold one observation into both mixtures (with forgetting), then
        apply the reset rule of ``reset_mode`` (class docstring). Returns
        the reset events ``(time, direction)``."""
        t = float(t)
        events: List[Tuple[float, str]] = []
        self.pf = persistence_update(self.pf, y, t, p_m, p_f, self.gamma)
        self.ef = emergence_update(self.ef, y, t, p_m, p_f, self.gamma)
        self.last_t = t
        if self.reset_mode == "belief":
            belief, _ = self.predict(t, prior_presence)
            phase = "persistence" if belief >= 0.5 else "emergence"
            if phase != self.dominant_model:
                self.pf = persistence_update(
                    reset_with_mixed_weights(self.pf, t, self.eps),
                    y, t, p_m, p_f, self.gamma)
                self.ef = emergence_update(
                    reset_with_mixed_weights(self.ef, t, self.eps),
                    y, t, p_m, p_f, self.gamma)
                self.dominant_model = phase
                events.append((t, f"to_{phase}"))
        elif self.reset_mode == "model_posterior":
            log_p, log_e = self.log_model_posterior(t, prior_presence)
            new = "persistence" if log_p >= log_e else "emergence"
            if new != self.dominant_model:
                if new == "emergence":
                    fresh = reset_with_mixed_weights(self.ef, t, self.eps)
                    self.ef = emergence_update(fresh, y, t, p_m, p_f, self.gamma)
                else:
                    fresh = reset_with_mixed_weights(self.pf, t, self.eps)
                    self.pf = persistence_update(fresh, y, t, p_m, p_f, self.gamma)
                self.dominant_model = new
                events.append((t, f"to_{new}"))
        return events


# ------------------------------------------------------------ EM learning

@dataclass(frozen=True)
class Segment:
    """One training sequence: observation times relative to its first
    observation (``times[0] == 0``) and boolean observations."""

    times: Array
    y: npt.NDArray[np.bool_]

    def __post_init__(self) -> None:
        object.__setattr__(self, "times", np.asarray(self.times, dtype=float))
        object.__setattr__(self, "y", np.asarray(self.y, dtype=bool))
        if self.times.shape != self.y.shape or self.times.ndim != 1 \
                or self.times.size == 0:
            raise ValueError("Segment: times and y must be equal-length 1-d")


@dataclass(frozen=True)
class FitResult:
    mixture: SurvivalMixture
    log_evidence: float
    n_iter: int
    aic: float
    per_k: Dict[int, SurvivalMixture] = field(default_factory=dict)
    """Best fit found for every mixture size tried; the next refit of the
    same edge warm-starts from these."""


class _Batch:
    """Padded segment batch with the per-interval measurement
    log-likelihoods ``ll[j, i]`` (paper eq. 3 evaluated at ``T = T_i``,
    ``T_0 = 0``, ``T_i = t_i``), shared by every E-step."""

    def __init__(self, segments: Sequence[Segment], kind: str,
                 p_m: float, p_f: float) -> None:
        if kind not in FILTER_KINDS:
            raise ValueError(f"filter kind {kind!r} not in {FILTER_KINDS}")
        self.n_seg = len(segments)
        self.n_obs = np.array([s.y.size for s in segments])
        n_max = int(self.n_obs.max())
        # thresholds T_0..T_N (N+1 per segment), padded with the last value
        self.thresholds = np.zeros((self.n_seg, n_max + 1))
        self.valid = np.zeros((self.n_seg, n_max + 1), dtype=bool)
        self.is_last = np.zeros((self.n_seg, n_max + 1), dtype=bool)
        self.ll = np.full((self.n_seg, n_max + 1), -np.inf)
        log_m = np.log(np.array([1.0 - p_m, p_m]))   # present: y=1, y=0
        log_f = np.log(np.array([p_f, 1.0 - p_f]))   # absent:  y=1, y=0
        for j, s in enumerate(segments):
            n = s.y.size
            self.thresholds[j, 1:n + 1] = s.times
            self.thresholds[j, n + 1:] = s.times[-1]
            self.valid[j, :n + 1] = True
            self.is_last[j, n] = True
            idx = np.where(s.y, 0, 1)
            m = np.concatenate([[0.0], np.cumsum(log_m[idx])])
            f = np.concatenate([[0.0], np.cumsum(log_f[idx])])
            if kind == "persistence":      # t <= T present, t > T absent
                self.ll[j, :n + 1] = m + (f[-1] - f)
            else:                          # t <= T absent, t > T present
                self.ll[j, :n + 1] = f + (m[-1] - m)
        self.longest = float(max(s.times[-1] for s in segments))

    @_quiet
    def log_interval_mass(self, prior: SurvivalMixture) -> Array:
        """``log [F_k(T_{i+1}) - F_k(T_i)]`` per (segment, interval,
        component), mirroring the filter recursion's terms: the first
        interval uses ``log1p(-S(T_1))`` on the clipped survival, later
        ones ``logdiff``, and the last (to infinity) ``log S(T_N)``."""
        log_s = prior.log_survival(self.thresholds)          # (J, N+1, K)
        first = np.log1p(-clip_prob(np.exp(clip_log(log_s[:, 1:2, :]))))
        middle = logdiff(log_s[:, 1:-1, :], log_s[:, 2:, :])
        mass = np.concatenate([first, middle, np.full_like(first, -np.inf)],
                              axis=1)                          # intervals 0..N
        mass = np.where(self.is_last[:, :, None], log_s, mass)
        return np.asarray(np.where(self.valid[:, :, None], mass, -np.inf),
                          dtype=float)

    @_quiet
    def log_joint(self, prior: SurvivalMixture) -> Array:
        """``log p(Y_j, C_k)`` = ``log p(Y_j | C_k) + log pi_k`` (eq. 5, 12)."""
        terms = self.ll[:, :, None] + self.log_interval_mass(prior)
        return np.asarray(logsumexp(terms, axis=1) + np.log(prior.weights),
                          dtype=float)


@_quiet
def _e_step_exponential(batch: _Batch, prior: SurvivalMixture
                        ) -> Tuple[Array, Array, Array]:
    """``mixture_exponential.process_sequence`` for every segment:
    ``(phi[J,K], psi[J,K], log_evidence[J])``."""
    lam = prior.params["lambda_"]
    log_joint = batch.log_joint(prior)
    log_ev = logsumexp(log_joint, axis=1)
    phi = np.exp(log_joint - log_ev[:, None])
    T = batch.thresholds[:, :, None]
    if True:
        g = -lam * T + np.log(T + 1.0 / lam)                  # (J, N+1, K)
    rho = logdiff(g[:, :-1, :], g[:, 1:, :])
    rho = np.concatenate([rho, g[:, -1:, :]], axis=1)
    rho = np.where(batch.is_last[:, :, None], g, rho)
    rho = np.where(batch.valid[:, :, None], rho, -np.inf)
    if True:
        log_psi = logsumexp(batch.ll[:, :, None] + rho, axis=1) + np.log(prior.weights)
    psi = np.exp(log_psi - log_ev[:, None])
    return phi, psi, log_ev


@_quiet
def _lognormal_log_t_integral(mu: Array, sigma: Array,
                              lo: Array, hi: Array) -> Array:
    """``mixture_lognormal.compute_log_t_expectation``:
    ``integral_lo^hi p(T) log T dT`` for a lognormal, clipped at 1e-10."""
    eps = 1e-10
    a = np.log(lo + eps) - mu
    b = np.log(np.where(np.isinf(hi), 1.0, hi) + eps) - mu
    b = np.where(np.isinf(hi), np.inf, b)
    s2 = np.sqrt(2.0) * sigma
    if True:
        term1 = sigma / math.sqrt(2 * math.pi) * np.exp(-a * a / (2 * sigma ** 2))
        term2 = np.where(np.isinf(b), 0.0,
                         -sigma / math.sqrt(2 * math.pi) * np.exp(-b * b / (2 * sigma ** 2)))
        erf_b = np.where(np.isinf(b), 1.0, _ERF(b / s2).astype(float))
        erf_a = _ERF(a / s2).astype(float)
    result = term1 + term2 + 0.5 * mu * (erf_b - erf_a)
    return np.asarray(np.clip(result, 1e-10, None), dtype=float)


@_quiet
def _lognormal_sq_dev_integral(mu: Array, sigma: Array,
                               mu_mle: Array, lo: Array,
                               hi: Array) -> Array:
    """``mixture_lognormal.compute_log_t_mu_expectation``:
    ``integral_lo^hi p(T) (log T - mu_mle)^2 dT``, clipped at 1e-10."""
    eps = 1e-10
    c1 = sigma ** 2 / 2
    c2 = sigma / math.sqrt(2 * math.pi)
    c3 = mu ** 2 / 2
    c4 = math.sqrt(2 / math.pi) * mu * sigma
    dl = np.log(lo + eps) - mu
    dh = np.log(np.where(np.isinf(hi), 1.0, hi) + eps) - mu
    dh = np.where(np.isinf(hi), np.inf, dh)
    s2 = math.sqrt(2.0) * sigma
    if True:
        L = dl / s2
        U = dh / s2
        erf_u = np.where(np.isinf(U), 1.0, _ERF(U).astype(float))
        erf_l = _ERF(L).astype(float)
        exp_u = np.where(np.isinf(U), 0.0, np.exp(-U * U))
        exp_l = np.exp(-L * L)
        first = (c1 * (erf_u - erf_l)
                 + np.where(np.isinf(U), 0.0, -c2 * exp_u * dh)
                 + c2 * exp_l * dl)
        second = np.where(np.isinf(U), 0.0, -c4 * exp_u) + c4 * exp_l
        third = c3 * (erf_u - erf_l)
    first_integral = first + second + third
    second_integral = _lognormal_log_t_integral(mu, sigma, lo, hi) * 2 * mu_mle
    third_integral = (mu_mle ** 2 / 2) * (erf_u - erf_l)
    return np.asarray(np.clip(first_integral - second_integral + third_integral,
                              1e-10, None), dtype=float)


def _interval_bounds(batch: _Batch) -> Tuple[Array, Array]:
    lo = batch.thresholds[:, :, None]
    hi = np.concatenate([batch.thresholds[:, 1:], np.full((batch.n_seg, 1), np.inf)],
                        axis=1)[:, :, None]
    hi = np.where(batch.is_last[:, :, None], np.inf, hi)
    return lo, hi


@_quiet
def _e_step_lognormal(batch: _Batch, prior: SurvivalMixture
                      ) -> Tuple[Array, Array, Array, Array]:
    """``process_sequence_mu`` for every segment: ``(phi, nu, log_evidence)``
    plus the joint needed for the variance step."""
    mu, sigma = prior.params["logmu"], prior.params["std"]
    log_joint = batch.log_joint(prior)
    log_ev = logsumexp(log_joint, axis=1)
    phi = np.exp(log_joint - log_ev[:, None])
    lo, hi = _interval_bounds(batch)
    if True:
        log_int = np.log(_lognormal_log_t_integral(mu, sigma, lo, hi))
        log_int = np.where(batch.valid[:, :, None], log_int, -np.inf)
        log_nu = logsumexp(batch.ll[:, :, None] + log_int, axis=1) + np.log(prior.weights)
    nu = np.exp(log_nu - log_ev[:, None])
    return phi, nu, log_ev, log_joint


@_quiet
def _variance_step_lognormal(batch: _Batch, prior: SurvivalMixture,
                             mu_new: Array, log_ev: Array) -> Array:
    """``process_sequence_var``: ``kappa[J, K]`` with the updated means."""
    mu, sigma = prior.params["logmu"], prior.params["std"]
    lo, hi = _interval_bounds(batch)
    if True:
        log_int = np.log(_lognormal_sq_dev_integral(mu, sigma, mu_new, lo, hi))
        log_int = np.where(batch.valid[:, :, None], log_int, -np.inf)
        log_kappa = logsumexp(batch.ll[:, :, None] + log_int, axis=1) + np.log(prior.weights)
    return np.asarray(np.exp(log_kappa - log_ev[:, None]), dtype=float)


@_quiet
def em_step(batch: _Batch, prior: SurvivalMixture
            ) -> Tuple[SurvivalMixture, float]:
    """One E+M step (``em_step`` of the reference); returns the new
    parameters and the total log-evidence of the OLD ones."""
    if prior.family == "exponential":
        phi, psi, log_ev = _e_step_exponential(batch, prior)
        pi = np.clip(phi.sum(0) / phi.sum(), 1e-10, 1.0)
        lam = np.clip(phi.sum(0) / psi.sum(0), 1e-10, 1e15)
        return SurvivalMixture.exponential(lam, pi), float(log_ev.sum())
    phi, nu, log_ev, _ = _e_step_lognormal(batch, prior)
    pi = np.clip(phi.sum(0) / phi.sum(), 1e-10, 1.0)
    mu = np.clip(nu.sum(0) / phi.sum(0), 1e-10, 1e15)
    kappa = _variance_step_lognormal(batch, prior, mu, log_ev)
    sigma = np.clip(np.sqrt(kappa.sum(0) / phi.sum(0)), 1e-10, 1e15)
    return SurvivalMixture.lognormal(mu, sigma, pi), float(log_ev.sum())


@_quiet
def log_evidence(segments: Sequence[Segment], kind: str, prior: SurvivalMixture,
                 p_m: float, p_f: float) -> float:
    """Total ``log p(Y)`` of the segments under the mixture (eq. 13)."""
    batch = _Batch(segments, kind, p_m, p_f)
    return float(logsumexp(batch.log_joint(prior), axis=1).sum())


@_quiet
def fit_mixture(segments: Sequence[Segment], kind: str, init: SurvivalMixture,
                p_m: float, p_f: float, max_iter: int = 250,
                tol: float = 1e-4) -> FitResult:
    """EM from ``init`` (``fit`` of the reference): iterate until the
    log-evidence moves by less than ``tol`` or ``max_iter`` steps; return
    the best-evidence iterate. AIC counts ``2K`` (exponential) or ``3K``
    (lognormal) parameters, as the reference does. The reference's
    ``tol`` is 1e-6 on a float32 log-evidence, i.e. the float32 resolution
    of sums of a few hundred; 1e-4 is that resolution in float64."""
    batch = _Batch(segments, kind, p_m, p_f)
    prior = init
    best, best_ev = init, -math.inf
    prev_ev = -math.inf
    n_iter = 0
    for n_iter in range(1, max_iter + 1):
        new_prior, ev = em_step(batch, prior)
        if math.isnan(ev):
            break
        if ev > best_ev:
            best, best_ev = prior, ev
        if abs(ev - prev_ev) < tol:
            break
        prev_ev = ev
        prior = new_prior
    n_params = (2 if init.family == "exponential" else 3) * init.n_components
    return FitResult(mixture=best, log_evidence=best_ev, n_iter=n_iter,
                     aic=2 * n_params - 2 * best_ev)


def quantile_init(family: str, longest_s: float, k: int) -> SurvivalMixture:
    """The reference's uninformed initialisation: component scales at the
    ``k`` inner quantiles of a uniform grid over ``[0, longest]``, uniform
    weights, lognormal spread 1."""
    positions = np.linspace(0.0, 1.0, k + 2)[1:-1]
    scales = np.maximum(positions * max(longest_s, 1.0), 1.0)
    if family == "exponential":
        return SurvivalMixture.exponential(1.0 / scales, np.full(k, 1.0 / k))
    return SurvivalMixture.lognormal(np.log(scales), np.ones(k), np.full(k, 1.0 / k))


@_quiet
def empirical_init(family: str, segments: Sequence[Segment],
                   k: int) -> SurvivalMixture:
    """Deterministic data-driven start: component scales at the ``k``
    inner quantiles of the segments' observed transition times (midpoint
    between the last head observation and the first tail observation),
    uniform weights, lognormal spread 1. Stands in for the reference's
    random-perturbation restarts, which the repo's determinism rule
    forbids."""
    transitions = []
    for seg in segments:
        flip = int(np.argmax(seg.y != seg.y[0]))
        if flip > 0:
            transitions.append(float(0.5 * (seg.times[flip - 1] + seg.times[flip])))
    if not transitions:
        return quantile_init(family, max(float(s.times[-1]) for s in segments), k)
    positions = (np.arange(k) + 0.5) / k
    scales = np.maximum(np.quantile(np.asarray(transitions), positions), 1.0)
    # Identical components are a fixed point of EM: spread coincident
    # starts geometrically so every component can move on its own.
    if k > 1 and np.any(np.diff(scales) < 0.01 * scales[:-1]):
        scales = scales * np.exp(0.3 * (np.arange(k) - (k - 1) / 2.0))
    if family == "exponential":
        return SurvivalMixture.exponential(1.0 / scales, np.full(k, 1.0 / k))
    return SurvivalMixture.lognormal(np.log(scales), np.ones(k), np.full(k, 1.0 / k))


def select_mixture(segments: Sequence[Segment], kind: str, family: str,
                   p_m: float, p_f: float, k_range: Sequence[int] = (1, 2, 3),
                   max_iter: int = 250, tol: float = 1e-4,
                   prune_threshold: float = 0.01,
                   warm_starts: Optional[Dict[int, SurvivalMixture]] = None
                   ) -> FitResult:
    """``select_and_refine_model`` without its random perturbation
    retries (the repo bans model randomness). For every ``K`` the EM runs
    from the deterministic starts -- the reference's grid-quantile
    initialisation, the data-driven :func:`empirical_init`, and, when a
    previous fit of the same data stream exists in ``warm_starts``, that
    fit -- and keeps the highest evidence; the lowest AIC across ``K``
    wins. Components under ``prune_threshold`` are pruned, after which one
    deterministic refit at the pruned size replaces the pruned mixture if
    its evidence is higher. With a warm start available the grid start is
    skipped (the warm start descends from it)."""
    longest = max(float(s.times[-1]) for s in segments)
    best: Optional[FitResult] = None
    per_k: Dict[int, SurvivalMixture] = {}
    for k in k_range:
        starts = [empirical_init(family, segments, k)]
        warm = (warm_starts or {}).get(k)
        if warm is not None and warm.n_components == k:
            starts.append(warm)
        else:
            starts.append(quantile_init(family, longest, k))
        fit_k: Optional[FitResult] = None
        for start in starts:
            fit = fit_mixture(segments, kind, start, p_m, p_f, max_iter, tol)
            if fit_k is None or fit.log_evidence > fit_k.log_evidence:
                fit_k = fit
        assert fit_k is not None
        per_k[k] = fit_k.mixture
        if best is None or fit_k.aic < best.aic:
            best = fit_k
    assert best is not None
    best = replace(best, per_k=per_k)
    keep = best.mixture.weights >= prune_threshold
    if not keep.all():
        pruned = SurvivalMixture(
            family, {n: v[keep] for n, v in best.mixture.params.items()},
            best.mixture.weights[keep] / best.mixture.weights[keep].sum())
        pruned_ev = log_evidence(segments, kind, pruned, p_m, p_f)
        n_params = (2 if family == "exponential" else 3) * pruned.n_components
        best = FitResult(pruned, pruned_ev, best.n_iter, 2 * n_params - 2 * pruned_ev)
        refit = fit_mixture(segments, kind,
                            quantile_init(family, longest, pruned.n_components),
                            p_m, p_f, max_iter, tol)
        if refit.log_evidence > best.log_evidence:
            best = refit
        best = replace(best, per_k=per_k)
    return best


# ------------------------------------------------------ segment extraction

def extract_segments(times: Sequence[float], y: Sequence[bool]
                     ) -> Tuple[List[Segment], List[Segment]]:
    """Split one edge's noise-free observation stream into training
    segments (the reference's ``extract_sequences`` with change points at
    the observed flips instead of PELT, decided 2026-09-03).

    Runs of equal ``y`` are the blocks. Every block but the last heads
    one segment made of itself plus the whole following block: a
    presence block heads a persistence segment, an absence block heads
    an emergence segment. The trailing block only ever serves as a tail
    (its own end is unobserved, so it heads nothing). Segment times are
    shifted so the head's first OBSERVATION time is 0 -- the flip
    boundary is always an observation time, never a midpoint.
    """
    t = np.asarray(times, dtype=float)
    obs = np.asarray(y, dtype=bool)
    if t.shape != obs.shape or t.ndim != 1:
        raise ValueError("extract_segments: times and y must match, 1-d")
    if t.size == 0:
        return [], []
    starts = [0] + [i for i in range(1, obs.size) if bool(obs[i] != obs[i - 1])]
    starts.append(obs.size)
    persistence: List[Segment] = []
    emergence: List[Segment] = []
    for b in range(len(starts) - 2):
        head, tail_end = starts[b], starts[b + 2]
        seg = Segment(t[head:tail_end] - t[head], obs[head:tail_end])
        (persistence if obs[head] else emergence).append(seg)
    return persistence, emergence
