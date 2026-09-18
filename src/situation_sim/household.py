"""Household sampler: residents, rooms, receptacles, objects, traits, groups.

Everything is sampled from code with one seeded ``random.Random``; no LLM
authoring and no per-household YAML. Ids follow the existing bank
conventions (``counter_k1``, ``nightstand_b1``, ``laptop_marco``,
``ON_PERSON``, ``OUT_OF_HOUSE``).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

from situation_sim import timing_constants as tc

ON_PERSON = "ON_PERSON"
OUT_OF_HOUSE = "OUT_OF_HOUSE"

# Receptacle kinds per room kind: (kind, capacity). Suffix letters follow
# the old banks (k = kitchen, l = living, e = entry, ba = bathroom,
# b = bedroom, o = office, d = dining).
ROOM_RECEPTACLES = {
    "kitchen": ("k", [("counter", 5), ("sink", 4), ("cupboard", 8),
                      ("dish_rack", 4), ("kitchen_table", 6), ("chair", 2)]),
    "living": ("l", [("couch", 4), ("coffee_table", 4), ("tv_stand", 3),
                     ("bookshelf", 8), ("armchair", 2)]),
    "entry": ("e", [("entry_table", 6), ("entry_hook", 4), ("entry_floor", 6)]),
    "bathroom": ("ba", [("bathroom_shelf", 5), ("towel_rack", 3),
                        ("medicine_cabinet", 6)]),
    "bedroom": ("b", [("bed", 3), ("nightstand", 4), ("desk", 4),
                      ("bedroom_floor", 6), ("wardrobe", 8)]),
    "office": ("o", [("desk", 4), ("office_shelf", 8), ("office_chair", 2)]),
    "dining": ("d", [("dining_table", 6), ("sideboard", 5)]),
}

# Which object classes each receptacle kind can hold. Used for whim and
# alternative candidates and for the allowed set each object is checked
# against (a home slot is always allowed). A kind absent here takes anything.
_SMALL = {"phone", "keys", "wallet", "glasses", "medication", "charger", "headphones",
          "remote", "book", "notebook", "mug", "water_bottle", "lunchbox"}
_DISHES = {"mug", "water_bottle", "lunchbox", "watering_can"}
ACCEPTS = {
    "nightstand": _SMALL,
    "entry_table": _SMALL | {"handbag", "umbrella"},
    "entry_hook": {"jacket", "backpack", "handbag", "umbrella", "keys", "gym_bag"},
    "entry_floor": {"shoes", "backpack", "handbag", "gym_bag", "umbrella", "laundry_basket",
                    "watering_can"},
    "desk": _SMALL | {"laptop", "handbag", "backpack"},
    "office_chair": {"handbag", "backpack", "jacket", "book", "notebook", "laptop", "phone",
                     "blanket", "towel", "gym_bag"},
    "chair": {"handbag", "backpack", "jacket", "book", "notebook", "laptop", "phone",
              "blanket", "towel", "gym_bag"},
    "coffee_table": _SMALL | {"laptop", "blanket"},
    "couch": _SMALL | {"laptop", "blanket", "jacket", "towel", "handbag", "backpack"},
    "armchair": _SMALL | {"laptop", "blanket", "jacket", "towel", "handbag", "backpack"},
    "tv_stand": _SMALL | {"laptop"},
    "bookshelf": _SMALL | {"laptop", "watering_can"},
    "office_shelf": _SMALL | {"laptop", "watering_can"},
    "bed": _SMALL | {"laptop", "blanket", "towel", "jacket"},
    "wardrobe": {"jacket", "shoes", "backpack", "handbag", "gym_bag", "towel", "blanket",
                 "umbrella", "laundry_basket"},
    "kitchen_table": _SMALL | {"laptop", "handbag", "backpack", "watering_can"},
    "dining_table": _SMALL | {"laptop", "handbag", "backpack", "watering_can"},
    "sideboard": _SMALL | {"laptop", "watering_can"},
    "counter": _SMALL | {"watering_can", "handbag"},
    "sink": _DISHES,
    "dish_rack": _DISHES,
    "cupboard": _DISHES | {"medication"},
    "bathroom_shelf": _SMALL | {"towel", "laundry_basket", "blanket"},
    "towel_rack": {"towel", "jacket"},
    "medicine_cabinet": {"medication", "glasses"},
    # bedroom_floor takes anything
}


def accepts(kind: str, cls: str) -> bool:
    ok = ACCEPTS.get(kind)
    return ok is None or cls in ok


FIRST_NAMES = ["marco", "priya", "elena", "tomas", "aisha", "leo", "nora",
               "sam", "ines", "kwame", "yuki", "dana"]

ROLES = ["worker_out", "worker_home", "retired"]
FORGET_LEVELS = ["rarely", "sometimes", "often"]


@dataclass
class Receptacle:
    id: str
    kind: str
    room: str
    capacity: int


@dataclass
class Resident:
    id: str
    name: str
    role: str
    bedroom: str            # room id
    workspace: str          # room id used for work_session
    tidiness: float         # 0 (leaves things everywhere) .. 1 (always puts back)
    jitter_scale: float     # punctuality multiplier on jitter sigmas
    forget_level: str
    forget_p: float
    mood_sensitivity: float  # how strongly internal state moves behaviour
    base_energy: float
    base_hurry: float
    base_distraction: float


@dataclass
class Obj:
    id: str
    cls: str
    owner: Optional[str]     # resident id or None for shared
    home: List[str]          # receptacle ids, primary first
    pocket: bool = False     # phone/keys/wallet: taken on trips out
    outdoor: bool = False    # shoes/jacket/umbrella: worn on trips out
    group: Optional[str] = None   # group name (bag_<res>, gym_<res>) or None
    after_use: Optional[str] = None   # where a used one goes (a dirty mug: the sink)
    allowed: List[str] = field(default_factory=list)


@dataclass
class Group:
    name: str
    kind: str                # "bag" or "gym"
    owner: str
    leader: str              # object id
    members: List[str]       # object ids that ride inside the leader


@dataclass
class Household:
    id: str
    seed: int
    household_type: str
    rooms: List[str]
    receptacles: Dict[str, Receptacle]
    residents: Dict[str, Resident]
    objects: Dict[str, Obj]
    groups: Dict[str, Group]

    # ---- lookups -------------------------------------------------------
    def recs_in(self, room: str) -> List[Receptacle]:
        return sorted((r for r in self.receptacles.values() if r.room == room),
                      key=lambda r: r.id)

    def rec_of_kind(self, kind: str, room: Optional[str] = None) -> Optional[str]:
        cands = sorted(r.id for r in self.receptacles.values()
                       if r.kind == kind and (room is None or r.room == room))
        return cands[0] if cands else None

    def has_room(self, kind: str) -> Optional[str]:
        rooms = sorted(r for r in self.rooms if r.split("_")[0] == kind)
        return rooms[0] if rooms else None

    def objects_of(self, resident: Optional[str]) -> List[Obj]:
        return sorted((o for o in self.objects.values() if o.owner == resident),
                      key=lambda o: o.id)

    def to_json(self) -> dict:
        return {
            "id": self.id, "seed": self.seed,
            "household_type": self.household_type,
            "rooms": list(self.rooms),
            "receptacles": {k: asdict(v) for k, v in sorted(self.receptacles.items())},
            "residents": {k: asdict(v) for k, v in sorted(self.residents.items())},
            "objects": {k: asdict(v) for k, v in sorted(self.objects.items())},
            "groups": {k: asdict(v) for k, v in sorted(self.groups.items())},
        }


def _u(rng: random.Random, lo: float, hi: float) -> float:
    return round(rng.uniform(lo, hi), 3)


def sample_household(seed: int, hh_id: Optional[str] = None) -> Household:
    rng = random.Random(f"household:{seed}")
    hh_id = hh_id or f"hh_s{seed}"

    # --- residents and rooms -------------------------------------------
    n_res = rng.choice([2, 2, 3])
    if n_res == 2:
        household_type = rng.choice(["couple", "couple", "flatmates"])
    else:
        household_type = rng.choice(["couple_plus_one", "flatmates"])
    names = rng.sample(FIRST_NAMES, n_res)

    rooms = ["kitchen", "living", "entry", "bathroom"]
    if household_type == "couple":
        bedrooms = ["bedroom_1"]
        res_bedroom = ["bedroom_1", "bedroom_1"]
    elif household_type == "couple_plus_one":
        bedrooms = ["bedroom_1", "bedroom_2"]
        res_bedroom = ["bedroom_1", "bedroom_1", "bedroom_2"]
    else:
        bedrooms = [f"bedroom_{i + 1}" for i in range(n_res)]
        res_bedroom = list(bedrooms)
    rooms += bedrooms
    if rng.random() < 0.55:
        rooms.append("office")
    if len(rooms) < 8 and rng.random() < 0.45:
        rooms.append("dining")
    rooms = sorted(rooms)

    receptacles: Dict[str, Receptacle] = {}
    for room in rooms:
        kind = room.split("_")[0]
        suffix, recs = ROOM_RECEPTACLES[kind]
        idx = room.split("_")[1] if "_" in room else "1"
        for rkind, cap in recs:
            rid = f"{rkind}_{suffix}{idx}"
            receptacles[rid] = Receptacle(rid, rkind, room, cap)

    residents: Dict[str, Resident] = {}
    roles = []
    for i in range(n_res):
        # at least one worker so the house empties on weekdays
        role = rng.choices(ROLES, weights=[0.5, 0.3, 0.2])[0]
        roles.append(role)
    if all(r == "retired" for r in roles):
        roles[0] = "worker_out"
    office = "office" if "office" in rooms else None
    for i, name in enumerate(names):
        rid = f"resident_{i + 1}"
        fl = rng.choices(FORGET_LEVELS, weights=[0.4, 0.4, 0.2])[0]
        residents[rid] = Resident(
            id=rid, name=name, role=roles[i], bedroom=res_bedroom[i],
            workspace=(office if office and roles[i] == "worker_home" else res_bedroom[i]),
            tidiness=_u(rng, 0.25, 0.95),
            # punctuality: lognormal around 1, hard-bounded to the old file's range
            jitter_scale=round(min(tc.JITTER_SCALE_MAX, max(tc.JITTER_SCALE_MIN,
                                   rng.lognormvariate(0.0, 0.3))), 3),
            forget_level=fl, forget_p=tc.FORGET_LEVELS[fl],
            mood_sensitivity=_u(rng, 0.2, 1.0),
            base_energy=_u(rng, 0.35, 0.75),
            base_hurry=_u(rng, 0.25, 0.65),
            base_distraction=_u(rng, 0.2, 0.6),
        )
    # two worker_home residents would both want the office desk: give the
    # second one their bedroom desk
    seen_office = False
    for r in sorted(residents.values(), key=lambda r: r.id):
        if r.workspace == "office":
            if seen_office:
                r.workspace = r.bedroom
            seen_office = True

    hh = Household(hh_id, seed, household_type, rooms, receptacles,
                   residents, {}, {})

    # --- objects ---------------------------------------------------------
    def rec(kind: str, room: Optional[str] = None) -> str:
        r = hh.rec_of_kind(kind, room)
        assert r is not None, (kind, room)
        return r

    objects: Dict[str, Obj] = {}
    groups: Dict[str, Group] = {}

    def add(cls: str, owner: Optional[str], home: List[str], **kw) -> Obj:
        oid = f"{cls}_{residents[owner].name}" if owner else f"{cls}_shared"
        o = Obj(oid, cls, owner, home, **kw)
        objects[oid] = o
        return o

    for rid, res in sorted(residents.items()):
        bd = res.bedroom
        ws = res.workspace
        worker = res.role in ("worker_out", "worker_home")
        add("phone", rid, [rec("nightstand", bd), rec("coffee_table")], pocket=True)
        add("keys", rid, [rec("entry_table"), rec("nightstand", bd)], pocket=True)
        add("wallet", rid, [rng.choice([rec("entry_table"), rec("nightstand", bd)]),
                            rec("desk", ws)], pocket=True)
        add("jacket", rid, [rec("entry_hook"), rec("wardrobe", bd)], outdoor=True)
        add("shoes", rid, [rec("entry_floor"), rec("wardrobe", bd)], outdoor=True)
        if rng.random() < 0.75:
            add("umbrella", rid, [rec("entry_floor"), rec("entry_hook")], outdoor=True)
        add("mug", rid, [rec("cupboard"), rec("dish_rack"), rec("sink")], after_use=rec("sink"))
        if rng.random() < 0.8:
            add("book", rid, [rec("nightstand", bd), rec("bookshelf")])
        if rng.random() < 0.45:
            add("glasses", rid, [rec("nightstand", bd), rec("desk", ws)])
        if rng.random() < 0.35:
            add("medication", rid, [rec("medicine_cabinet"), rec("nightstand", bd)])
        add("towel", rid, [rec("towel_rack"), rec("bathroom_shelf")])
        bag_members: List[str] = []
        if worker:
            lap = add("laptop", rid, [rec("desk", ws), rec("bookshelf")])
            bag_members.append(lap.id)
            if rng.random() < 0.7:
                bag_members.append(add("charger", rid, [rec("desk", ws), rec("nightstand", bd)]).id)
            if rng.random() < 0.5:
                bag_members.append(add("notebook", rid, [rec("desk", ws), rec("bookshelf")]).id)
        if rng.random() < 0.6:
            hp = add("headphones", rid, [rec("desk", ws), rec("nightstand", bd)])
            if worker and rng.random() < 0.6:
                bag_members.append(hp.id)
        if rng.random() < 0.7:
            wb = add("water_bottle", rid, [rec("dish_rack"), rec("counter"), rec("sink")], after_use=rec("sink"))
            if worker and rng.random() < 0.6:
                bag_members.append(wb.id)
        if res.role == "worker_out" and rng.random() < 0.6:
            bag_members.append(add("lunchbox", rid, [rec("cupboard"), rec("counter"), rec("sink")], after_use=rec("sink")).id)
        if res.role == "worker_out":
            bag_cls = rng.choice(["backpack", "handbag"])
            bag = add(bag_cls, rid, [rec("entry_hook"), rec("bedroom_floor", bd), rec("desk", ws)])
            gname = f"bag_{res.name}"
            # group membership sampled per household: each candidate rides
            # in the bag with p 0.75, otherwise it is carried loose / stays
            members = sorted(m for m in bag_members if rng.random() < 0.75)
            groups[gname] = Group(gname, "bag", rid, bag.id, members)
            bag.group = gname
            for m in members:
                objects[m].group = gname
        if rng.random() < 0.4:
            gym = add("gym_bag", rid, [rec("wardrobe", bd), rec("bedroom_floor", bd)])
            gname = f"gym_{res.name}"
            members = sorted(o.id for o in objects.values()
                             if o.owner == rid and o.cls in ("water_bottle", "headphones")
                             and o.group is None and rng.random() < 0.6)
            groups[gname] = Group(gname, "gym", rid, gym.id, members)
            gym.group = gname
            for m in members:
                objects[m].group = gname
    # shared objects
    add("remote", None, [rec("tv_stand"), rec("coffee_table")])
    add("blanket", None, [rec("couch"), rec("armchair")])
    add("laundry_basket", None, [rec("bathroom_shelf"), rec("bedroom_floor", "bedroom_1")])
    if rng.random() < 0.6:
        add("watering_can", None, [rec("cupboard"), rec("counter")])

    hh.objects = dict(sorted(objects.items()))
    hh.groups = dict(sorted(groups.items()))
    return hh


def bag_kind(obj: Obj) -> bool:
    return obj.cls in ("backpack", "handbag")
