"""Stage 1.3 — symbolic answerer.

"Symbolic" because we generated the questions and kept their structured
form: mapping a question type to a belief query needs no language model.

  location_now  belief.predict(t_query)[obj]; pick the option receptacle
                with the highest mass.
  room_now      aggregate that distribution's mass by room (ReplayWorld.
                room_of; ELSEWHERE maps to the "elsewhere" pseudo-room);
                pick the option room with the highest mass.
  count_now     expected count = sum of belief mass on receptacles in
                {room} across the class's instances; round, then pick the
                nearest numeric option.

Returns the chosen option index. Ties break toward the lowest index —
deterministic, and unbiased because option order is already shuffled with a
balanced correct position (generate.py).
"""
from __future__ import annotations

import numpy as np

from dynbelief import ELSEWHERE_ID
from dynbelief.beliefs.base import object_class


def _room_mass(world, dist: np.ndarray) -> dict[str, float]:
    mass: dict[str, float] = {}
    for rid, p in enumerate(dist):
        if p <= 0:
            continue
        room = "elsewhere" if rid == ELSEWHERE_ID else (world.room_of(rid) or "elsewhere")
        mass[room] = mass.get(room, 0.0) + float(p)
    return mass


def answer(world, belief, question: dict) -> int:
    t_query = question["t_query"]
    qtype = question["type"]
    if qtype == "location_now":
        dist = belief.predict(t_query)[question["target_obj"]]
        scores = [float(dist[opt]) if opt < len(dist) else 0.0
                  for opt in question["options"]]
        return int(np.argmax(scores))
    if qtype == "room_now":
        dist = belief.predict(t_query)[question["target_obj"]]
        mass = _room_mass(world, dist)
        scores = [mass.get(opt, 0.0) for opt in question["options"]]
        return int(np.argmax(scores))
    if qtype == "count_now":
        cls = question["count_class"]
        room = question["count_room"]
        preds = belief.predict(t_query)
        expected = 0.0
        room_receps = [r for r in world.receptacles() if world.room_of(r) == room]
        for obj, dist in preds.items():
            if object_class(world.obj_label[obj]) != cls:
                continue
            expected += float(sum(dist[r] for r in room_receps if r < len(dist)))
        rounded = round(expected)
        diffs = [abs(opt - rounded) for opt in question["options"]]
        return int(np.argmin(diffs))
    raise ValueError(qtype)
