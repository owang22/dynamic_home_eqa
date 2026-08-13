"""FreMEn baseline: spectral occupancy model per (object, receptacle).

Derived from Krajnik et al., "FreMEn: Frequency Map Enhancement for
Long-Term Mobile Robot Autonomy in Changing Environments" (IEEE T-RO
2017; reference implementation gestom/FreMEn). Each binary state s(t) —
"object o is inside receptacle r" — is modelled by its mean plus the n
highest-amplitude frequency components of its history:

    p(t) = clamp( a0 + sum_j |a_j| * cos(omega_j * t - phi_j), 0, 1 )

fitted by projecting the history onto a candidate frequency set and
keeping the n components with the largest amplitude, exactly the paper's
order-selection scheme; n is a constructor argument, default 2, recorded
in the results provenance.

Deviations from the paper, with reasons:

1. **Complete state, not sparse visits.** The paper's setting is a robot
   that OBSERVES a cell only when it visits; its incremental spectral
   update handles irregular sampling. HOMER+ gives complete piecewise-
   constant state, so the history is sampled EXACTLY on a regular 10-min
   grid (the dataset's own dt) with no missing entries — uniform
   projection is exact here, and the reference implementation's
   non-uniform machinery has nothing to do. This is a property of the
   dataset, not a shortcut: there is no observation gap to handle.
   (The synthetic validation still exercises gaps by masking, to prove
   the projection itself is sound — see tests/test_fremen_synthetic.py.)
2. **Candidate frequencies** are the paper's harmonic set: periods
   T = 24h / k for k = 1..H (H = 48, down to 30-min cycles) plus the
   7-day period and its harmonics. HOMER+ days are sampled schedule
   variations with no weekday structure, so the weekly components are
   expected to carry ~no amplitude — they are INCLUDED so the data can
   say so rather than the code assuming it; the recovered spectra are
   saved per household for inspection (reports/homer_spectra/*.png).
3. **Query-time normalization.** The paper scores each cell
   independently; localization needs a distribution, so the per-
   receptacle probabilities are normalized across receptacles at query
   time (floor 1e-6 before normalizing, so a receptacle never seen for
   this object keeps negligible but nonzero mass).

Held-out fallback: a held-out object has no history to transform; FreMEn
falls back to the Modal fallback distribution (initial placement blended
with pooled popularity), the same fallback every per-object model shares
so E2 differences between them come from the model, not the fallback.
"""

from __future__ import annotations

import collections
import math
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from homer.baselines import Distribution, Modal, _norm

MIN_PER_DAY = 1440
GRID_MIN = 10.0                       # HOMER+'s own dt
DAY_HARMONICS = 48                    # periods 24h/k, k=1..48
WEEK_HARMONICS = 6                    # periods 7d/k, k=1..6


def candidate_omegas() -> np.ndarray:
    periods = [MIN_PER_DAY / k for k in range(1, DAY_HARMONICS + 1)]
    periods += [7 * MIN_PER_DAY / k for k in range(1, WEEK_HARMONICS + 1)]
    return 2.0 * math.pi / np.asarray(sorted(set(periods), reverse=True))


class Spectral:
    """One binary series -> mean + top-n components (paper's model)."""

    def __init__(self, order: int = 2) -> None:
        self.order = order
        self.a0 = 0.0
        self.components: List[Tuple[float, float, float]] = []  # w, amp, phi

    def fit(self, t_min: np.ndarray, s: np.ndarray) -> "Spectral":
        self.a0 = float(s.mean())
        resid = s - self.a0
        # Nyquist guard: a candidate whose period is at or below twice the
        # sampling step is indistinguishable from a constant on this grid
        # (a 1 h cosine sampled hourly is identically 1), so its projection
        # absorbs spurious amplitude. First observed without this guard:
        # the "dominant" periods on hourly occupancy came out as 1.0 h and
        # 0.5 h — pure aliasing, not behaviour.
        step = float(np.median(np.diff(np.sort(t_min)))) or 1.0
        omegas = candidate_omegas()
        omegas = omegas[2.0 * math.pi / omegas > 2.0 * step]
        amps = np.empty(len(omegas))
        phis = np.empty(len(omegas))
        for i, w in enumerate(omegas):
            # Projection of the residual onto e^{-iwt}; with uniform,
            # complete sampling this is the DFT coefficient at w.
            c = (resid * np.exp(-1j * w * t_min)).mean()
            amps[i] = 2.0 * abs(c)
            phis[i] = math.atan2(c.imag, c.real)
        keep = np.argsort(amps)[::-1][:self.order]
        self.components = [(float(omegas[i]), float(amps[i]), float(phis[i]))
                           for i in keep]
        return self

    def p(self, t_min: float) -> float:
        v = self.a0 + sum(a * math.cos(w * t_min + phi)
                          for w, a, phi in self.components)
        return min(1.0, max(0.0, v))

    def spectrum(self) -> List[Tuple[float, float]]:
        """(period_minutes, amplitude) for every candidate — for plots."""
        omegas = candidate_omegas()
        out = []
        for w in omegas:
            match = [a for (w2, a, _) in self.components
                     if abs(w2 - w) < 1e-12]
            out.append((2.0 * math.pi / w, match[0] if match else 0.0))
        return out


class Fremen:
    """The localization baseline: one Spectral model per (object,
    receptacle) the object was ever seen in, normalized across
    receptacles at query time."""

    name = "fremen"

    def __init__(self, order: int = 2) -> None:
        self.order = order

    def fit(self, occupancy: Mapping[str, List[Dict[int, str]]],
            receptacles: Sequence[str], initial: Mapping[str, str],
            heldout: Sequence[str]) -> None:
        self._fallback = Modal()
        self._fallback.fit(occupancy, receptacles, initial, heldout)
        self._models: Dict[str, Dict[str, Spectral]] = {}
        self._heldout = set(heldout)
        for obj, days in occupancy.items():
            if obj in heldout:
                continue
            # Rebuild the regular grid from the hourly occupancy (states
            # are piecewise-constant; the hourly grid IS the state).
            t_list: List[float] = []
            series: Dict[str, List[float]] = collections.defaultdict(list)
            support = sorted({rec for byhour in days
                              for rec in byhour.values()})
            for day, byhour in enumerate(days):
                for hour in sorted(byhour):
                    t = day * MIN_PER_DAY + hour * 60.0
                    t_list.append(t)
                    for rec in support:
                        series[rec].append(1.0 if byhour[hour] == rec
                                           else 0.0)
            t_arr = np.asarray(t_list)
            self._models[obj] = {
                rec: Spectral(self.order).fit(t_arr, np.asarray(series[rec]))
                for rec in support}

    def predict(self, object_id: str, t: float) -> Distribution:
        if object_id in self._heldout or object_id not in self._models:
            return self._fallback.predict(object_id, t)
        # Query time is minutes from midnight of a test day; the daily
        # harmonics are invariant to which day, and the weekly ones carry
        # ~zero amplitude on this data (verified in the spectra plots), so
        # the phase origin does not matter for prediction.
        probs = {rec: max(m.p(t), 1e-6)
                 for rec, m in self._models[object_id].items()}
        return _norm(probs)
