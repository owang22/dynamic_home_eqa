"""The hidden lab: places, people, objects, their routines and routine shifts. See ../README.md.

    world = make_world(Config(days=60, seed=0))
    world.person_place(name, t)      # place id, or None when the person is not in the lab
    world.object_place(name, t)      # place id, or None when the object is out of the lab

Time is epoch seconds (US/Pacific wall clock, so 09:00 means 09:00 in the lab). Everything is fixed by the seed.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")
HERE = Path(__file__).resolve().parent

# Stand-in for the lab's 16 places until cheetah sends places.json: name -> (x, y, kind, description).
# kind decides who uses a place: desk (one person each), sink, meeting, common, storage, entry.
DEFAULT_PLACES = {
    "dock": (0.0, 0.0, "entry", "floor by the lab door, where the dog starts"),
    "desk_1": (2.0, 1.5, "desk", "desk 1, by the window"),
    "desk_2": (2.0, 3.5, "desk", "desk 2"),
    "desk_3": (4.5, 1.5, "desk", "desk 3, by the printer"),
    "desk_4": (4.5, 3.5, "desk", "desk 4"),
    "desk_5": (7.0, 1.5, "desk", "desk 5, by the whiteboard"),
    "desk_6": (7.0, 3.5, "desk", "desk 6, the spare desk"),
    "meeting_table": (9.5, 2.5, "meeting", "the round meeting table"),
    "sink": (1.0, 5.5, "sink", "the sink and drying rack"),
    "kitchen_counter": (2.5, 5.8, "lunch", "the kitchen counter by the fridge"),
    "sofa": (5.0, 6.0, "common", "the small sofa by the wall"),
    "shelf_A": (8.0, 6.0, "storage", "bookcase A"),
    "rack_B": (10.0, 5.5, "storage", "the metal rack B"),
    "workbench": (11.5, 1.0, "common", "the workbench with the soldering station"),
    "cart": (11.5, 3.5, "storage", "the rolling cart"),
    "coat_rack": (0.5, 1.0, "entry", "the coat rack by the door"),
}

PEOPLE = [  # name, look (what the camera would say)
    ("Alice", "a person in a red hoodie"),
    ("Bob", "a tall person in a grey sweater"),
    ("Chen", "a person with glasses and a green jacket"),
    ("Dana", "a person in a denim jacket"),
    ("Eli", "a person in a black t-shirt"),
    ("Farah", "a person with a yellow scarf"),
]

# name, description, aliases the camera might use instead
OBJECTS = [
    ("mug_blue", "white mug with a blue stripe", ["white mug", "cup"]),
    ("mug_red", "red mug", ["red cup", "mug"]),
    ("backpack_black", "black backpack", ["black bag", "bag"]),
    ("backpack_green", "green backpack", ["green bag", "bag"]),
    ("laptop_silver", "silver laptop", ["laptop", "computer"]),
    ("umbrella_red", "red umbrella", ["umbrella"]),
    ("bottle_green", "green water bottle", ["water bottle", "bottle"]),
    ("bucket_blue", "blue plastic bucket", ["bucket", "blue bin"]),
    ("toy_dog", "stuffed toy dog", ["plush toy", "stuffed animal"]),
    ("cables_box", "cardboard box labelled CABLES", ["cardboard box", "box"]),
    ("multimeter", "yellow multimeter", ["meter", "yellow device"]),
    ("drill", "cordless drill", ["power drill", "tool"]),
    ("headphones", "black over-ear headphones", ["headphones", "headset"]),
    ("lunchbox", "orange lunch box", ["lunch box", "orange box"]),
    ("tripod", "camera tripod", ["tripod", "stand"]),
    ("projector", "small white projector", ["projector", "white box"]),
    ("plant", "potted plant", ["plant"]),
    ("helmet", "bike helmet", ["helmet"]),
    ("tape_roll", "roll of blue tape", ["tape"]),
    ("notebook_stack", "stack of lab notebooks", ["notebooks", "papers"]),
    ("speaker", "small bluetooth speaker", ["speaker"]),
    ("fan", "desk fan", ["fan"]),
    ("kettle", "electric kettle", ["kettle"]),
    ("whiteboard_markers", "cup of whiteboard markers", ["markers", "pens"]),
]

# routine type -> how many objects get it (scaled to n_objects); "owner" types need a person
ROUTINE_MIX = [
    ("fixed", 4), ("weekday", 3), ("rotation", 2), ("follows_owner", 4), ("use_return", 2),
    ("drift", 3), ("away_days", 2), ("meeting", 1), ("random", 2),
]
# routines that only make sense for some objects; anything else gets a place-based routine
SUITS = {
    "follows_owner": {"backpack_black", "backpack_green", "laptop_silver", "umbrella_red", "helmet", "headphones"},
    "use_return": {"mug_blue", "mug_red", "lunchbox", "bottle_green"},
    "meeting": {"projector", "whiteboard_markers", "speaker", "notebook_stack"},
}
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass
class Config:
    days: int = 60
    seed: int = 0
    start: str = "2026-11-02"                 # a Monday
    n_people: int = 5
    n_objects: int = 20
    shifts: int = 2                           # routine shift days, spread over the run
    off_routine: float = 0.05                 # per object per lab day: put somewhere else for the day
    out_of_lab: float = 0.02                  # per object per lab day: taken out for the day
    absent: float = 0.05                      # per person per weekday: sick or travelling
    places_file: str | None = None            # JSON {name: {"x":..,"y":..,"kind":..,"desc":..}} or None


@dataclass
class Person:
    name: str
    look: str
    desks: list               # [(from_day, desk)] desk changes at shifts
    arrive: float             # usual arrival, hours
    leave: float              # usual departure, hours
    wfh: list                 # weekday numbers (0=Mon) worked from home
    off_days: set = field(default_factory=set)
    times: dict = field(default_factory=dict)   # day -> (arrive_h, leave_h) or None


@dataclass
class Obj:
    name: str
    desc: str
    aliases: list
    regimes: list             # [(from_day, routine dict)]; routine = {"type", "places", "owner", ...}


REAL_PLACES = HERE.parents[1] / "go2" / "memory_lab" / "places_2026-10-25.json"
# kinds for the real lab's places, by id (anything else: desk_* is a desk, the rest common)
REAL_KINDS = {"door_outside": "entry", "door_stairwell": "entry", "conference_table": "meeting",
              "water_cooler": "sink", "sofa": "lunch"}


def load_places(path):
    """The stand-in places (path None) or a lab places file: a list of {"id", "x", "y", "target": {"x", "y"}}
    as in go2/memory_lab/places_2026-10-25.json, or a dict {name: {"x", "y", "kind", "desc"}}."""
    if not path:
        return {k: {"x": v[0], "y": v[1], "kind": v[2], "desc": v[3], "target": None}
                for k, v in DEFAULT_PLACES.items()}
    raw = json.loads(Path(path).read_text())
    if isinstance(raw, dict):
        return {k: {"x": v["x"], "y": v["y"], "kind": v.get("kind", "common"), "desc": v.get("desc", k),
                    "target": v.get("target")} for k, v in raw.items()}
    out = {}
    for p in raw:
        pid = p["id"]
        kind = REAL_KINDS.get(pid, "desk" if pid.startswith("desk_") else "common")
        desc = f"{pid[5:].capitalize()}'s desk" if kind == "desk" else pid.replace("_", " ")
        out[pid] = {"x": p["x"], "y": p["y"], "kind": kind, "desc": desc, "target": p.get("target")}
    return out


class World:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.rng = random.Random(f"lab-history-{cfg.seed}")
        self.places = load_places(cfg.places_file)
        self.start = dt.datetime.fromisoformat(cfg.start).replace(tzinfo=TZ)
        assert self.start.weekday() == 0, "start must be a Monday"
        self.shift_days = sorted({round(cfg.days * (k + 1) / (cfg.shifts + 1)) for k in range(cfg.shifts)})
        self.people = self._make_people()
        self.objects = self._make_objects()
        self._apply_shifts()
        self._daily = {}       # (obj, day) -> place placed that morning (rule + noise), None = out
        self._noise = {}       # (obj, day) -> "moved" / "out" / None
        self._roll_days()

    def role(self, kind):
        """The first place of a kind (meeting, sink, lunch, entry), or None if the lab has none."""
        return next((p for p, v in self.places.items() if v["kind"] == kind), None)

    # ---- calendar ----------------------------------------------------------------------------
    def day_start(self, day):
        """Epoch seconds of 00:00 on run day `day` (day 0 is the start Monday)."""
        return (self.start + dt.timedelta(days=day)).timestamp()

    def day_of(self, t):
        return (dt.datetime.fromtimestamp(t, TZ).date() - self.start.date()).days

    def hour_of(self, t):
        d = dt.datetime.fromtimestamp(t, TZ)
        return d.hour + d.minute / 60 + d.second / 3600

    def weekday(self, day):
        return (self.start + dt.timedelta(days=day)).weekday()

    def is_workday(self, day):
        return self.weekday(day) < 5

    def lab_day_index(self, day):
        """How many workdays came before this day (for rotations, which skip weekends)."""
        weeks, k = divmod(day, 7)
        return weeks * 5 + min(k, 5)

    # ---- people ------------------------------------------------------------------------------
    def _make_people(self):
        rng = self.rng
        desks = [p for p, v in self.places.items() if v["kind"] == "desk"]
        assert len(desks) >= self.cfg.n_people, "need one desk per person"
        rng.shuffle(desks)
        people = []
        for i, (name, look) in enumerate(PEOPLE[:self.cfg.n_people]):
            wfh = rng.sample(range(5), rng.choice([0, 0, 1, 1, 2]))
            p = Person(name, look, [(0, desks[i])], rng.uniform(8.0, 10.5), 0.0, wfh)
            p.leave = p.arrive + rng.uniform(7.5, 9.5)
            people.append(p)
        self.spare_desks = desks[self.cfg.n_people:]
        for p in people:
            for day in range(self.cfg.days):
                wd = self.weekday(day)
                if wd >= 5 or wd in p.wfh or rng.random() < self.cfg.absent:
                    p.times[day] = None
                    continue
                a = p.arrive + rng.gauss(0, 0.4)
                p.times[day] = (a, max(a + 3, p.leave + rng.gauss(0, 0.6)))
        return people

    def person(self, name):
        return next(p for p in self.people if p.name == name)

    def desk_of(self, p: Person, day):
        return [d for fr, d in p.desks if fr <= day][-1]

    def person_place(self, name, t):
        p = self.person(name)
        day, h = self.day_of(t), self.hour_of(t)
        times = p.times.get(day)
        if not times or not (times[0] <= h < times[1]):
            return None
        if self.weekday(day) == 1 and 14 <= h < 15:          # group meeting, Tuesdays 14:00
            return self.role("meeting") or self.desk_of(p, day)
        if 12.25 <= h < 12.75 and self.role("lunch"):                  # lunch
            return self.role("lunch")
        return self.desk_of(p, day)

    # ---- objects -----------------------------------------------------------------------------
    def _make_objects(self):
        rng = self.rng
        pool = OBJECTS[:]
        rng.shuffle(pool)
        pool = pool[:self.cfg.n_objects]
        total = sum(n for _, n in ROUTINE_MIX)
        slots = []
        for t, n in ROUTINE_MIX:
            slots += [t] * max(1, round(n * self.cfg.n_objects / total))
        rng.shuffle(slots)
        slots = (slots + ["fixed"] * len(pool))[:len(pool)]
        # special routines go only to objects they suit; the rest get place-based routines
        assigned, left = [], pool[:]
        for t in ("follows_owner", "use_return", "meeting"):
            want = slots.count(t)
            fits = [o for o in left if o[0] in SUITS[t]][:want]
            assigned += [(o, t) for o in fits]
            left = [o for o in left if o not in fits]
        plain = [s for s in slots if s not in SUITS]
        plain += [rng.choice(["fixed", "weekday", "drift"]) for _ in range(len(left) - len(plain))]
        assigned += list(zip(left, plain))
        return [Obj(n, d, a, [(0, self._routine(t))]) for (n, d, a), t in assigned]

    def _routine(self, t, avoid=()):
        rng = self.rng
        P = [p for p in self.places if p not in avoid and self.places[p]["kind"] != "entry"]
        if t == "fixed":
            return {"type": t, "places": rng.sample(P, 1)}
        if t in ("weekday", "away_days"):
            r = {"type": t, "places": rng.sample(P, 2 if t == "weekday" else 1)}
            r["days"] = sorted(rng.sample(range(5), 2))
            return r
        if t in ("rotation", "random"):
            return {"type": t, "places": rng.sample(P, 3)}
        if t in ("follows_owner", "use_return"):
            r = {"type": t, "owner": rng.choice(self.people).name}
            if t == "use_return":
                r["places"] = [self.role("sink") or rng.choice(P)]
            return r
        if t == "drift":
            return {"type": t, "places": rng.sample(P, 1), "p": 0.3}
        if t == "meeting":
            room = self.role("meeting") or rng.choice(P)
            return {"type": t, "places": [rng.choice([p for p in P if p != room]), room]}
        raise ValueError(t)

    def _apply_shifts(self):
        """On each shift day: one person moves desks, and two objects with a place-based routine get new places."""
        rng = self.rng
        self.shift_log = []
        for day in self.shift_days:
            if self.spare_desks:
                p = rng.choice(self.people)
                old, new = self.desk_of(p, day), self.spare_desks.pop()
                p.desks.append((day, new))
                self.spare_desks.append(old)
                self.shift_log.append({"day": day, "who": p.name, "kind": "desk",
                                       "text": f"{p.name} moves from {old} to {new}"})
            movable = [o for o in self.objects
                       if self.regime(o, day)["type"] in ("fixed", "weekday", "rotation", "away_days", "drift")]
            for o in rng.sample(movable, min(2, len(movable))):
                r_old = self.regime(o, day)
                r_new = self._routine(r_old["type"], avoid=set(r_old["places"]))
                o.regimes.append((day, r_new))
                self.shift_log.append({"day": day, "who": o.name, "kind": "routine",
                                       "text": f"{o.name}: was {self.describe(r_old)}; now {self.describe(r_new)}"})

    def regime(self, o: Obj, day):
        return [r for fr, r in o.regimes if fr <= day][-1]

    def _roll_days(self):
        """Morning placement for every place-based object and workday; drift keeps its own walk."""
        rng = self.rng
        drift_at = {}
        for day in range(self.cfg.days):
            if not self.is_workday(day):
                continue
            for o in self.objects:
                r = self.regime(o, day)
                t, P = r["type"], r.get("places", [])
                if t == "fixed":
                    place = P[0]
                elif t == "weekday":
                    place = P[1] if self.weekday(day) in r["days"] else P[0]
                elif t == "away_days":
                    place = None if self.weekday(day) in r["days"] else P[0]
                elif t == "rotation":
                    place = P[self.lab_day_index(day) % 3]
                elif t == "random":
                    place = rng.choice(P)
                elif t == "drift":
                    cur = drift_at.get(o.name) if drift_at.get(o.name) is not None else P[0]
                    if self._regime_started(o, day):
                        cur = P[0]
                    if rng.random() < r["p"]:
                        cur = rng.choice(self.neighbours(cur, 3))
                    drift_at[o.name] = place = cur
                else:          # owner-driven and meeting objects are placed through the day, not here
                    place = "_dynamic"
                noise = None
                u = rng.random()
                if place != "_dynamic":
                    if u < self.cfg.out_of_lab:
                        place, noise = None, "out"
                    elif u < self.cfg.out_of_lab + self.cfg.off_routine:
                        others = [p for p in self.places if p != place and self.places[p]["kind"] != "entry"]
                        place, noise = rng.choice(others), "moved"
                self._daily[(o.name, day)] = place
                self._noise[(o.name, day)] = noise

    def _regime_started(self, o, day):
        return any(fr == day and fr > 0 for fr, _ in o.regimes)

    def neighbours(self, place, k):
        x, y = self.places[place]["x"], self.places[place]["y"]
        d = sorted((math.hypot(v["x"] - x, v["y"] - y), p) for p, v in self.places.items()
                   if p != place and v["kind"] != "entry")
        return [p for _, p in d[:k]]

    def _last_workday(self, day):
        while day >= 0 and not self.is_workday(day):
            day -= 1
        return day

    def object_place(self, name, t):
        o = next(o for o in self.objects if o.name == name)
        day, h = self.day_of(t), self.hour_of(t)
        r = self.regime(o, day)
        if r["type"] == "follows_owner":
            p = self.person(r["owner"])
            if self.person_place(p.name, t) is None:
                return None
            return self.desk_of(p, day)         # left at the desk during lunch and meetings
        if r["type"] == "use_return":
            return self._use_return(o, r, day, h)
        if r["type"] == "meeting":
            home, room = r["places"]
            on = self.weekday(day) == 1 and 13.75 <= h < 15.25
            return room if on else home
        # place-based: the morning placement holds from 07:00 until 07:00 on the next workday
        d = day if (self.is_workday(day) and h >= 7) else self._last_workday(day - 1)
        if d < 0:              # before the first workday's 07:00: where that day starts
            d = self._next_workday(0)
        return self._daily[(name, d)]

    def _next_workday(self, day):
        while not self.is_workday(day):
            day += 1
        return day

    def _use_return(self, o, r, day, h):
        """At the owner's desk from arrival until lunch ends (12:45); at the sink the rest of the time."""
        p = self.person(r["owner"])
        times = p.times.get(day)
        if times and times[0] <= h < min(times[1], 12.75):
            return self.desk_of(p, day)
        return r["places"][0]

    # ---- text --------------------------------------------------------------------------------
    def describe(self, r):
        t, P = r["type"], r.get("places", [])
        days = ", ".join(WEEKDAYS[d] for d in r.get("days", []))
        return {
            "fixed": lambda: f"always at {P[0]}",
            "weekday": lambda: f"at {P[1]} on {days}; otherwise at {P[0]}",
            "away_days": lambda: f"out of the lab on {days}; otherwise at {P[0]}",
            "rotation": lambda: f"rotates {P[0]} -> {P[1]} -> {P[2]}, one step each workday",
            "random": lambda: f"at one of {', '.join(P)} at random each workday",
            "drift": lambda: f"starts at {P[0]} and moves to a nearby place on about {round(r['p'] * 100)}% of workdays",
            "follows_owner": lambda: f"comes and goes with {r['owner']}; at {r['owner']}'s desk while they are in",
            "use_return": lambda: f"at {r['owner']}'s desk in the morning, at {P[0]} from after lunch until "
                                  f"{r['owner']} comes in next",
            "meeting": lambda: f"at {P[0]}, taken to {P[1]} for the Tuesday 14:00 group meeting",
        }[t]()

    def routines(self):
        return {
            "places": self.places,
            "people": [{"name": p.name, "look": p.look, "desks": p.desks, "arrive_h": round(p.arrive, 2),
                        "leave_h": round(p.leave, 2), "wfh": [WEEKDAYS[d] for d in p.wfh]} for p in self.people],
            "objects": [{"name": o.name, "desc": o.desc, "regimes": [
                {"from_day": fr, **r, "text": self.describe(r)} for fr, r in o.regimes]} for o in self.objects],
            "shift_days": self.shift_days,
            "shifts": self.shift_log,
            "noise_days": {o.name: {d: n for (name, d), n in self._noise.items() if name == o.name and n}
                           for o in self.objects},
        }


def make_world(cfg: Config) -> World:
    return World(cfg)
