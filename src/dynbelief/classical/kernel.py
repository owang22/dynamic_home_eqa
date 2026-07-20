"""Transition-kernel classical arm (K1/K2/K3) — replaces the marginal arms C1-C4.

The diagnosis those arms failed on: a marginal-occupancy model discards the
SOURCE receptacle when it propagates, so it is indistinguishable from
last-observation parroting on top-1. The kernel conditions on where the object
was last seen.

Model (discrete-time transition probabilities — no rates, no continuous time):
  time bin b = (hour_of_day // bin_hours, is_weekend); default bin_hours=4 ->
  6 dayparts x {weekday, weekend} = 12 bins (1h/2h are reported but unusable at
  this observation cadence, ~7h between snapshots -> see the discard diagnostic).
  States = the R tracked receptacles + `elsewhere`.
  Per object CLASS c (instances pooled for volume):
      A_c,b[i,j] = P(state j at end of bin b | state i at start of bin b)

Learning is COUNTING, not EM (observations are noiseless -> observed state is
not hidden). Only consecutive observation pairs exactly ONE absolute bin apart
are counted; the discarded-pair fraction is logged (if >50%, bins are too
narrow for the schedule).

Backoff (sparsity is the main risk): hierarchical Dirichlet cascade
  L0 (class,bin,source) <- L1 (class,daypart,weekend,source) <- L2 (class,source)
  <- L3 (class) <- L4 uniform; each coarser level is the prior mean for the
  finer, pseudo-count m. The deepest level with >= m counts is logged per
  prediction (`backoff_level`).

Prediction: belief starts as a point mass on the last observed receptacle and
is multiplied forward through each elapsed bin's kernel -- the shared Bayes
filter with a source-conditioned transition operator.

Injection (K2 LLM prior / K3 oracle prior): row-wise Dirichlet pseudo-counts
  A_hat_row = (kappa * q_row + n_row) / (kappa + sum_k n_row[k])
kappa = equivalent sample size in OBSERVED TRANSITIONS. A zero-count row returns
exactly q; a row with kappa observed transitions returns the midpoint (both
unit-tested). q is elicited at daypart granularity and expanded to bins.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.profiles.schema import default_class

DAYPART_HOURS = 4                      # L1 daypart width (fixed, 6 dayparts)


def is_weekend(t: int) -> int:
    return int((t // MIN_PER_DAY) % 7 >= 5)


class KernelModel:
    name = "K_kernel"

    def __init__(self, candidates: list[str], bin_hours: int = 4,
                 backoff_m: float = 5.0, prior_q: dict | None = None,
                 kappa: float = 0.0):
        self.candidates = list(candidates)
        self.R = len(candidates)
        self._idx = {c: i for i, c in enumerate(candidates)}
        self.el = self._idx["elsewhere"]
        self.bin_hours = int(bin_hours)
        self.bins_per_day = 24 // self.bin_hours
        self.n_bins = self.bins_per_day * 2          # x{weekday,weekend}
        self.m = float(backoff_m)
        self.q = prior_q or {}                       # (class,daypart,wknd,src)->np.array
        self.kappa = float(kappa)
        # counts
        self._n0 = defaultdict(lambda: np.zeros(self.R))   # (cls,bin,src)->dest
        self._n1 = defaultdict(lambda: np.zeros(self.R))   # (cls,daypart,wknd,src)
        self._n2 = defaultdict(lambda: np.zeros(self.R))   # (cls,src)
        self._n3 = defaultdict(lambda: np.zeros(self.R))   # (cls)
        self.discarded = 0
        self.kept = 0

    # ── binning ───────────────────────────────────────────────────────────────
    def _cyclic_bin(self, t: int) -> int:
        h = (t % MIN_PER_DAY) // 60
        return int((h // self.bin_hours) + self.bins_per_day * is_weekend(t))

    def _daypart(self, t: int) -> int:
        h = (t % MIN_PER_DAY) // 60
        return int(h // DAYPART_HOURS)

    def _abs_bin(self, t: int) -> int:
        return int(t // (self.bin_hours * 60))

    # ── learning (counting) ─────────────────────────────────────────────────────
    def fit(self, observation_history: list[dict]) -> None:
        rows = sorted(observation_history, key=lambda r: r["t_min"])
        prev: dict[str, tuple[int, str]] = {}
        for r in rows:
            for o, rec in r["parents"].items():
                if o in prev:
                    t1, s1 = prev[o]
                    t2, s2 = r["t_min"], rec
                    if s1 in self._idx and s2 in self._idx:
                        if self._abs_bin(t2) == self._abs_bin(t1) + 1:   # exactly 1 bin apart
                            cls = default_class(o)
                            j = self._idx[s2]
                            self._n0[(cls, self._cyclic_bin(t1), s1)][j] += 1
                            self._n1[(cls, self._daypart(t1), is_weekend(t1), s1)][j] += 1
                            self._n2[(cls, s1)][j] += 1
                            self._n3[(cls,)][j] += 1
                            self.kept += 1
                        else:
                            self.discarded += 1
                prev[o] = (r["t_min"], rec)

    @property
    def discard_frac(self) -> float:
        tot = self.kept + self.discarded
        return self.discarded / tot if tot else float("nan")

    # ── one kernel row + the level that supplied it ─────────────────────────────
    def _row(self, cls: str, t: int, src: str):
        wk, dp, cb = is_weekend(t), self._daypart(t), self._cyclic_bin(t)
        uni = np.full(self.R, 1.0 / self.R)
        n3 = self._n3.get((cls,))
        est3 = ((n3 + self.m * uni) / (n3.sum() + self.m)) if n3 is not None else uni
        n2 = self._n2.get((cls, src))
        est2 = ((n2 + self.m * est3) / (n2.sum() + self.m)) if n2 is not None else est3
        # injection: if an elicited/oracle q row exists, it is THE prior (Dirichlet
        # pseudo-counts), bypassing the coarser backoff for this row.
        qrow = self.q.get((cls, dp, wk, src))
        n0 = self._n0.get((cls, cb, src))
        n0sum = n0.sum() if n0 is not None else 0.0
        if qrow is not None and self.kappa > 0:
            base = n0 if n0 is not None else np.zeros(self.R)
            row = (self.kappa * qrow + base) / (self.kappa + n0sum)
            return row / row.sum(), "prior_injected"
        # K1 backoff cascade L1 <- L0
        n1 = self._n1.get((cls, dp, wk, src))
        est1 = ((n1 + self.m * est2) / (n1.sum() + self.m)) if n1 is not None else est2
        if n0 is not None:
            row = (n0 + self.m * est1) / (n0sum + self.m)
            level = "L0_bin" if n0sum >= self.m else ("L1_daypart" if (n1 is not None and n1.sum() >= self.m) else "L2plus")
            return row / row.sum(), level
        if n1 is not None and n1.sum() >= self.m:
            return est1, "L1_daypart"
        if n2 is not None and n2.sum() >= self.m:
            return est2, "L2_classsrc"
        if n3 is not None and n3.sum() >= self.m:
            return est3, "L3_class"
        return uni, "L4_uniform"

    def kernel_matrix(self, cls: str, t: int):
        """Full R x R transition matrix for class cls at bin(t): row i = _row from
        source candidates[i]."""
        A = np.zeros((self.R, self.R))
        lv = None
        for i, src in enumerate(self.candidates):
            A[i], lv = self._row(cls, t, src)
        return A

    # ── prediction: matrix product from the last observation ────────────────────
    def predict_belief(self, obj: str, r_last, t_last, t_query: int):
        if r_last is None or t_last is None or r_last not in self._idx:
            b = np.full(self.R, 1.0 / self.R)
            return {c: float(b[i]) for i, c in enumerate(self.candidates)}, "no_obs"
        cls = default_class(obj)
        b = np.zeros(self.R); b[self._idx[r_last]] = 1.0
        step = self.bin_hours * 60
        t = int(t_last)
        last_level = "same_bin"
        # advance to the end of the current bin, then bin by bin to the query bin
        while self._abs_bin(t) < self._abs_bin(t_query):
            A_row_src = self.candidates[int(np.argmax(b))]  # (level logged from dominant source)
            A = self.kernel_matrix(cls, t)
            b = b @ A
            _, last_level = self._row(cls, t, A_row_src)
            t += step
        s = b.sum()
        b = b / s if s > 0 else np.full(self.R, 1.0 / self.R)
        return {c: float(b[i]) for i, c in enumerate(self.candidates)}, last_level

    def estimator_for(self, object_id: str) -> str:
        return "kernel"
