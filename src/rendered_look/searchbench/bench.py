"""The search benchmark: a policy searches for a named thing by choosing camera
positions, and pays for each look and each metre walked.

    python -m rendered_look.searchbench.bench --rig go2 --perception "in view"

Everything a look returns comes from a picture rendered beforehand
(render_positions.py), so a whole month of searches runs in seconds and every
policy sees the same pictures.

What a search is
  A question names a thing and a time. The robot starts where its last search
  ended. It chooses a position, walks there, and takes the picture. The picture
  reports the things a perception rule picks out of it. If the named thing is
  reported, the search ends found. The policy may instead answer "cannot be
  found". After the look limit the search ends unanswered.

What the robot knows
  Only its own looks: a walk through the whole-room positions at 18:00 on day
  0 (rendered at that time), and every look it has taken in earlier searches.
  Policies are given a `Known` object that holds the positions and the walking
  distances and nothing else; the truth and the pictures are not reachable
  from it.

What is scored, per search
  found: the named thing was reported and was really there         (right)
  found the wrong thing: reported, but it was a look-alike         (wrong; only under the measured rule)
  gave up, rightly: no position at that moment showed the thing  (right)
  gave up, wrongly: some position would have shown it            (wrong)
  ran out of looks                                               (wrong, whether or not it could have been found)
  looks, metres walked, and whether the thing had really moved (by the truth)
  since the robot last saw it.

The three hand-set rules give a thing's identity for free. The 'measured' rule
replays a real detector's misses and a matcher's mistakes, so under it a
look-alike can be declared found.

The robot starts each search where the last one ended, so the whole month
depends on where it began. Every policy is therefore run from several starting
positions and the results pooled, with the lowest and highest per-start value
reported beside the pooled one.

Costly looks (study 3; every option off by default, and then nothing above changes)
  --occupied-penalty P   a look into a room where a resident is at that moment costs P more
  --budget B[,B2,B3]     cost = metres walked + looks * metres per look + occupied penalties;
                         a search whose cost passes B without finding ends "ran out of budget"
  --metres-per-look M    the exchange rate between a look and walking (5, as chance-over-cost uses)
  model policy           a language model names the next place from what Known and Memory hold
  --fake-model nearest   the model policy answered by the last-seen-then-nearest rule, no network
  --fake-model distance  the model policy answered by nearest-untried-place, no network
  --show-prompt N        print the prompt the model policy would send in search N, then stop
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import os
import pathlib
import random
from typing import Callable, Dict, List, Optional, Set

import numpy as np

from rendered_look.world import REPO

HOME = REPO / "results/rendered_look/hh_s151"
LOOK_LIMIT = 12
DAY = 86400
PERCEPTION_RULES = ["in view", "600 pixels", "clear", "measured"]
CANNOT = "cannot be found"


@dataclasses.dataclass
class Costs:
    """What a search pays. The defaults make cost a number that is recorded but binds nothing."""
    metres_per_look: float = 5.0
    occupied_penalty: float = 0.0
    budget: Optional[float] = None

    def total(self, metres: float, looks: int, occupied_looks: int) -> float:
        return metres + looks * self.metres_per_look + occupied_looks * self.occupied_penalty


def clock_of(t: int) -> str:
    """day and time of a benchmark timestamp, as moments.json counts them (day 1 starts at t = 86400)"""
    return f"day {t // DAY}, {(t % DAY) // 3600:02d}:{(t % 3600) // 60:02d}"


def kind_of(thing: str) -> str:
    return thing.rsplit("_", 1)[0]


# ----------------------------------------------------------------------------- what a picture reports
class Perception:
    """Turns what is in a picture into what the robot reports.
    in view     at least 200 pixels, not cut by the edge, at least half of the thing's best showing
    600 pixels  in view, and at least 600 pixels
    clear       600 pixels, and not flagged as close in brightness to its surroundings
    measured    what a real detector and matcher did on these pictures (perception.json): each thing
                in the picture is detected with the recall measured for its size in pixels, and a
                detected thing is named right with the matching accuracy measured for its kind,
                otherwise named as another thing of its kind. The draw is fixed per picture and
                thing, so every policy meets the same misses and mistakes.
    The 'best showing' threshold is the 90th percentile of the thing's share of its
    outline over the whole month's pictures: a per-thing threshold no real detector has."""

    def __init__(self, kind: str, best_share: Dict[str, float], measured: Optional[dict] = None,
                 same_kind: Optional[Dict[str, List[str]]] = None) -> None:
        assert kind in PERCEPTION_RULES
        self.kind, self.best_share = kind, best_share
        self.same_kind = same_kind or {}
        if kind == "measured":
            assert measured is not None
            by_size = measured["detection"]["recall_by_pixels"]["0.2"]
            self.recall = {b: v[0] / max(1, v[1]) for b, v in by_size.items()}
            overall = sum(v[0] for v in by_size.values()) / max(1, sum(v[1] for v in by_size.values()))
            # the detector's recall for each kind, where at least 30 sightings were measured; the size
            # bins then only scale it up or down (glasses were found 0 times, towels most of the time)
            self.recall_by_kind = {k: v[0] / v[1] for k, v in measured["detection"]["recall_by_kind"]["0.2"].items() if v[1] >= 30}
            self.overall_recall = overall
            match = measured["matching"]["dinov2"].get("right_among_this_households_models") or \
                    measured["matching"]["dinov2"]["right_by_kind"]
            self.right_name = {k: v[0] / max(1, v[1]) for k, v in match.items() if v[1]}

    @staticmethod
    def _draw(*parts) -> float:
        import hashlib
        return int(hashlib.sha256("|".join(str(x) for x in parts).encode()).hexdigest()[:8], 16) / 16 ** 8

    def reported(self, in_picture: List[dict], salt: str = "") -> Set[str]:
        return self.reported_and_present(in_picture, salt)[0]

    def reported_and_present(self, in_picture: List[dict], salt: str = ""):
        """(what the robot reports, what is truly there in the sense of the 'in view' rule)"""
        out, present = set(), set()
        for p in in_picture:
            if p["is_person"] or p["pixels"] < 200 or p.get("cut_by_the_edge"):
                continue
            if p["what"] in self.best_share and p["share_of_its_outline"] < 0.5 * self.best_share[p["what"]]:
                continue
            present.add(p["what"])
            if self.kind == "measured":
                size = next(b for b in ("200-400", "400-1000", "1000-3000", "3000-")
                            if p["pixels"] < {"200-400": 400, "400-1000": 1000, "1000-3000": 3000, "3000-": 10 ** 9}[b])
                kind = kind_of(p["what"])
                chance = self.recall.get(size, 0.0)
                if kind in self.recall_by_kind and self.overall_recall > 0:
                    chance = min(1.0, self.recall_by_kind[kind] * chance / self.overall_recall)
                if self._draw("detect", salt, p["what"]) >= chance:
                    continue
                others = [o for o in self.same_kind.get(kind, []) if o != p["what"]]
                if others and self._draw("name", salt, p["what"]) >= self.right_name.get(kind, 1.0):
                    out.add(others[int(self._draw("which", salt, p["what"]) * len(others))])
                else:
                    out.add(p["what"])
                continue
            if self.kind in ("600 pixels", "clear") and p["pixels"] < 600:
                continue
            if self.kind == "clear" and p["hard_to_make_out"]:
                continue
            out.add(p["what"])
        return out, present


# ----------------------------------------------------------------------------- what policies may see
class Known:
    """The map: positions and the walking distance between them. Nothing about
    where things are or what any picture contains."""

    def __init__(self, positions: List[dict], metres: np.ndarray) -> None:
        self.positions = positions
        self.index = {p["id"]: i for i, p in enumerate(positions)}
        self.metres = metres
        self.place_of_position = {p["id"]: p["place"] for p in positions}
        self.room_of_position = {p["id"]: p["room"] for p in positions}
        self.kind_of_position = {p["id"]: p["kind"] for p in positions}
        self.whole_room_positions = [p["id"] for p in positions if p["kind"] == "whole room"]
        self.close_positions = [p["id"] for p in positions if p["kind"] == "one place"]
        self.places = sorted({p["place"] for p in positions if p["place"]})
        self.rooms = sorted({p["room"] for p in positions})
        # what each thing looks like, a fixed sentence per thing with no place in it; filled by Stored
        # from the day-0 walkthrough header so the model policy can describe what it is searching for
        self.looks_like: Dict[str, str] = {}
        self.positions_by_spot: Dict[str, List[str]] = collections.defaultdict(list)
        for p in positions:
            self.positions_by_spot[self.spot(p["id"])].append(p["id"])

    def spot(self, position_id: str) -> str:
        """The place a position looks at, or its room for a whole-room position."""
        return self.place_of_position[position_id] or ("room " + self.room_of_position[position_id])

    def spots(self) -> List[str]:
        """Every spot a look can be aimed at: the places, then the whole-room looks."""
        return self.places + ["room " + r for r in self.rooms]

    def positions_at(self, spot: str) -> List[str]:
        return self.positions_by_spot[spot]

    def room_of_spot(self, spot: str) -> str:
        return self.room_of_position[self.positions_at(spot)[0]]

    def distance(self, a: str, b: str) -> float:
        return float(self.metres[self.index[a], self.index[b]])

    def nearest_position_at(self, here: str, spot: str, tried: List[str]) -> Optional[str]:
        """The position aimed at `spot` the robot would walk to: the nearest untried one; ties go
        to the earlier position in the list, as min() does for the rule policies."""
        return _nearest(here, self, [p for p in self.positions_at(spot) if p not in tried])


# ----------------------------------------------------------------------------- the stored world
class Stored:
    def __init__(self, rig_dir: pathlib.Path, perception_kind: str) -> None:
        meta = json.load((rig_dir / "positions.json").open())
        metres = np.array(meta["metres_between"])
        metres[metres < 0] = 50.0
        self.known = Known(meta["positions"], metres)
        self.moments: List[dict] = sorted(json.load((rig_dir / "moments.json").open()), key=lambda m: m["t"])
        self.pictures: Dict[tuple, List[dict]] = {}
        self.frame_of: Dict[tuple, str] = {}
        shares = collections.defaultdict(list)
        with (rig_dir / "observations.jsonl").open() as rows:
            for line in rows:
                row = json.loads(line)
                self.pictures[row["t"], row["position"]] = row["in_picture"]
                self.frame_of[row["t"], row["position"]] = row["frame"]
                for p in row["in_picture"]:
                    if not p["is_person"] and p["seen"] and not p.get("cut_by_the_edge"):
                        shares[p["what"]].append(p["share_of_its_outline"])
        self.walkthrough: List[dict] = []
        self.walkthrough_truth: Dict[str, dict] = {}
        with (rig_dir / "walkthrough.jsonl").open() as rows:
            for line in rows:
                row = json.loads(line)
                if row.get("header"):
                    self.walkthrough_truth = row["things"]
                else:
                    self.walkthrough.append(row)
        best = {k: float(np.percentile(v, 90)) for k, v in shares.items() if len(v) >= 5}
        things = sorted({m["asked_about"] for m in self.moments} | set(self.walkthrough_truth))
        same_kind = collections.defaultdict(list)
        for thing in things:
            same_kind[kind_of(thing)].append(thing)
        measured = json.load((rig_dir / "perception.json").open()) if perception_kind == "measured" else None
        self.perception = Perception(perception_kind, best, measured, same_kind)
        self.reports, self.present = {}, {}
        for key, pic in self.pictures.items():
            # the draw is keyed on the picture itself, so an identical picture gets an identical report
            self.reports[key], self.present[key] = self.perception.reported_and_present(pic, self.frame_of[key])
        self.truth_at: Dict[int, Dict[str, dict]] = {m["t"]: m["things"] for m in self.moments}
        self.truth_at[self.walkthrough[0]["t"]] = self.walkthrough_truth
        self.known.looks_like = {k: v["looks_like"] for k, v in self.walkthrough_truth.items() if v.get("looks_like")}
        # which rooms hold a resident at each moment: moments.json gives each resident a room
        # (or AWAY with shown false), never a place, so "the room contains a resident" is read
        # straight off that field. The walkthrough moment has no people record: no room is occupied.
        self.occupied_rooms: Dict[int, Set[str]] = {m["t"]: {p["room"] for p in m.get("people", []) if p.get("shown")}
                                                    for m in self.moments}

    def occupied(self, t: int, position: str) -> bool:
        return self.known.room_of_position[position] in self.occupied_rooms.get(t, set())

    def saw_person(self, t: int, position: str) -> bool:
        """The camera's own knowledge of people: a person entry in the picture that was seen."""
        return any(p["is_person"] and p["seen"] for p in self.pictures[t, position])

    def look(self, t: int, position: str) -> Set[str]:
        return self.reports[t, position]

    def findable(self, t: int, thing: str) -> bool:
        """Some position's picture reports the thing, and it really is there."""
        return any(thing in self.reports[t, p["id"]] and thing in self.present[t, p["id"]] for p in self.known.positions)

    def true_place(self, t: int, thing: str) -> Optional[str]:
        record = self.truth_at.get(t, {}).get(thing, {})
        return record.get("place") if record.get("shown") else None


# ----------------------------------------------------------------------------- what the robot remembers
class Memory:
    """Every look the robot took: when, where it stood, and what it reported."""

    def __init__(self, known: Known) -> None:
        self.known = known
        self.sightings: Dict[str, List[dict]] = collections.defaultdict(list)   # thing -> [{t, position, spot}]

    def record(self, t: int, position: str, reported: Set[str]) -> None:
        for thing in reported:
            # the robot knows where it stood and what it aimed at, not where in the room the thing was
            self.sightings[thing].append({"t": t, "position": position, "spot": self.known.spot(position)})

    def last_seen(self, thing: str) -> Optional[dict]:
        return self.sightings[thing][-1] if self.sightings[thing] else None


# ----------------------------------------------------------------------------- policies
# A policy: (thing, memory, here, known, tried, rng, step) -> the next position, or None for "cannot be found".
# `step` says what the policy may know about the search it is in beyond the map and its memory.

@dataclasses.dataclass
class Step:
    """What a policy may know about the search it is in, beyond the map and its memory.
    Under a budget "untried" means "untried and affordable" for every policy alike: a look is
    allowed only if the walk to it plus one look fee fits in the budget left. The budget left
    here counts metres and look fees only; the occupancy penalties are charged by the world
    and no policy is told about them, so a policy can propose a look the world then refuses."""
    t: int                                 # the moment asked
    budget_left: Optional[float] = None    # budget minus metres walked and look fees so far; penalties are NOT in it
    reach: Optional[float] = None          # the longest walk the next look may take (budget_left minus one look fee)
    at: Optional[Callable] = None          # spot -> the position the robot would stand at; where affordability is judged

    def affordable(self, known: "Known", here: str, position: str) -> bool:
        """Judged at the position the robot would stand at for that position's spot (where it last
        saw the thing from, else the nearest open position), so that a place is affordable or not
        as a whole; the prompt shows places, not positions, and the rules must agree with it."""
        if self.reach is None:
            return True
        stand = self.at(known.spot(position)) if self.at else position
        return known.distance(here, stand or position) <= self.reach


def standing_positions(thing, memory, here, known, tried) -> Callable:
    """spot -> where the robot would stand to look at it: the newest untried position it saw the
    thing from, else the nearest untried position of the spot. Memoised for one step."""
    newest: Dict[str, str] = {}
    for s in reversed(memory.sightings[thing]):
        if s["spot"] not in newest and s["position"] not in tried:
            newest[s["spot"]] = s["position"]
    cache: Dict[str, Optional[str]] = {}

    def at(spot: str) -> Optional[str]:
        if spot not in cache:
            cache[spot] = newest.get(spot) or known.nearest_position_at(here, spot, tried)
        return cache[spot]
    return at


FREE = Step(t=0)   # no budget: nothing is filtered


def _untried_spots(known: Known, tried: List[str], candidates: List[str], here: str = None, step: Step = FREE) -> List[str]:
    """Candidates whose spot has not been looked at in this search and which the budget still allows."""
    spots_tried = {known.spot(p) for p in tried}
    return [c for c in candidates if c not in tried and known.spot(c) not in spots_tried
            and (here is None or step.affordable(known, here, c))]


def _nearest(here: str, known: Known, pool: List[str]) -> Optional[str]:
    return min(pool, key=lambda p: known.distance(here, p)) if pool else None


def _by_recency(thing, memory, known, tried, here=None, step=FREE) -> List[str]:
    order = []
    for s in reversed(memory.sightings[thing]):
        if s["position"] not in order:
            order.append(s["position"])
    return _untried_spots(known, tried, order, here, step)


def _by_frequency(thing, memory, known, tried, here=None, step=FREE) -> List[str]:
    counts = collections.Counter(s["position"] for s in memory.sightings[thing])
    return _untried_spots(known, tried, [p for p, _ in counts.most_common()], here, step)


def _by_kind(thing, memory, known, tried, here=None, step=FREE) -> List[str]:
    """Household common sense: positions where things of the same kind were seen, most first."""
    counts = collections.Counter()
    for other, sightings in memory.sightings.items():
        if other != thing and kind_of(other) == kind_of(thing):
            for s in sightings:
                counts[s["position"]] += 1
    return _untried_spots(known, tried, [p for p, _ in counts.most_common()], here, step)


def _by_time_of_day(thing, memory, known, tried, here, step) -> List[str]:
    """Positions from which the thing was seen within an hour of the present clock time on an earlier
    day, most such sightings first; ties go to the more recently seen, then to the shorter walk."""
    tod = step.t % DAY
    counts, newest = collections.Counter(), {}
    for s in memory.sightings[thing]:
        gap = abs(s["t"] % DAY - tod)
        if s["t"] // DAY < step.t // DAY and min(gap, DAY - gap) <= 3600:
            counts[s["position"]] += 1
            newest[s["position"]] = s["t"]
    order = sorted(counts, key=lambda p: (-counts[p], -newest[p], known.distance(here, p)))
    return _untried_spots(known, tried, order, here, step)


def _room_not_looked_in(here, known, tried, step=FREE) -> Optional[str]:
    rooms_tried = {known.room_of_position[p] for p in tried}
    return _nearest(here, known, [p for p in known.whole_room_positions
                                  if known.room_of_position[p] not in rooms_tried and p not in tried
                                  and step.affordable(known, here, p)])


def _nearest_untried_place(here, known, tried, step=FREE) -> Optional[str]:
    pool = _untried_spots(known, tried, known.close_positions, here, step)
    if not pool and step.reach is None:
        # every place looked at: look again from another position. Never reached within the look
        # limit (12 looks, 26 places); under a budget it is not offered, because there "untried"
        # means an untried place, which is all the prompt can name, and the rules must agree with it.
        pool = [p for p in known.close_positions if p not in tried] or \
               [p["id"] for p in known.positions if p["id"] not in tried]
    return _nearest(here, known, pool)


def open_places(known, here, tried, step) -> List[str]:
    """Close positions at places not yet looked at in this search that the budget still allows. When
    there are none, a policy that stops has run out of budget rather than given up."""
    return _untried_spots(known, tried, known.close_positions, here, step)


FALLBACKS = ["nearest", "kind, then nearest", "kind, then rooms", "rooms, then nearest"]


def fallback(rule: str, thing, memory, here, known, tried, step=FREE) -> Optional[str]:
    """What to do when the thing has never been seen, or every position it was seen from is tried."""
    if rule.startswith("kind"):
        for p in _by_kind(thing, memory, known, tried, here, step):
            return p
    if "rooms" in rule:
        room = _room_not_looked_in(here, known, tried, step)
        if room:
            return room
    return _nearest_untried_place(here, known, tried, step)


def make_rule_policy(order: str, fb: str) -> Callable:
    def policy(thing, memory, here, known, tried, rng, step=FREE):
        if order == "mix":
            recency = _by_recency(thing, memory, known, tried, here, step)
            frequency = _by_frequency(thing, memory, known, tried, here, step)
            if recency:
                score = {p: (recency.index(p) if p in recency else len(recency)) +
                            (frequency.index(p) if p in frequency else len(frequency))
                         for p in sorted(set(recency) | set(frequency))}
                return min(score, key=lambda p: (score[p], known.distance(here, p), p))   # ties: the nearer, then by name
        elif order == "same time of day":
            # the brief's clock baseline: same hour on earlier days, then recency, then nearest untried
            for get in (_by_time_of_day, _by_recency):
                for p in get(thing, memory, known, tried, here, step):
                    return p
        elif order == "last seen by room":
            # recency order, but the sighted places in the room the robot stands in come first
            recency = _by_recency(thing, memory, known, tried, here, step)
            room = known.room_of_position[here]
            for p in [p for p in recency if known.room_of_position[p] == room] + recency:
                return p
        else:
            lists = [_by_recency, _by_frequency] if order == "last seen" else [_by_frequency, _by_recency]
            for get in lists:
                for p in get(thing, memory, known, tried, here, step):
                    return p
        return fallback(fb, thing, memory, here, known, tried, step)
    return policy


def policy_random(thing, memory, here, known, tried, rng, step=FREE):
    left = [p["id"] for p in known.positions if p["id"] not in tried and step.affordable(known, here, p["id"])]
    return rng.choice(left) if left else None


class PolicyChanceOverCost:
    """Look where (chance it is there x chance of seeing it if it is) / cost is
    largest; after a look that found nothing, lower that spot's chance.

    Chance it is there: the thing's past sightings by spot (the spot a position
    was aimed at), newest counting most (half-life 3 days), plus a small floor
    everywhere. If it has never been seen, every spot starts equal.
    Chance of seeing it: 0.35 for a close look at its spot, 0.10 for a
    whole-room look at its room, the averages measured in this home at 0.37 m
    (a real robot would have to learn these).
    Cost: one look plus the walk, at five metres to a look.
    Answers "cannot be found" when the chance left after the looks that found
    nothing falls below a quarter (a tenth was never reached in this home).
    """

    def __init__(self, close: float = 0.35, room: float = 0.10, give_up_below: float = 0.25,
                 half_life_days: float = 3.0, floor: float = 0.002, metres_per_look: float = 5.0) -> None:
        self.q_close, self.q_room, self.give_up_below = close, room, give_up_below
        self.half_life, self.floor, self.metres_per_look = half_life_days, floor, metres_per_look
        self.belief: Dict[str, float] = {}
        self.mass_left = 1.0

    def start(self, thing: str, memory: Memory, known: Known, t: int) -> None:
        weight = collections.Counter()
        for s in memory.sightings[thing]:
            weight[s["spot"]] += 0.5 ** ((t - s["t"]) / DAY / self.half_life)
        total = sum(weight.values())
        spots = known.places + ["room " + r for r in known.rooms]
        self.belief = {s: self.floor + (weight[s] / total if total else 1.0 / len(spots)) for s in spots}
        norm = sum(self.belief.values())
        self.belief = {k: v / norm for k, v in self.belief.items()}
        self.mass_left = 1.0

    def chance_of_seeing(self, known: Known, position_id: str, spot: str) -> float:
        if known.place_of_position[position_id] == spot:
            return self.q_close
        if known.kind_of_position[position_id] == "whole room" and spot == "room " + known.room_of_position[position_id]:
            return self.q_room
        return 0.0

    def __call__(self, thing, memory, here, known, tried, rng, step=FREE):
        if self.mass_left < self.give_up_below:
            return None
        best, best_value = None, 0.0
        for p in known.positions:
            if p["id"] in tried or not step.affordable(known, here, p["id"]):
                continue
            chance = sum(self.belief[s] * self.chance_of_seeing(known, p["id"], s) for s in self.belief)
            value = chance / (1.0 + known.distance(here, p["id"]) / self.metres_per_look)
            if value > best_value:
                best, best_value = p["id"], value
        return best

    def missed(self, known: Known, position_id: str) -> None:
        for spot in list(self.belief):
            self.belief[spot] *= 1.0 - self.chance_of_seeing(known, position_id, spot)
        norm = sum(self.belief.values())
        self.mass_left *= norm
        if norm > 0:
            self.belief = {k: v / norm for k, v in self.belief.items()}


def policy_distance_order(thing, memory, here, known, tried, rng, step=FREE):
    """The brief's second baseline: every place in order of distance from where the robot stands,
    re-read after each move (the robot stands somewhere new). No memory of the thing at all."""
    return _nearest_untried_place(here, known, tried, step)


# ----------------------------------------------------------------------------- the model policy
SCHEMA = {
    "type": "object",
    "properties": {
        # "why" first on purpose: the model writes its reasons before it commits to a place
        "why": {"type": "string", "maxLength": 600},
        "next": {"type": "string"},
    },
    "required": ["why", "next"], "additionalProperties": False}

SYSTEM = ("You direct a home robot that is searching for one thing. It can walk to a place and look "
          "at it, or look across a whole room. Each look costs walking plus a fixed charge per look, and "
          "a penalty if the room it looks into has a resident in it. You see only what the robot itself has "
          "seen. Answer with JSON: first \"why\" (your reasons, under 600 characters), then \"next\": the id "
          f"of the place to look at next, exactly as listed, or \"{CANNOT}\" to stop and answer that the "
          "thing cannot be found now.")

ROOM_LOOK = "whole_room:"   # how a whole-room look is named in the prompt; "room X" inside the benchmark


def spot_label(spot: str) -> str:
    return ROOM_LOOK + spot[5:] if spot.startswith("room ") else spot


def spot_from_label(label: str) -> str:
    return "room " + label[len(ROOM_LOOK):] if label.startswith(ROOM_LOOK) else label


class PolicyModel:
    """At each step the model is handed, and only handed:
      the asked thing's id and what it looks like (Known.looks_like, a fixed sentence);
      the robot's own earlier sightings of it, one line per moment with the places (Memory);
      every spot with the walk the robot would make to it, whether this search already looked
        there, and what that look reported, including "a person" when the picture showed one
        (Known, and this search's own pictures);
      the budget left without the penalties charged, the look cap, the penalty, and the share of
        questions over the month with no position showing the thing (a fixed number);
      the day and time now.
    It names a spot; the robot walks to a position aimed at that spot. stand = "where last seen"
    (the default): the position it last saw the thing from, if it has such a sighting there and
    that position is untried, else the nearest untried one; this is what the last-seen rule does.
    stand = "nearest": always the nearest untried position of the spot, as "distance order" does.
    The walk shown for a spot is the walk to that very position.
    It never sees the truth, a picture it has not taken, or a resident's whereabouts from the
    moments file; the budget left shown leaves the penalties out so that it cannot be worked back
    to which rooms were occupied.

    fake = "nearest": the answer is read off the rendered prompt by the last-seen-then-nearest
    rule (the newest sighting line's first place not yet looked at and still affordable; else the
    first open, affordable place in the list, which is sorted by walk), so the run must match
    "last seen (nearest)" search for search. fake = "distance": the first open, affordable place
    in the list, which matches "distance order" when stand = "nearest". Neither touches the network.
    """

    def __init__(self, fake: Optional[str] = None, client=None, show: bool = False,
                 stand: str = "where last seen", unfindable_share: Optional[float] = None) -> None:
        assert fake in (None, "nearest", "distance") and stand in ("where last seen", "nearest")
        self.fake, self.client, self.show, self.stand = fake, client, show, stand
        self.unfindable_share = unfindable_share
        self.transcript: List[dict] = []         # (prompt, answer) pairs when show is on
        self.decisions: List[dict] = []          # who decided each step of the present search
        self.thing = None
        self.costs: Costs = Costs()
        self.seen_this_search: Dict[str, dict] = {}

    def start(self, thing: str, costs: Costs) -> None:
        self.thing, self.costs = thing, costs
        self.seen_this_search = {}
        self.decisions = []

    def after_look(self, known: Known, position: str, reported: Set[str], saw_person: bool) -> None:
        self.seen_this_search[known.spot(position)] = {"things": sorted(reported), "person": saw_person}

    # -- where the robot would stand for a spot, shared by the walk shown and the walk made
    def position_for(self, memory: Memory, here: str, known: Known, tried: List[str]) -> Callable:
        if self.stand == "where last seen":
            return standing_positions(self.thing, memory, here, known, tried)
        return lambda spot: known.nearest_position_at(here, spot, tried)

    # -- the input, as data; the prompt is rendered from it
    def inputs(self, memory: Memory, here: str, known: Known, tried: List[str], step: Step) -> dict:
        spots_tried = {known.spot(p) for p in tried}
        sightings = memory.sightings[self.thing]
        moments: Dict[int, List[str]] = {}
        for s in sightings:                        # one line per moment; within it the newest look first
            places = moments.setdefault(s["t"], [])
            if s["spot"] in places:
                places.remove(s["spot"])
            places.insert(0, s["spot"])
        events = [{"t": t, "spots": moments[t]} for t in sorted(moments, reverse=True)]
        candidates, at = [], self.position_for(memory, here, known, tried)
        for spot in known.spots():
            position = at(spot)
            if position is None:
                continue
            seen = self.seen_this_search.get(spot)
            candidates.append({"spot": spot, "room": known.room_of_spot(spot), "position": position,
                               "distance": known.distance(here, position), "order": known.index[position],
                               "affordable": step.reach is None or known.distance(here, position) <= step.reach,
                               "tried": spot in spots_tried, "seen": seen})
        # sorted by the walk, ties by position order: the list order is the nearest-first order the rules use
        candidates.sort(key=lambda c: (c["distance"], c["order"]))
        return {"thing": self.thing, "looks_like": known.looks_like.get(self.thing), "now": clock_of(step.t),
                "events": events, "candidates": candidates, "tried_spots": sorted(spots_tried),
                "budget_left": step.budget_left, "metres_per_look": self.costs.metres_per_look,
                "penalty": self.costs.occupied_penalty, "looks_left": LOOK_LIMIT - len(tried),
                "unfindable_share": self.unfindable_share}

    @staticmethod
    def render(inp: dict) -> List[dict]:
        lines = [f"Find: {inp['thing']}" + (f" ({inp['looks_like']})" if inp["looks_like"] else "") + ".",
                 f"Now: {inp['now']}.", ""]
        if inp["events"]:
            lines.append("When and where the robot has seen it (newest first):")
            for e in inp["events"]:
                lines.append(f"  {clock_of(e['t'])}: {', '.join(spot_label(s) for s in e['spots'])}")
        else:
            lines.append("The robot has never seen it.")
        lines += ["", "Places it can look at, nearest first, with the walk from where it stands now:"]
        for c in inp["candidates"]:
            note = ""
            if c["tried"]:
                saw = list(c["seen"]["things"]) + (["a person"] if c["seen"]["person"] else [])
                note = "  <- looked at in this search: did not see it (" + (("saw: " + ", ".join(saw)) if saw else "nothing") + ")"
            elif not c["affordable"]:
                note = "  [too far for the budget left]"
            lines.append(f"  {spot_label(c['spot'])} (in {c['room']}): {c['distance']:.1f} m{note}")
        lines += ["", f"Each look costs {inp['metres_per_look']:g} on top of the metres walked, and {inp['penalty']:g} more if a "
                      f"resident is in the room it looks into; the robot does not know in advance who is where. "
                      f"At most {LOOK_LIMIT} looks per search ({inp['looks_left']} left)."]
        if inp["budget_left"] is not None:
            lines.append(f"Budget left for this search, counting metres and look charges only: {inp['budget_left']:.1f}. "
                         "Penalties already charged are not shown. Naming a place marked too far ends the search.")
        else:
            lines.append("No budget for this search; fewer looks and metres are still better.")
        if inp["unfindable_share"] is not None:
            lines.append(f"Over the month, {100 * inp['unfindable_share']:.1f}% of the time the thing asked about cannot be seen "
                         f"from any position (put away, carried, or out of every camera's view), so \"{CANNOT}\" is a real option.")
        lines += ["", f"Where should the robot look next? Give \"why\" first, then \"next\" (a place id above or \"{CANNOT}\")."]
        return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n".join(lines)}]

    # -- the fakes read the rendered prompt, not the data behind it
    @staticmethod
    def parse_prompt(text: str):
        """(sighting lines as lists of place ids newest first, open affordable place ids in list order, tried place ids)"""
        events, open_places, tried = [], [], []
        section = None
        for line in text.split("\n"):
            if line.startswith("When and where"):
                section = "events"
            elif line.startswith("Places it can look at"):
                section = "places"
            elif not line.startswith("  "):
                section = None
            elif section == "events":
                events.append([spot_from_label(p) for p in line.split(": ", 1)[1].split(", ")])
            elif section == "places":
                label = line.strip().split(" (in ")[0]
                if "<- looked at" in line:
                    tried.append(spot_from_label(label))
                elif "[too far" not in line:
                    open_places.append(spot_from_label(label))
        return events, open_places, tried

    def decide_fake(self, messages: List[dict]) -> str:
        events, open_places, tried = self.parse_prompt(messages[1]["content"])
        if self.fake == "nearest":
            for places in events:                      # the newest sighting at a place still open and affordable
                for spot in places:
                    if spot in open_places:
                        return spot
        places = [p for p in open_places if not p.startswith("room ")]   # a place, as the rule's fallback: never a whole-room look
        return places[0] if places else CANNOT

    def decide_model(self, messages: List[dict], inp: dict):
        """(the chosen spot, who decided)"""
        open_spots = [c["spot"] for c in inp["candidates"] if not c["tried"] and c["affordable"]]
        # the schema pins "next" to the places still open, so the server cannot return a misspelling
        schema = dict(SCHEMA, properties={**SCHEMA["properties"],
                                          "next": {"type": "string", "enum": [spot_label(s) for s in open_spots] + [CANNOT]}})
        text, _ = self.client.complete(messages, schema, 400)
        if text is None:
            return self.decide_fallback(messages), "fallback: lost call"
        try:
            answer = json.loads(text)["next"]
        except (TypeError, ValueError, KeyError):
            return self.decide_fallback(messages), "fallback: unparseable"
        if answer == CANNOT:
            return answer, "model"
        spot = spot_from_label(answer)
        if spot not in open_spots:
            return self.decide_fallback(messages), "fallback: tried place"
        return spot, "model"

    def decide_fallback(self, messages: List[dict]) -> str:
        fake, self.fake = self.fake, "distance"
        try:
            return self.decide_fake(messages)
        finally:
            self.fake = fake

    def enum_sent(self, inp: dict) -> List[str]:
        return [spot_label(c["spot"]) for c in inp["candidates"] if not c["tried"] and c["affordable"]] + [CANNOT]

    def __call__(self, thing, memory, here, known, tried, rng, step=FREE):
        inp = self.inputs(memory, here, known, tried, step)
        messages = self.render(inp)
        if self.fake:
            answer, by = self.decide_fake(messages), "fake " + self.fake
        else:
            answer, by = self.decide_model(messages, inp)
        self.decisions.append({"by": by, "next": spot_label(answer) if answer != CANNOT else CANNOT})
        if self.show:
            self.transcript.append({"messages": messages, "answer": answer, "by": by, "enum": self.enum_sent(inp)})
        if answer == CANNOT:
            return None
        return next((c["position"] for c in inp["candidates"] if c["spot"] == answer), None)


def make_client():
    """The shared vLLM client, built only when the model policy is chosen and no fake is set.
    The endpoint comes from the locked study settings (an env override wins), the model name from
    the env or the patrol client's default; the settings file names no model. The cache is kept
    per model name AND endpoint, so two servers under one model name never share answers."""
    import re
    import urllib.parse
    from baselines.patrol import llm as patrol_llm
    from self_improve.study_settings import LOCKED
    endpoint = os.environ.get("SEARCHBENCH_LLM_ENDPOINT", LOCKED.endpoint)
    model = os.environ.get("SEARCHBENCH_LLM_MODEL", patrol_llm.MODEL)
    u = urllib.parse.urlsplit(endpoint)
    folder = re.sub(r"[^A-Za-z0-9._-]+", "_", model) + "__" + f"{u.hostname}_{u.port or 80}"
    return patrol_llm.LLMClient(HOME / "searchbench" / "model_cache" / folder, endpoint=endpoint, model=model)


# ----------------------------------------------------------------------------- running a month
MEMORYLESS = ("random", "distance order", "oracle", "oracle within memory")


def run(stored: Stored, policy_name: str, seed: int = 0, start: int = 0, costs: Optional[Costs] = None,
        model: Optional[PolicyModel] = None) -> List[dict]:
    """One month of searches. `start` picks which whole-room position the robot begins at;
    the robot then starts each search where the last one ended, so the start matters.
    `costs` prices the looks; with the default Costs() the cost is recorded and binds nothing.
    `model` is the model policy's state, made by the caller so one client serves every run.

    The budget, applied identically to every policy, model included:
      a look is taken only if it is affordable: what has been charged so far (metres, look fees
      and the penalties the world charged) plus the walk plus one look fee fits in the budget;
      a policy that names an unaffordable look, or has none left to name, ends the search as
      "ran out of budget" without that look;
      a find on the last affordable look counts, even when that look's own occupancy penalty
      (unknown until the look is taken) carries the total past the budget;
      policies are told the budget left without the penalties, so they can be refused.
    """
    rng = random.Random(seed)
    costs = costs or Costs()
    known = stored.known
    memory = Memory(known)
    chance = PolicyChanceOverCost(metres_per_look=costs.metres_per_look) if policy_name == "chance over cost" else None
    if policy_name == "random":
        policy = policy_random
    elif policy_name in ("chance over cost", "oracle", "oracle within memory"):
        policy = chance
    elif policy_name == "oracle within memory, then last seen":
        policy = make_rule_policy("last seen", "nearest")
    elif policy_name == "distance order":
        policy = policy_distance_order
    elif policy_name == "model":
        assert model is not None
        policy = model
    else:
        order, fb = policy_name.split(" (")
        policy = make_rule_policy(order, fb.rstrip(")"))
    judge_at_last_seen = policy_name not in MEMORYLESS and not (model and model.stand == "nearest")
    # day 0, 18:00: the walk through every whole-room position, the same for every policy
    t_walk = stored.walkthrough[0]["t"]
    for look in stored.walkthrough:
        memory.record(t_walk, look["position"], stored.perception.reported(look["in_picture"], f"walk|{look['position']}"))
    here = known.whole_room_positions[start % len(known.whole_room_positions)]
    results = []
    for moment in stored.moments:
        t, thing = moment["t"], moment["asked_about"]
        before = memory.last_seen(thing)
        truth_now = stored.true_place(t, thing)
        truth_then = stored.true_place(before["t"], thing) if before else None
        really_moved = bool(before and truth_now and truth_then and truth_then != truth_now)
        findable = stored.findable(t, thing)
        tried: List[str] = []
        metres, outcome = 0.0, "ran out of looks"
        occupied_looks, cost = 0, 0.0
        if chance:
            chance.start(thing, memory, known, t)
        if model:
            model.start(thing, costs)
        for _ in range(LOOK_LIMIT):
            step = Step(t)
            if costs.budget is not None:
                step.budget_left = costs.budget - metres - len(tried) * costs.metres_per_look
                step.reach = step.budget_left - costs.metres_per_look
                step.at = standing_positions(thing, memory, here, known, tried) if judge_at_last_seen else None
            if policy_name == "oracle":   # reads the truth by design: the nearest position that truly shows the thing
                showing = [p["id"] for p in known.positions
                           if thing in stored.reports[t, p["id"]] and thing in stored.present[t, p["id"]]]
                nxt = _nearest(here, known, [p for p in showing if p not in tried and step.affordable(known, here, p)]) \
                    if showing else None
            elif policy_name.startswith("oracle within memory"):
                # reads the truth by design, but only among places the robot's own memory has seen the thing at.
                # As asked for, it answers "cannot be found" when no remembered place shows the thing, so it
                # never explores and its memory never grows: that makes it a floor, not a ceiling. The
                # ", then last seen" variant does exactly what "last seen (nearest)" does when memory has no
                # place that shows the thing (a nearest-untried walk from where the robot stands did worse
                # than the rule, whose wrong first look lands it next to the right place), so its memory
                # grows as the rule's does; that is the ceiling for a method that works from this memory.
                seen_at = {s["spot"] for s in memory.sightings[thing]}
                showing = [p["id"] for p in known.positions if known.spot(p["id"]) in seen_at
                           and thing in stored.reports[t, p["id"]] and thing in stored.present[t, p["id"]]]
                nxt = _nearest(here, known, [p for p in showing if p not in tried and step.affordable(known, here, p)])
                if nxt is None and policy_name.endswith("then last seen"):
                    nxt = policy(thing, memory, here, known, tried, rng, step)
            else:
                nxt = policy(thing, memory, here, known, tried, rng, step)
            if nxt is None:
                if costs.budget is not None and not open_places(known, here, tried, step):
                    outcome = "ran out of budget"
                else:
                    outcome = "gave up, rightly" if not findable else "gave up, wrongly"
                break
            walk = known.distance(here, nxt)
            if costs.budget is not None and cost + walk + costs.metres_per_look > costs.budget:
                outcome = "ran out of budget"        # the look is not taken
                break
            metres += walk
            here = nxt
            tried.append(nxt)
            occupied_looks += stored.occupied(t, nxt)
            cost = costs.total(metres, len(tried), occupied_looks)
            reported = stored.look(t, nxt)
            memory.record(t, nxt, reported)
            if model:
                model.after_look(known, nxt, reported, stored.saw_person(t, nxt))
            if thing in reported:
                outcome = "found" if thing in stored.present[t, nxt] else "found the wrong thing"
                break
            if chance:
                chance.missed(known, nxt)
        stood_at_right_place = bool(truth_now) and any(known.place_of_position[p] == truth_now for p in tried)
        results.append({"policy": policy_name, "start": start, "question": moment["question_id"], "day": moment["day"], "t": t,
                        "thing": thing, "kind": kind_of(thing), "outcome": outcome, "looks": len(tried),
                        "stood_at_right_place": stood_at_right_place,
                        "metres": round(metres, 1), "findable": findable, "really_moved": really_moved,
                        "seen_before": before is not None, "truth_place": truth_now,
                        "looked_at_same_place_twice": len({known.spot(p) for p in tried}) < len(tried),
                        "occupied_looks": occupied_looks, "cost": round(cost, 1), "budget": costs.budget, "tried": list(tried),
                        "found_within_budget": outcome == "found",
                        "decided_by": list(model.decisions) if model else None})
    return results


def summarise(results: List[dict]) -> dict:
    n = len(results)
    found = [r for r in results if r["outcome"] == "found"]
    findable = [r for r in results if r["findable"]]
    decisions = collections.Counter(d["by"] for r in results for d in (r["decided_by"] or []))

    def share(rows, test=lambda r: r["outcome"] == "found"):
        return round(float(np.mean([test(r) for r in rows])), 3) if rows else None

    return {
        "searches": n, "findable": len(findable),
        "found, of findable": share(findable),
        "found, of findable towels": share([r for r in findable if r["kind"] == "towel"]),
        "found, of findable other things": share([r for r in findable if r["kind"] != "towel"]),
        "right answer, of all": share(results, lambda r: r["outcome"] in ("found", "gave up, rightly")),
        "found the wrong thing": sum(r["outcome"] == "found the wrong thing" for r in results),
        "gave up rightly": sum(r["outcome"] == "gave up, rightly" for r in results),
        "gave up wrongly": sum(r["outcome"] == "gave up, wrongly" for r in results),
        "ran out of looks": sum(r["outcome"] == "ran out of looks" for r in results),
        "looks when found": round(float(np.mean([r["looks"] for r in found])), 2) if found else None,
        "metres when found": round(float(np.mean([r["metres"] for r in found])), 1) if found else None,
        "looks, all searches": round(float(np.mean([r["looks"] for r in results])), 2),
        "metres, all searches": round(float(np.mean([r["metres"] for r in results])), 1),
        "found of findable, really moved since last seen": share([r for r in findable if r["really_moved"]]),
        "found of findable, not moved": share([r for r in findable if r["seen_before"] and not r["really_moved"]]),
        "found of findable, never seen before": share([r for r in findable if not r["seen_before"]]),
        "searches that looked at a place twice": sum(r["looked_at_same_place_twice"] for r in results),
        "stood at the right place but did not find it": sum(r["stood_at_right_place"] and r["outcome"] != "found" for r in results),
        # costly looks: with the options off these are 0 / the same as found / metres + 5 per look
        "ran out of budget": sum(r["outcome"] == "ran out of budget" for r in results),
        "found within budget, of findable": share(findable, lambda r: r["found_within_budget"]),
        "found within budget, of findable towels": share([r for r in findable if r["kind"] == "towel"], lambda r: r["found_within_budget"]),
        "found within budget, of findable other things": share([r for r in findable if r["kind"] != "towel"], lambda r: r["found_within_budget"]),
        "cost per question among found": round(float(np.mean([r["cost"] for r in results if r["found_within_budget"]])), 1)
        if any(r["found_within_budget"] for r in results) else None,
        "occupied looks per search": round(float(np.mean([r["occupied_looks"] for r in results])), 2),
        # the model policy only: who decided each step
        "steps decided by the model": decisions["model"],
        "steps by fallback: lost call": decisions["fallback: lost call"],
        "steps by fallback: unparseable": decisions["fallback: unparseable"],
        "steps by fallback: tried place": decisions["fallback: tried place"],
    }


def paired(rows: List[dict], reference: List[dict], start: int = 0) -> dict:
    """Question by question at one start: on how many findable questions do the two differ in finding
    within budget, and how many more does `rows` find. The 2-SE bar belongs on the discordant count."""
    ref = {r["question"]: r for r in reference if r["start"] == start}
    mine = [r for r in rows if r["start"] == start and r["findable"] and r["question"] in ref]
    discordant = [r for r in mine if r["found_within_budget"] != ref[r["question"]]["found_within_budget"]]
    net = sum(r["found_within_budget"] for r in discordant) - sum(ref[r["question"]]["found_within_budget"] for r in discordant)
    return {"discordant questions": len(discordant), "net extra finds": net, "findable questions": len(mine)}


RULES = [f"{o} ({fb})" for o in ("last seen", "most frequent", "mix") for fb in FALLBACKS] + \
        ["same time of day (nearest)", "last seen by room (nearest)"]
POLICIES = ["random"] + RULES + ["chance over cost", "distance order", "oracle within memory",
                                 "oracle within memory, then last seen", "oracle"]
BASE_KEYS = ["found, of findable", "found, of findable towels", "found, of findable other things", "right answer, of all",
             "looks when found", "metres when found", "found the wrong thing", "gave up wrongly", "ran out of looks",
             "found of findable, really moved since last seen", "found of findable, not moved"]
BUDGET_KEYS = ["found within budget, of findable", "found within budget, of findable towels",
               "found within budget, of findable other things", "cost per question among found",
               "ran out of budget", "occupied looks per search", "looks when found", "metres when found"]
MODEL_KEYS = ["steps decided by the model", "steps by fallback: lost call", "steps by fallback: unparseable",
              "steps by fallback: tried place"]
REFERENCE_FOR_FAKE = {"nearest": "last seen (nearest)", "distance": "distance order"}


def print_table(title: str, table: Dict[str, dict], keys: List[str], per_start: Optional[Dict[str, List[dict]]] = None) -> None:
    """Pooled row per policy, then one row per start under it. Columns are numbered and named in full above."""
    print(f"\n{title} (n = 1 household)")
    for i, k in enumerate(keys, 1):
        print(f"  [{i}] {k}")
    print(f"{'policy':38}" + "".join(f"{'[' + str(i) + ']':>9}" for i in range(1, len(keys) + 1)))
    for name, s in table.items():
        print(f"{name:38}" + "".join(f"{str(s.get(k)):>9}" for k in keys))
        for j, ps in enumerate(per_start.get(name, []) if per_start else []):
            print(f"  {'start ' + str(j):36}" + "".join(f"{str(ps.get(k)):>9}" for k in keys))


def same_searches(a: List[dict], b: List[dict]) -> List[str]:
    """The rows on which two policies' months differ, as one line each; empty when identical."""
    fields = ("start", "question", "outcome", "looks", "metres", "cost", "occupied_looks")
    rows_b = {(r["start"], r["question"]): r for r in b}
    differ = []
    for r in a:
        o = rows_b.get((r["start"], r["question"]))
        if o is None or any(r[f] != o[f] for f in fields):
            differ.append(f"start {r['start']} {r['question']} {r['thing']}: "
                          + ", ".join(f"{f} {r[f]} vs {o[f] if o else '-'}" for f in fields[2:] if o is None or r[f] != o[f]))
    return differ


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rig", default="go2")
    parser.add_argument("--perception", default="in view", choices=PERCEPTION_RULES)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--starts", type=int, default=5, help="how many different starting positions to average over")
    parser.add_argument("--occupied-penalty", type=float, default=0.0,
                        help="cost units added to a look into a room that holds a resident at that moment")
    parser.add_argument("--budget", default=None, help="one or more cost budgets per search, comma-separated, e.g. 30,60,120")
    parser.add_argument("--metres-per-look", type=float, default=5.0, help="a look costs this many metres' worth")
    parser.add_argument("--policies", default=None, help="comma-separated subset of policies to run (default: all, plus "
                                                         "'model' when --fake-model or --model is given)")
    parser.add_argument("--model", action="store_true", help="also run the model policy against the local server")
    parser.add_argument("--fake-model", choices=["nearest", "distance"], default=None,
                        help="run the model policy with a rule standing in for the model; no network")
    parser.add_argument("--stand", choices=["where last seen", "nearest"], default="where last seen",
                        help="where the robot stands inside the place the model names (see PolicyModel)")
    parser.add_argument("--show-prompt", type=int, default=None, metavar="N",
                        help="print the prompt(s) the model policy sends in search N (0-based) from start 0, then stop")
    args = parser.parse_args()
    costly = args.budget is not None or args.occupied_penalty or args.metres_per_look != 5.0
    budgets = [float(b) for b in args.budget.split(",")] if args.budget else [None]
    stored = Stored(HOME / "searchbench" / args.rig, args.perception)
    findable = sum(stored.findable(m["t"], m["asked_about"]) for m in stored.moments)
    unfindable_share = 1.0 - findable / len(stored.moments)
    print(f"{len(stored.known.positions)} positions, {len(stored.moments)} searches, perception: {args.perception}; "
          f"findable at the time asked: {findable} (n = 1 household)")
    if costly:
        print(f"costs: {args.metres_per_look:g} metres' worth per look, {args.occupied_penalty:g} per look into an occupied room, "
              f"budgets {args.budget or 'none'}")
    use_model = args.model or args.fake_model is not None or args.show_prompt is not None
    if use_model:
        print(f"model policy: {'fake ' + args.fake_model if args.fake_model else 'the local server'}, stands {args.stand}")
    client = make_client() if use_model and args.fake_model is None else None

    def new_model(show: bool = False) -> PolicyModel:
        return PolicyModel(args.fake_model, client, show=show, stand=args.stand, unfindable_share=unfindable_share)

    if args.show_prompt is not None:
        model = new_model(show=True)
        stored.moments = stored.moments[:args.show_prompt + 1]     # run up to and including that search
        costs = Costs(args.metres_per_look, args.occupied_penalty, budgets[0])
        rows = run(stored, "model", 0, 0, costs, model)
        last = rows[-1]
        steps = model.transcript[-len(last["decided_by"]):] if last["decided_by"] else []
        print(f"\nsearch {args.show_prompt}: {last['question']} for {last['thing']}, {last['looks']} look(s), outcome: {last['outcome']}"
              f"{'' if args.fake_model is None else ' (answers by the fake model ' + args.fake_model + ')'}")
        for i, step in enumerate(steps):
            print(f"\n===== step {i + 1}: messages sent =====")
            for m in step["messages"]:
                print(f"--- {m['role']} ---\n{m['content']}")
            print(f"--- enum sent for 'next' ---\n{json.dumps(step['enum'])}")
            print(f"--- answer ({step['by']}) ---\n{step['answer']}")
        print(f"\n===== response schema (at each step 'next' is pinned to the enum printed above) =====\n{json.dumps(SCHEMA, indent=1)}")
        return

    names = args.policies.split(",") if args.policies else list(POLICIES) + (["model"] if use_model else [])
    out = HOME / "searchbench" / args.rig
    for budget in budgets:
        costs = Costs(args.metres_per_look, args.occupied_penalty, budget)
        if budget is not None:
            print(f"\n################ budget {budget:g} ################")
        table, every, months, per_start = {}, [], {}, {}
        for name in names:
            model = new_model() if name == "model" else None
            runs = [[r for seed in range(args.seeds if name == "random" else 1) for r in run(stored, name, seed, start, costs, model)]
                    for start in range(args.starts)]
            months[name] = [r for rr in runs for r in rr]
            every += months[name]
            table[name] = summarise(months[name])
            per_start[name] = [summarise(rr) for rr in runs]
            table[name]["found, of findable: lowest and highest over starts"] = \
                [min(s["found, of findable"] for s in per_start[name]), max(s["found, of findable"] for s in per_start[name])]
            if budget is not None:
                table[name]["found within budget, of findable: lowest and highest over starts"] = \
                    [min(s["found within budget, of findable"] for s in per_start[name]),
                     max(s["found within budget, of findable"] for s in per_start[name])]
            table[name]["starts"] = args.starts
            if client is not None and model is not None:
                table[name]["model calls"] = dict(client.stats)
        # the paired comparison: every policy against the best rule row, at start 0
        rules_run = [n for n in names if n in RULES]
        if rules_run:
            best = max(rules_run, key=lambda n: table[n]["found within budget, of findable"] or 0)
            for name in names:
                table[name]["paired vs best rule, start 0"] = dict(paired(months[name], months[best]), **{"best rule": best})
        # the original results file is left alone whenever any costly-looks option is on
        stem = f"results_{args.perception.replace(' ', '_')}" + ("_costly" if costly or use_model else "")
        if budget is not None:
            stem += f"_budget{budget:g}"
        (out / f"{stem}.json").write_text(json.dumps({"summary": table, "searches": every}, indent=1))
        print_table("all searches" + (f", budget {budget:g}" if budget is not None else ""), table, BASE_KEYS, per_start)
        if costly:
            print_table(f"within the budget of {budget:g}" if budget is not None else "costs", table, BUDGET_KEYS, per_start)
        if rules_run:
            print(f"\npaired against the best rule, {best}, at start 0 (n = 1 household): "
                  "findable questions on which the two differ in finding within budget, and the net extra finds")
            for name in names:
                p = table[name]["paired vs best rule, start 0"]
                print(f"{name:38} discordant {p['discordant questions']:>4}   net extra finds {p['net extra finds']:>+4}")
        if "model" in table:
            print_table("the model policy's steps", {"model": table["model"]}, MODEL_KEYS)
        if args.fake_model and "model" in months and REFERENCE_FOR_FAKE[args.fake_model] in months:
            reference = REFERENCE_FOR_FAKE[args.fake_model]
            differ = same_searches(months["model"], months[reference])
            print(f"\nrequired check: model (fake {args.fake_model}) against {reference}: "
                  + ("identical on every search" if not differ else f"{len(differ)} of {len(months['model'])} searches differ"))
            for line in differ[:40]:
                print("  " + line)


if __name__ == "__main__":
    main()
