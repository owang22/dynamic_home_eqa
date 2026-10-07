"""Where every asked-about thing and every resident is, at any moment of the run.

Read from the bank (the truth), then given a fixed spot on the furniture for
as long as the thing stays at that place, so it does not jump about between
two pictures of the same hour.
"""
from __future__ import annotations

import bisect
import json
import pathlib
from typing import Dict, List, Optional

import numpy as np

from rendered_look.world import steady_number

DAY = 86400


class Bank:
    def __init__(self, path: pathlib.Path) -> None:
        self.header: dict = {}
        self.moves: Dict[str, List[dict]] = {}
        self.whereabouts: Dict[str, List[dict]] = {}
        self.questions: List[dict] = []
        with path.open() as rows:
            for line in rows:
                row = json.loads(line)
                if row["kind"] == "episode_header":
                    self.header = row
                elif row["kind"] == "truth":
                    self.moves.setdefault(row["object_id"], []).append(row)
                elif row["kind"] == "resident":
                    self.whereabouts.setdefault(row["resident_id"], []).append(row)
                elif row["kind"] == "question":
                    self.questions.append(row)
        for rows in list(self.moves.values()) + list(self.whereabouts.values()):
            rows.sort(key=lambda r: r["t"])
        self.asked = sorted({q["object_id"] for q in self.questions})
        self.rooms = self.header["receptacle_rooms"]

    def stage_of_day(self, day: int) -> str:
        stages = self.header.get("stages")
        if isinstance(stages, list) and day < len(stages):
            return stages[day] if isinstance(stages[day], str) else str(stages[day])
        if isinstance(stages, dict):
            return str(stages.get(str(day), stages.get(day, "")))
        return ""

    def room_of_resident(self, resident: str, t: int) -> dict:
        rows = self.whereabouts[resident]
        i = bisect.bisect_right([r["t"] for r in rows], t) - 1
        return rows[max(i, 0)]


class Stays:
    """Every stay of every asked-about thing at a place, with its spot on the furniture."""

    def __init__(self, bank: Bank, world) -> None:
        self.bank, self.world = bank, world
        self.stays: Dict[str, List[dict]] = {}
        arrivals = []
        for object_id in bank.asked:
            rows = bank.moves.get(object_id, [])
            for i, row in enumerate(rows):
                until = rows[i + 1]["t"] if i + 1 < len(rows) else 10 ** 12
                if i and rows[i - 1]["receptacle_id"] == row["receptacle_id"]:
                    self.stays[object_id][-1]["until"] = until  # still there
                    continue
                stay = {"object_id": object_id, "place": row["receptacle_id"], "from": row["t"],
                        "until": until, "cause": row.get("cause", "")}
                self.stays.setdefault(object_id, []).append(stay)
                arrivals.append(stay)
        arrivals.sort(key=lambda s: (s["from"], s["object_id"]))
        here: Dict[str, List[dict]] = {}
        for stay in arrivals:
            others = [s for s in here.get(stay["place"], []) if s["until"] > stay["from"]]
            self._give_a_spot(stay, others)
            here[stay["place"]] = others + [stay]

    def _give_a_spot(self, stay: dict, others: List[dict]) -> None:
        place = stay["place"]
        spec = self.world.binding.PLACES.get(place)
        if spec is None or place not in self.world.surfaces:
            stay["shown"] = False
            stay["why_not_shown"] = (
                "carried by a person" if place == "ON_PERSON" else
                "out of the house" if place == "OUT_OF_HOUSE" else
                f"inside the {spec['called']}, which is closed" if spec and spec["kind"] == "enclosed" else
                (spec or {}).get("stand_in") or self.world.place_problems.get(place, "no furniture for this place"))
            return
        surface = self.world.surfaces[place]
        facts = self.world.thing_facts[stay["object_id"]]
        radius = facts["radius"]
        taken = [(s["x"], s["z"], self.world.thing_facts[s["object_id"]]["radius"])
                 for s in others if s.get("shown")]
        usable = np.ones(len(surface.xz), dtype=bool)
        if "head_toward" in spec:  # a bed: things go on the half nobody lies on
            head = np.array(spec["head_toward"], dtype=float)
            across = np.array([-head[1], head[0]])
            middle = surface.xz.mean(axis=0)
            usable = (surface.xz - middle) @ across < -0.15
        gap = np.full(len(surface.xz), np.inf)
        for x, z, r in taken:
            gap = np.minimum(gap, np.hypot(surface.xz[:, 0] - x, surface.xz[:, 1] - z) - r - radius - 0.02)
        fits_edge = surface.clearance >= min(radius * 1.1, surface.clearance.max() * 0.9)
        good = fits_edge & (gap >= 0) & usable
        stay["crowded"] = not good.any()
        under = [s for s in others if s.get("shown") and self.world.thing_facts[s["object_id"]]["stacks"]]
        if not good.any() and facts["stacks"] and under:
            # share the spot of the widest flat thing already here; which one is
            # on top is worked out at each moment, from who is still there
            below = max(under, key=lambda s: self.world.thing_facts[s["object_id"]]["radius"])
            stay.update(shown=True, x=below["x"], z=below["z"], y=below["y"], yaw=below["yaw"] + 0.2,
                        overhangs=below.get("overhangs", False))
            return
        if good.any():
            choices = np.flatnonzero(good)
            pick = choices[int(steady_number(stay["object_id"], place, stay["from"]) * len(choices))]
        else:  # nowhere free: the spot farthest from everything else, as far from the edge as it gets
            score = np.where(np.isfinite(gap), gap, 1.0) + surface.clearance + np.where(usable, 0, -5)
            pick = int(np.argmax(score))
        x, z = surface.xz[pick]
        quarter = int(steady_number("turn", stay["object_id"], place, stay["from"]) * 4)
        lean = (steady_number("lean", stay["object_id"], place, stay["from"]) - 0.5) * 0.5
        stay.update(shown=True, x=float(x), z=float(z),
                    y=surface.height_under(float(x), float(z), radius * 0.7),
                    yaw=quarter * np.pi / 2 + lean,
                    overhangs=bool(surface.clearance[pick] < radius * 0.6))

    def at(self, object_id: str, t: int) -> Optional[dict]:
        for stay in self.stays.get(object_id, []):
            if stay["from"] <= t < stay["until"]:
                return stay
        return None
