"""A memory of MODES: the household is in one of several regimes, and the robot infers which.

No language model anywhere. This is the missing baseline between LastSeen - which holds one trail
per object and cannot represent "things are different this week" - and a written memory, which can
say it but has to be asked to. A mode model can represent the shift without being told and without
being able to write anything down.

THE MODEL, exactly as specified:

  modes           a list, starting with one. Each holds counts[object][room] with a Dirichlet
                  prior of 0.5 on every room, so an unseen room in a seen object keeps a floor.
  a day's home    at the end of each day the day's sightings are assigned to ONE mode, hard, by a
                  Chinese restaurant process: existing mode k is weighted by the number of days
                  already assigned to it, a brand-new empty mode by alpha. The day's counts go to
                  the winner, and a new mode is created if the new mode wins.
  within a day    a posterior over modes, started from yesterday's mode with a stay probability
                  and the rest spread over the other modes AND a new one, updated after every
                  sighting made today.
  choosing        rank rooms by P(room | object) = sum over modes of P(mode) P(room | object, mode).
  unseen objects  fall back to the LastSeen rule, because a mode model has nothing to say about an
                  object it has never seen and a uniform guess would be worse than the trail.

The two knobs are alpha and the stay probability. They are NOT tuned against the outcome: the
driver reports the whole grid.
"""
from __future__ import annotations

import collections
import math
from typing import Dict, List, Optional, Sequence, Tuple

PRIOR = 0.5


class Mode:
    """One regime: how often each object has been seen in each room, while this regime held."""

    def __init__(self, rooms: Sequence[str]) -> None:
        self.rooms = list(rooms)
        self.counts: Dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        self.days = 0

    def knows(self, object_id: str) -> bool:
        return bool(self.counts.get(object_id))

    def probability_of(self, object_id: str, room: str) -> float:
        counts = self.counts.get(object_id)
        floor = PRIOR * len(self.rooms)
        if not counts:
            return 1.0 / len(self.rooms)
        return (counts.get(room, 0) + PRIOR) / (sum(counts.values()) + floor)

    def add(self, sightings: Sequence[Tuple[str, str]]) -> None:
        for object_id, room in sightings:
            self.counts[object_id][room] += 1
        self.days += 1


class HouseholdModes:
    """The memory. One of these per household, alive for the whole month."""

    def __init__(self, rooms: Sequence[str], alpha: float = 1.0,
                 stay: float = 0.9) -> None:
        self.rooms = list(rooms)
        self.alpha = alpha
        self.stay = stay
        self.modes: List[Mode] = [Mode(rooms)]
        self.yesterday = 0
        self.belief: List[float] = [1.0]
        self.history: List[Tuple[int, int]] = []          # (day, which mode took the day)

    # ---- within a day -------------------------------------------------------------
    def start_the_day(self) -> None:
        """Yesterday's mode keeps `stay`; the rest is split over the others and a new one."""
        others = len(self.modes) - 1 + 1                   # the other modes, plus a new one
        spread = (1.0 - self.stay) / max(1, others)
        self.belief = [spread] * len(self.modes) + [spread]      # last slot = a mode not yet made
        self.belief[self.yesterday] = self.stay
        total = sum(self.belief)
        self.belief = [b / total for b in self.belief]

    def saw(self, object_id: str, room: str) -> None:
        """One sighting made today moves the posterior over modes."""
        weights = [b * self.probability(i, object_id, room)
                   for i, b in enumerate(self.belief)]
        total = sum(weights)
        if total > 0:
            self.belief = [w / total for w in weights]

    def probability(self, index: int, object_id: str, room: str) -> float:
        """P(room | object) under mode `index`; the last index is the not-yet-made mode."""
        if index >= len(self.modes):
            return 1.0 / len(self.rooms)
        return self.modes[index].probability_of(object_id, room)

    # ---- choosing -----------------------------------------------------------------
    def knows(self, object_id: str) -> bool:
        return any(m.knows(object_id) for m in self.modes)

    def rank(self, object_id: str, rooms_left: Sequence[str]) -> List[str]:
        scored = [(sum(b * self.probability(i, object_id, room)
                       for i, b in enumerate(self.belief)), room)
                  for room in rooms_left]
        scored.sort(key=lambda pair: (-pair[0], pair[1]))    # ties by room name, never by chance
        return [room for _, room in scored]

    # ---- the end of the day -------------------------------------------------------
    def close_the_day(self, day: int, sightings: Sequence[Tuple[str, str]]) -> int:
        """Assign the day to a mode, hard, and fold its counts in. Returns the mode."""
        if not sightings:
            self.history.append((day, self.yesterday))
            return self.yesterday
        scores = []
        for i, mode in enumerate(self.modes):
            weight = math.log(mode.days) if mode.days > 0 else math.log(self.alpha)
            scores.append(weight + sum(math.log(mode.probability_of(o, r))
                                       for o, r in sightings))
        fresh = math.log(self.alpha) + len(sightings) * math.log(1.0 / len(self.rooms))
        scores.append(fresh)
        best = max(range(len(scores)), key=lambda i: scores[i])
        if best == len(self.modes):
            self.modes.append(Mode(self.rooms))
        self.modes[best].add(sightings)
        self.yesterday = best
        self.history.append((day, best))
        return best
