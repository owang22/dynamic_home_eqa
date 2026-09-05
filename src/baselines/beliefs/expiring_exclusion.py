"""LastObs with negative evidence that lapses.

The base class's exclusion never ages: once a visit finds the last-seen
receptacle empty, that receptacle stays ruled out until the object's next
positive sighting, which at long ages never comes. The rate sweep showed
this is what turns LastObs into "answer OUT_OF_HOUSE" a day after the
last sighting. This variant is the cheap comparator to the survival
models' emergence machinery: an exclusion recorded at ``t_ex`` is honoured
for ``expiry_h`` hours and then forgotten, so the object is allowed to
have come back. Nothing else changes -- the same one-hot last-sighting
belief, the same reclaimed-mass rule.
"""

from __future__ import annotations

import random
from typing import Set, Union

from baselines.beliefs.last_observation import LastObservation


class ExpiringExclusionLastObservation(LastObservation):
    """LastObs whose exclusions expire ``expiry_h`` hours after the
    inspection that recorded them."""

    def __init__(self, rng: random.Random, expiry_h: float,
                 exclusion_floor: float = 0.0) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        if expiry_h <= 0:
            raise ValueError(
                f"ExpiringExclusionLastObservation: expiry_h {expiry_h} "
                f"must be positive")
        self._expiry_s = float(expiry_h) * 3600.0
        self.expiry_h = float(expiry_h)

    @property
    def name(self) -> str:
        return f"LastObsExpiring{self.expiry_h:g}h"

    def _active_exclusions(self, object_id: str,
                           t: Union[int, None] = None) -> Set[str]:
        active = super()._active_exclusions(object_id, t)
        if t is None or not active:
            return active
        recorded = self._exclusions.get(object_id, {})
        return {rec for rec in active
                if t - recorded[rec] < self._expiry_s}
