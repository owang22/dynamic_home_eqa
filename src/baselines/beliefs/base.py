"""Belief-model interface and the observation bookkeeping every basic model
shares.

A belief model consumes the observation stream (plus any sense results the
policy pays for) and answers ``predict(object_id, t)`` with a distribution
over receptacles. All times are seconds since episode start.

Shared bookkeeping lives here so concrete models stay single-idea:
:class:`BeliefModel` maintains, per object, the chronological list of
positive sightings ``(t, receptacle_id)``. Sense results are folded in as
positive sightings of their contents; their negative information (absence
from the sensed receptacle) is intentionally dropped at this tier — the
:class:`~baselines.types.SenseResult` contract preserves it for later
model families.
"""

from __future__ import annotations

import abc
import random
from typing import Dict, List, Mapping, Tuple, Union

from baselines.types import EpisodeContext, Observation, Prediction, SenseResult


class BeliefModel(abc.ABC):
    """Base class: history bookkeeping, uniform fallback, tie-breaking.

    Concrete models implement :meth:`_predict_from_history` only. The
    seeded ``rng`` is the model's *only* source of randomness (used to
    break argmax ties, e.g. inside the uniform fallback); it is supplied
    by the harness so runs are fully determined by (bank, config, seed).
    """

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng
        self._context: EpisodeContext | None = None
        self._history: Dict[str, List[Tuple[int, str]]] = {}

    @property
    def name(self) -> str:
        """Stable identifier used in logs and result tables."""
        return type(self).__name__

    # ---------------------------------------------------------------- API

    def reset(self, context: EpisodeContext) -> None:
        """Start a fresh episode: forget all history, remember the context."""
        self._context = context
        self._history = {}

    def update(self, evidence: Union[Observation, SenseResult]) -> None:
        """Fold one piece of evidence into the history.

        An :class:`Observation` is a single positive sighting. A
        :class:`SenseResult` contributes one positive sighting per object in
        its contents; its negative information is dropped here (see module
        docstring).
        """
        if isinstance(evidence, Observation):
            self._history.setdefault(evidence.object_id, []).append(
                (evidence.t, evidence.receptacle_id))
        else:
            for obj in evidence.contents:
                self._history.setdefault(obj, []).append(
                    (evidence.t, evidence.receptacle_id))

    def predict(self, object_id: str, t: int) -> Prediction:
        """Distribution over receptacles for ``object_id`` at time ``t``.

        A never-observed object gets the uniform fallback over all
        receptacles (argmax tie broken by the seeded generator).
        """
        history = self._history.get(object_id, [])
        if not history:
            return self._uniform()
        return self._predict_from_history(history, t)

    # ------------------------------------------------------------ helpers

    @abc.abstractmethod
    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        """Predict from a non-empty chronological sighting list."""

    def _receptacles(self) -> Tuple[str, ...]:
        if self._context is None:
            raise RuntimeError(f"{self.name}: predict() before reset()")
        return self._context.receptacle_ids

    def _uniform(self) -> Prediction:
        """Uniform distribution over all receptacles; random tied argmax."""
        recs = self._receptacles()
        p = 1.0 / len(recs)
        return Prediction(distribution={r: p for r in recs},
                          argmax=self._rng.choice(list(recs)))

    def _normalized(self, counts: Mapping[str, int],
                    tie_break_recency: List[Tuple[int, str]]) -> Prediction:
        """Frequency-normalize ``counts`` into a Prediction.

        Argmax ties are broken by recency: among tied receptacles, the one
        sighted most recently in ``tie_break_recency`` wins. This is
        deterministic, so tied modal locations never consume randomness.
        """
        total = sum(counts.values())
        dist = {r: c / total for r, c in counts.items()}
        top = max(dist.values())
        tied = [r for r, p in dist.items() if p == top]
        if len(tied) == 1:
            return Prediction(distribution=dist, argmax=tied[0])
        last_seen = {rec: i for i, (_, rec) in enumerate(tie_break_recency)}
        return Prediction(distribution=dist,
                          argmax=max(tied, key=lambda r: last_seen.get(r, -1)))
