"""Household A as the question scripts see it: snapshots, fixed spot views, rendered pictures
and what each picture truly shows.

    W = World()
    W.states[(day, "HHMM")]          the snapshot (positions_HHMM.json)
    W.views[spot]                    the fixed robot viewpoint of an open spot
    W.furniture[key] -> [spots]      key = "room|furniture"; only spots with a view
    W.truth(day, hhmm) -> {spot: {oid: pixels}}   objects drawn in each spot's picture
    W.picture(day, hhmm, spot) -> path of the jpg
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import random
import sys

REPO = pathlib.Path("/home/oliver/robot/dynamic_home_eqa")
sys.path.insert(0, str(REPO / "3d_rendering/src"))
from lived_home import play  # noqa: E402

RUN = REPO / "3d_rendering/results/lived_home/hssd_a"
RENDER = REPO / "3d_rendering/results/vlm_night/render"
PICS = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a")
VERDICTS = REPO / "3d_rendering/results/render_methods/habitat_hssd/checks/model_verdicts.json"

PATROL_TIMES = ["0800", "1200", "1600", "2000"]
QUESTION_TIMES = ["1000", "1400", "1800", "2200"]
NOTE_PX = 300      # a patrol note lists a thing when it covers at least this many pixels
FIND_PX = 500      # a question is asked only when the thing covers this many pixels somewhere


class World:
    def __init__(self):
        self.spec, self.states = play.load(RUN)
        sv = json.loads((RENDER / "spot_views.json").read_text())
        self.views = {v["spot"]: v for v in sv["views"]}
        places = next(iter(self.states.values()))["places"]
        self.places = places
        self.furniture = collections.defaultdict(list)
        for spot in self.views:
            self.furniture[self.fkey(spot)].append(spot)
        self.objects = {o["id"]: o for o in self.spec["objects"]}
        verdicts = json.loads(VERDICTS.read_text())["types"]
        self.verdict = {t: v["verdict"] for t, v in verdicts.items()}
        self.type_count = collections.Counter(o["type"] for o in self.objects.values())
        self._truth = {}

    def fkey(self, spot: str) -> str:
        p = self.places[spot]
        return f"{p['room']}|{p['furniture']}"

    def fname(self, key: str) -> str:
        room, furn = key.split("|")
        return f"{furn} ({room.replace('_', ' ')})"

    def rooms(self) -> list:
        return sorted({self.places[s]["room"] for s in self.views})

    def picture(self, day: int, hhmm: str, spot: str) -> pathlib.Path:
        return PICS / f"day_{day:02d}" / hhmm / f"{spot}.jpg"

    def truth(self, day: int, hhmm: str) -> dict:
        """{spot: {oid: pixels}} for every viewed spot at that time."""
        k = (day, hhmm)
        if k not in self._truth:
            f = PICS / f"day_{day:02d}" / hhmm / "truth.json"
            data = json.loads(f.read_text())
            objs = self.states[k]["objects"]
            out = {}
            for spot, rec in data["pictures"].items():
                # only things placed on this piece of furniture: a chair-seat picture that also
                # shows the table's bowls does not count the bowls as on the chair
                f = self.fkey(spot)
                out[spot] = {o["object"]: o["pixels"] for o in rec["objects"]
                             if objs[o["object"]].get("place") in self.places
                             and self.fkey(objs[o["object"]]["place"]) == f}
            self._truth[k] = out
        return self._truth[k]

    def raw_truth(self, day: int, hhmm: str) -> dict:
        """{spot: {oid: pixels}} for everything drawn in each picture, whatever it rests on."""
        k = ("raw", day, hhmm)
        if k not in self._truth:
            data = json.loads((PICS / f"day_{day:02d}" / hhmm / "truth.json").read_text())
            self._truth[k] = {spot: {o["object"]: o["pixels"] for o in rec["objects"]}
                              for spot, rec in data["pictures"].items()}
        return self._truth[k]

    def rendered(self, day: int, hhmm: str) -> bool:
        return (PICS / f"day_{day:02d}" / hhmm / "truth.json").exists()

    def seen_at(self, day, hhmm, px=NOTE_PX) -> dict:
        """{furniture key: set(oid)} with at least px pixels in one of its pictures."""
        out = collections.defaultdict(set)
        for spot, objs in self.truth(day, hhmm).items():
            for oid, n in objs.items():
                if n >= px:
                    out[self.fkey(spot)].add(oid)
        return out

    def patrol_plan(self, seed=0) -> list:
        if not hasattr(self, "_plans"):
            self._plans = {}
        if seed not in self._plans:
            self._plans[seed] = self._patrol_plan(seed)
        return self._plans[seed]

    def _patrol_plan(self, seed=0) -> list:
        """[(day, hhmm, [rooms])]: each patrol walks about a third of the rooms in a
        shuffled cycle, so every room is seen at least once every three patrols."""
        rng = random.Random(seed)
        rooms = self.rooms()
        per = max(3, math.ceil(len(rooms) / 3))
        out, cycle = [], []
        for day in sorted({d for d, _ in self.states}):
            for t in PATROL_TIMES:
                if (day, t) not in self.states:
                    continue
                if len(cycle) < per:
                    more = list(rooms)
                    rng.shuffle(more)
                    cycle += [r for r in more if r not in cycle]
                visit, cycle = cycle[:per], cycle[per:]
                out.append((day, t, visit))
        return out

    def furniture_xz(self) -> dict:
        out = {}
        for key, spots in self.furniture.items():
            pts = [self.views[s]["middle_of_surface"] for s in spots]
            out[key] = (sum(p[0] for p in pts) / len(pts), sum(p[2] for p in pts) / len(pts))
        return out
