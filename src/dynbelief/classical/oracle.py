"""C5 — oracle-parameter filter (CEILING, not a baseline).

Same shared Filter; occupancy and leave rates computed from the GENERATOR by
Monte Carlo over the profile's stochastic branches (jitter draws, after-branch
outcomes, misplacement noise, dish-cycle coin flips): M independent 30-day
simulations, states recorded on a 15-minute grid, aggregated by MINUTE-OF-WEEK
(the generator is weekly periodic, so the week-bucket marginal is the exact
stationary schedule up to MC error; tested against an independent MC run).

This is the ONLY arm allowed to read the profile (L1's explicit exception).
Its required output is accuracy on MOVED episodes: that number decides whether
the LLM/classical "moved wall" is a model failure or irreducible environment
stochasticity (the generator draws branch outcomes the filter cannot know).

NOTE: atyp_shift_v1 is excluded — its per-object log-level scramble is a
bank-level realization, so a generator-marginal oracle is ill-defined there
(documented in the summary)."""
from __future__ import annotations

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.profiles.schema import Profile
from dynbelief.profiles.generator import simulate

MIN_PER_WEEK = 7 * MIN_PER_DAY
GRID_MIN = 15
NBINS = MIN_PER_WEEK // GRID_MIN


class C5Oracle:
    name = "C5_oracle"

    def __init__(self, profile: Profile, candidates: list[str],
                 n_sims: int = 200, n_days: int = 28, seed0: int = 50_000):
        self.profile = profile
        self.candidates = list(candidates)
        self._idx = {c: i for i, c in enumerate(candidates)}
        self.n_sims, self.n_days, self.seed0 = n_sims, n_days, seed0
        self._occ: dict[str, np.ndarray] = {}    # obj -> (NBINS, R) frequencies
        self._leave: dict[str, np.ndarray] = {}  # obj -> (NBINS,) move prob/min
        self._fitted = False

    def fit(self, observation_history: list[dict]) -> None:
        """Ignores the history (oracle); runs the MC once (cached)."""
        if self._fitted:
            return
        objs = sorted(self.profile.placements)
        occ = {o: np.zeros((NBINS, len(self.candidates))) for o in objs}
        moves = {o: np.zeros(NBINS) for o in objs}
        dwell = np.zeros(NBINS)
        for s in range(self.n_sims):
            events, _snaps, _meta = simulate(self.profile, n_days=self.n_days,
                                             seed=self.seed0 + s)
            by_obj: dict[str, list] = {o: [] for o in objs}
            for e in events:
                by_obj[e["label"]].append((e["t_min"], e["parent_label"]))
            horizon = self.n_days * MIN_PER_DAY
            for o in objs:
                cur = self.profile.placements[o].home
                evs = by_obj[o]
                k = 0
                for t in range(0, horizon, GRID_MIN):
                    while k < len(evs) and evs[k][0] <= t:
                        cur = evs[k][1]
                        k += 1
                    b = (t % MIN_PER_WEEK) // GRID_MIN
                    j = self._idx.get(cur, self._idx.get("elsewhere"))
                    occ[o][b, j] += 1
                for (t, _r) in evs:
                    moves[o][(t % MIN_PER_WEEK) // GRID_MIN] += 1
            dwell += (self.n_days * MIN_PER_DAY // MIN_PER_WEEK)  # weeks per sim
        for o in objs:
            row = occ[o].sum(1, keepdims=True)
            self._occ[o] = (occ[o] + 1e-3) / np.maximum(1e-9, row + 1e-3 * len(self.candidates))
            # move prob per minute in this week-bucket
            samples_per_bin = np.maximum(1e-9, occ[o].sum(1))
            self._leave[o] = moves[o] / (samples_per_bin * GRID_MIN)
        self._fitted = True

    def occupancy(self, object_id: str, receptacle_id: str, t: int) -> float:
        v = self._occ.get(object_id)
        if v is None:
            return 1.0 / len(self.candidates)
        return float(v[(t % MIN_PER_WEEK) // GRID_MIN, self._idx[receptacle_id]])

    def rate(self, object_id: str, receptacle_id: str, t: int) -> float:
        v = self._leave.get(object_id)
        if v is None:
            return 0.0
        return float(v[(t % MIN_PER_WEEK) // GRID_MIN])

    def estimator_for(self, object_id: str) -> str:
        return "oracle_marginal"


class C5Particle:
    """C5+ — particle / trajectory oracle: the TRUE information-theoretic ceiling.

    Samples N full trajectories from the generator and, for a query, keeps the
    trajectories in which the queried object was at its last-observed receptacle
    at the last-observation time; the posterior over the object's location at
    the query time is read from the survivors. Because it uses the ACTUAL
    generator it captures CONDITIONAL dependence the marginal oracle (C5Marginal)
    cannot -- the dish cycle ('plate in sink at 21:30 -> cupboard at 21:45'),
    carry-chains, and branch correlations -- automatically.

    With no conditioning observation (D=0 / held-out) the posterior IS the
    marginal, so C5+ gracefully reduces to C5Marginal there. Falls back to the
    marginal when too few particles survive the match (logged via `used`).
    """
    name = "C5plus_particle"

    GRID = 30    # minutes per state-grid bin (vectorized lookup)

    def __init__(self, profile: Profile, candidates: list[str],
                 n_particles: int = 2500, n_days: int = 30, seed0: int = 90_000,
                 min_survivors: int = 40):
        self.profile = profile
        self.candidates = list(candidates)
        self._idx = {c: i for i, c in enumerate(candidates)}
        self.el = self._idx["elsewhere"]
        self.n_particles, self.n_days, self.seed0 = n_particles, n_days, seed0
        self.min_survivors = min_survivors
        self._grid = None                    # int16 [n_particles, n_obj, n_bins]
        self._objpos: dict[str, int] = {}
        self._marginal = C5Marginal(profile, candidates, n_sims=150, n_days=n_days)
        self.used = "particle"

    def fit(self, observation_history=None) -> None:
        if self._grid is not None:
            return
        self._marginal.fit([])
        objs = sorted(self.profile.placements)
        self._objpos = {o: i for i, o in enumerate(objs)}
        nb = (self.n_days * MIN_PER_DAY) // self.GRID
        grid = np.empty((self.n_particles, len(objs), nb), dtype=np.int16)
        homes = np.array([self._idx.get(self.profile.placements[o].home, self.el) for o in objs])
        for s in range(self.n_particles):
            events, _sn, _m = simulate(self.profile, n_days=self.n_days, seed=self.seed0 + s)
            cur = homes.copy()
            evs = sorted(events, key=lambda e: e["t_min"])
            k = 0
            for b in range(nb):
                t = b * self.GRID
                while k < len(evs) and evs[k]["t_min"] <= t:
                    e = evs[k]
                    cur[self._objpos[e["label"]]] = self._idx.get(e["parent_label"], self.el)
                    k += 1
                grid[s, :, b] = cur
        self._grid = grid

    def _bin(self, t):
        return min(self._grid.shape[2] - 1, int(t) // self.GRID)

    def predict_belief(self, obj: str, r_last, t_last, t_query: int) -> dict:
        """Posterior over obj at t_query conditioned on the last observation
        (obj at r_last at ~t_last). None r_last -> marginal. Vectorized."""
        if r_last is None or t_last is None or obj not in self._objpos:
            self.used = "marginal_no_obs"
            return {c: self._marginal.occupancy(obj, c, t_query) for c in self.candidates}
        oi = self._objpos[obj]
        col_last = self._grid[:, oi, self._bin(t_last)]
        col_q = self._grid[:, oi, self._bin(t_query)]
        mask = col_last == self._idx.get(r_last, -1)
        if mask.sum() < self.min_survivors:      # widen +-1 bin
            b = self._bin(t_last)
            wide = np.zeros(self._grid.shape[0], dtype=bool)
            for bb in (b - 1, b, b + 1):
                if 0 <= bb < self._grid.shape[2]:
                    wide |= (self._grid[:, oi, bb] == self._idx.get(r_last, -1))
            mask = wide
        if mask.sum() < self.min_survivors:      # fall back to the marginal
            self.used = "marginal_fallback"
            return {c: self._marginal.occupancy(obj, c, t_query) for c in self.candidates}
        self.used = "particle"
        counts = np.bincount(col_q[mask], minlength=len(self.candidates)).astype(float)
        counts = counts + 1e-3
        counts /= counts.sum()
        return {c: float(counts[i]) for i, c in enumerate(self.candidates)}

    def estimator_for(self, object_id: str) -> str:
        return self.used


C5Marginal = C5Oracle  # the marginal ceiling (C5+ = C5Particle is the true ceiling)
