"""The truth of the home: where every object is and what each resident holds.

Every object is in exactly one spot:
  {"at": "place",  "place": p, "rel": r, "ref": o or None}   r is inside, on_top, under or
                                                              next_to; the reference is the
                                                              object o, or the place itself
  {"at": "hand",   "person": rid}                              in a hand (two each)
  {"at": "pocket", "person": rid}
  {"at": "worn",   "person": rid}                              clothes, shoes, a watch, a backpack on
  {"at": "inside", "carrier": o}                              in a bag, box or basket
Anything can go inside anything (a bookmark in a book, an infuser in a mug, a
pouch in a backpack), except into itself or into something already inside it.
An object's carrier kind only decides whether what is inside it can be seen:
closed and pockets hide it; open and none do not. pocket puts a thing into the
pockets of what the resident wears; taking those clothes off leaves it there. Moving a carrier
moves what is inside it. A resident who leaves the house takes what they hold,
their pockets, and what is inside the carriers they hold.

A position is hidden from someone standing in the room when it is inside a
closed container (a closed place, or a bag, box or pocket), or under something
(including under the place itself, such as under the bed), or resting on or next
to something hidden. Everything else is visible. Residents see hidden positions
only at the place they stand at, and see inside a closed carrier only when they
hold it.

Clothes get dirty when worn for a day and clean again when washed: anything
inside a washing machine when someone spends time at it.

Each resident keeps their own memory of where they last saw each object, which
is out of date when someone else moved it.
"""
from __future__ import annotations

import collections
from dataclasses import dataclass, field
from typing import Optional

from lived_home.layout import CLOSED, OPEN, SURFACE, Layout

HANDS = 2
POCKET_SLOTS = 5
RELATIONS = ["inside", "on_top", "under", "next_to"]
FOOTPRINT = {"small": 0.01, "medium": 0.04, "large": 0.12}   # m^2 an object takes on a spot
DEPTH = 4.0        # a drawer, cupboard or basin holds this many times its floor area
HIDING_RELATIONS = {"under"}
WASHABLE = ("shirt", "t-shirt", "blouse", "trousers", "pants", "jeans", "shorts", "socks",
            "underwear", "bra", "leggings", "sweater", "hoodie", "sweatshirt", "cardigan",
            "dress", "skirt", "polo", "joggers")
CARRIER_KINDS = ["none", "open", "closed", "pockets"]   # pockets: clothes with pockets
SHUT = ("closed", "pockets")                               # contents not seen from outside


def clock(minute: int) -> str:
    return f"{(minute // 60) % 24:02d}:{minute % 60:02d}"


def at_place(place: str, rel: str = "on_top", ref: Optional[str] = None) -> dict:
    return {"at": "place", "place": place, "rel": rel, "ref": ref}


def washable(type_: str) -> bool:
    words = type_.lower().replace("-", " ").split()
    return any(w in words or type_.lower().endswith(w) for w in WASHABLE) and \
        not any(w in type_.lower() for w in ("sleep", "pajama", "pyjama", "robe"))


SLEEPWEAR = ("sleep", "pajama", "pyjama", "nightgown", "nightdress", "nightshirt")
UNDER = ("underwear", "bra", "socks", "tights", "undershirt", "boxers", "briefs")
BOTTOMS = ("trousers", "pants", "jeans", "shorts", "joggers", "sweatpants", "chinos")


OVER = ("hoodie", "cardigan", "sweatshirt", "sweater", "jumper", "fleece", "robe", "lounge")


def is_sleepwear(type_: str) -> bool:
    t = type_.lower()
    return any(w in t for w in SLEEPWEAR) and "mask" not in t


def is_daywear(type_: str) -> bool:
    """Day clothes that cannot go over or under sleepwear (underwear and socks can,
    and a hoodie or cardigan over pajamas is ordinary)."""
    t = type_.lower()
    return washable(t) and not any(w in t for w in UNDER + OVER)


def is_bottoms(type_: str) -> bool:
    t = type_.lower()
    return not is_sleepwear(t) and any(t.endswith(w) or f"{w} " in t for w in BOTTOMS)


# Where a thing is kept ("its home") is where it started, unless it started on a
# spot people drop things on rather than keep them: a floor, a bed or seat (not
# their shelves or drawers), a basin or tub, a washer drum, a stovetop.
# Exceptions: large things and shoes live on floors, bedding and cushions on beds
# and seats, soap, sponges and shampoo in basins and on shower floors.
FLOOR_DWELLERS = ("shoe", "boot", "sneaker", "trainer", "slipper", "sandal", "flats", "heels",
                  "loafer", "clog", "basket", "hamper", "bin", "rug", "mat", "dumbbell",
                  "kettlebell", "toilet brush", "umbrella")
BED_DWELLERS = ("pillow", "duvet", "blanket", "throw", "cushion", "comforter", "quilt",
                "sheet", "bedspread")
SINK_DWELLERS = ("sponge", "soap", "brush", "scrubber", "shampoo", "conditioner", "body wash",
                 "face wash", "loofah")
SEATS = ("mattress", "bed", "sofa", "couch", "sectional", "seat", "chair", "stool", "bench",
         "ottoman", "armchair")
STORAGE = ("shelf", "drawer", "compartment", "cabinet", "cubby", "storage", "rack", "hook")
WET = ("sink", "basin", "tub", "bathtub")         # only the basin itself, not a counter or edge
PASSING = ("drum", "hamper", "laundry basket")     # things pass through, nothing lives there
HOT = ("stove", "stovetop", "burner", "hob", "cooktop")


def _spot_words(place) -> str:
    """The spot's own words, without 'by the ottoman' or 'near the bed' (a
    nightstand by the bed is not a bed)."""
    import re
    cut = lambda x: re.split(r"\b(?:by|near|next to|beside|under|across from)\b", x.lower())[0]
    return f" {cut(place.furniture)} {cut(place.name)} "


def _has(words: str, w: str) -> bool:
    import re
    return re.search(rf"\b{re.escape(w)}s?\b", words) is not None


def _drop_kind(place, rel: str = "") -> str:
    """'floor', 'seat', 'wet', 'hot', 'passing' for a spot people drop things on,
    else ''. Under something counts as the floor (slippers under the bed). A basin
    is judged by the spot's own name: the drawers of a sink cabinet are not wet."""
    import re
    w = _spot_words(place)
    own = " " + re.split(r"\b(?:by|near|next to|beside|under|across from)\b", place.name.lower())[0] + " "
    storage = any(_has(w, x) for x in STORAGE)
    if _has(w, "floor") or rel == "under":
        return "floor"
    if any(_has(w, x) for x in PASSING):
        return "passing"
    if place.kind != SURFACE and any(_has(own, x) for x in WET) and not _has(own, "cabinet"):
        return "wet"
    if any(_has(own, x) for x in HOT) and not storage:
        return "hot"
    if any(_has(w, x) for x in SEATS) and not any(_has(w, x) for x in STORAGE):
        return "seat"
    return ""


def _clothing(type_: str) -> bool:
    t = type_.lower()
    return washable(t) or is_sleepwear(t) or any(
        _has(f" {t} ", w) for w in ("blazer", "jacket", "coat", "robe", "bathrobe", "scarf", "vest",
                                    "suit", "dress"))


# bags and baskets things are dropped into on their way somewhere (a dirty sock's
# place is not the laundry basket); a wallet kept in a backpack is a home
PASSING_CARRIERS = ("laundry", "hamper", "trash", "rubbish", "garbage", "bin", "grocery",
                    "shopping", "delicates")


def _may_live_on(type_: str, size: str, place, rel: str = "") -> bool:
    t, kind, w = f" {type_.lower()} ", _drop_kind(place, rel), _spot_words(place)
    if kind == "passing":
        return False
    if kind and _clothing(t.strip()):
        return False                       # clothes are not kept on floors, beds or seats
    if kind == "floor" and (_has(w, "shower") or _has(w, "bath")):
        return any(_has(t, x) for x in SINK_DWELLERS)
    if kind == "floor":
        return size == "large" or any(_has(t, x) for x in FLOOR_DWELLERS)
    if kind == "wet":
        return any(_has(t, x) for x in SINK_DWELLERS)
    if kind == "hot":
        return any(_has(t, x) for x in ("kettle", "pan", "saucepan", "pot", "skillet"))
    return kind == "" or any(_has(t, x) for x in BED_DWELLERS)


def homes(objects: dict, layout: Layout) -> dict:
    """Where each thing is kept: {"place": p} or {"carrier": c} (a pen kept in its
    pencil case), or None when its starting spot says nothing about that (dropped
    on a floor, worn in bed). Clothes with no home of their own are kept where most
    of the same person's clothes are kept."""
    out = {}
    for oid, o in objects.items():
        st = o.get("start") or {}
        if st.get("at") == "place" and st.get("place") in layout.places:
            pl = layout.places[st["place"]]
            ok = _may_live_on(o.get("type", ""), o.get("size", ""), pl, st.get("rel") or "")
            out[oid] = {"place": st["place"]} if ok else None
        elif st.get("at") == "inside" and st.get("carrier") in objects:
            ctype = objects[st["carrier"]].get("type", "").lower()
            out[oid] = None if any(_has(f" {ctype} ", w) for w in PASSING_CARRIERS) else {"carrier": st["carrier"]}
        else:
            out[oid] = None
    # a plate on the dining table or a mug on a nightstand is in use, not kept there:
    # when most things of its type are kept shut away (cupboard, drawer), so is it
    shut = collections.defaultdict(collections.Counter)
    total = collections.Counter(o.get("type", "") for o in objects.values())
    for oid, o in objects.items():
        h = out[oid]
        if h and "place" in h and layout.places[h["place"]].kind == CLOSED:
            shut[o.get("type", "")][h["place"]] += 1
    for oid, o in objects.items():
        t, h = o.get("type", ""), out[oid]
        if shut[t] and sum(shut[t].values()) * 2 > total[t] and not _clothing(t) \
                and (h is None or ("place" in h and layout.places[h["place"]].kind == SURFACE)):
            out[oid] = {"place": shut[t].most_common(1)[0][0], "inferred": True}
    for oid, o in objects.items():
        t = o.get("type", "")
        if out[oid] is None and o.get("owner") and _clothing(t):
            kept = collections.Counter(
                out[x]["place"] for x, p in objects.items()
                if x != oid and p.get("owner") == o["owner"] and out.get(x) and "place" in out[x]
                and not out[x].get("inferred") and _clothing(p.get("type", "")))
            shut_away = collections.Counter({k: v for k, v in kept.items()
                                             if layout.places[k].kind == CLOSED})
            kept = shut_away or kept          # a drawer or wardrobe before an open shelf
            if kept:
                out[oid] = {"place": kept.most_common(1)[0][0], "inferred": True}
    return out


@dataclass
class Resident:
    rid: str
    at: Optional[str]                          # place id, or None while out of the house
    hands: list = field(default_factory=list)
    pocket: list = field(default_factory=list)
    worn: list = field(default_factory=list)
    back_at: int = -1                          # minute of return while out
    belief: dict = field(default_factory=dict)    # object -> {"pos", "day", "minute"}
    touched: dict = field(default_factory=dict)   # object -> (day, minute)
    noticed: dict = field(default_factory=dict)   # object -> (day, minute) seen somewhere new


class World:
    def __init__(self, layout: Layout, objects: dict, resident_ids: list[str],
                 start_place: dict, names: Optional[dict] = None) -> None:
        """objects: id -> {type, attributes..., owner, pocketable, carrier, start}.
        names: resident id -> first name, for labels like "(Daniel's)"."""
        self.layout, self.objects = layout, objects
        self.names = names or {r: r.title() for r in resident_ids}
        self.where = {oid: dict(o["start"]) for oid, o in objects.items()}
        self.people = {r: Resident(r, start_place[r]) for r in resident_ids}
        for oid, pos in self.where.items():           # what they wear in bed at the start
            if pos["at"] == "worn" and pos["person"] in self.people:
                self.people[pos["person"]].worn.append(oid)
        for person in self.people.values():
            person.belief = {oid: {"pos": dict(o["start"]), "day": -1, "minute": 0}
                             for oid, o in objects.items()}
        self.home = homes(objects, layout)     # where each thing is kept (None: nowhere known)
        self.day, self.log = 0, []
        self.dirty: set = set()               # clothes worn and not yet washed
        self.worn_today: set = set()

    # ---------------------------------------------------------------- facts
    def carrier_kind(self, oid: str) -> str:
        return self.objects[oid].get("carrier", "none")

    def contents(self, carrier: str) -> list[str]:
        return [o for o, w in self.where.items()
                if w["at"] == "inside" and w["carrier"] == carrier]

    def base(self, oid: str) -> dict:
        """The position of the object, or of the outermost carrier it is inside."""
        pos = self.where[oid]
        while pos["at"] == "inside":
            pos = self.where[pos["carrier"]]
        return pos

    def place_of(self, oid: str) -> Optional[str]:
        b = self.base(oid)
        return b["place"] if b["at"] == "place" else None

    def holder_of(self, oid: str) -> Optional[str]:
        b = self.base(oid)
        return b["person"] if b["at"] in ("hand", "pocket", "worn") else None

    def hidden(self, oid: str) -> bool:
        """Hidden from someone standing in the room (not at the place itself)."""
        pos = self.where[oid]
        if pos["at"] == "inside":
            if self.carrier_kind(pos["carrier"]) in SHUT:
                return True
            return self.hidden(pos["carrier"])
        if pos["at"] != "place":
            return False
        place = self.layout.places[pos["place"]]
        if pos["rel"] in HIDING_RELATIONS:
            return True
        if pos["rel"] == "inside" and not pos.get("ref") and place.kind == CLOSED:
            return True
        return bool(pos.get("ref")) and pos["ref"] in self.where and self.hidden(pos["ref"])

    def room_of_person(self, rid: str) -> Optional[str]:
        at = self.people[rid].at
        return self.layout.room_of(at) if at else None

    def others_in_room(self, rid: str) -> list[Resident]:
        room = self.room_of_person(rid)
        return [p for p in self.people.values()
                if p.rid != rid and p.at and room and self.layout.room_of(p.at) == room]

    def default_rel(self, place: str) -> str:
        return "on_top" if self.layout.places[place].kind == SURFACE else "inside"

    def things_at(self, place: str) -> list[str]:
        return [o for o, w in self.where.items() if w["at"] == "place" and w["place"] == place]

    def _clothes_clash(self, person, oid: str) -> list:
        """What must come off before oid goes on: sleepwear and day clothes are not
        worn together, nor two pairs of trousers."""
        new = self.objects[oid]["type"]
        out = []
        for w in person.worn:
            old = self.objects[w]["type"]
            if (is_sleepwear(new) and is_daywear(old)) or (is_daywear(new) and is_sleepwear(old)) \
                    or (is_bottoms(new) and is_bottoms(old)):
                out.append(w)
        return out

    def describe(self, pos: dict, rid: Optional[str] = None, depth: int = 0) -> str:
        """A position in words. Inside a carrier, also where the carrier is: as the
        resident remembers it (with rid), or as it is (without)."""
        if pos["at"] == "inside":
            c = pos["carrier"]
            if depth >= 4:
                return f"inside {c}"
            if rid is None:
                where = self.where.get(c)
            else:
                b = self.people[rid].belief.get(c)
                where = b["pos"] if b else None
            if not where:
                return f"inside {c}"
            return f"inside {c}, " + self.describe(where, rid, depth + 1)
        if pos["at"] == "place":
            rel = pos["rel"].replace("_", " ")
            if pos.get("ref"):
                return f"{rel} {pos['ref']} at {pos['place']}"
            return f"{rel} {pos['place']}"
        if pos["at"] == "unknown":
            return f"not at {pos['not_at']} when you looked; you do not know where"
        if pos["at"] == "worn":
            return "worn by you" if pos["person"] == rid else f"worn by {pos['person']}"
        who = "your" if pos["person"] == rid else f"{pos['person']}'s"
        return f"in {who} {pos['at']}"

    # ------------------------------------------------------------- seeing
    def can_see(self, rid: str, oid: str) -> bool:
        person = self.people[rid]
        room = self.room_of_person(rid)
        if room is None:
            return False
        pos = self.where[oid]
        if pos["at"] == "inside" and self.holder_of(pos["carrier"]) == rid:
            return True
        holder = self.holder_of(oid)
        if holder is not None:
            if holder == rid:
                return True
            other = self.people[holder]
            in_hand = (self.where[oid]["at"] in ("hand", "worn") or
                       (pos["at"] == "inside" and self.where[pos["carrier"]]["at"] in ("hand", "worn")
                        and self.carrier_kind(pos["carrier"]) == "open"))
            return in_hand and other.at is not None and self.layout.room_of(other.at) == room
        place = self.place_of(oid)
        if place is None or self.layout.room_of(place) != room:
            return False
        if not self.hidden(oid):
            return True
        # at the place itself: open the drawer, look under the bed,
        # but not inside a closed bag
        closed_bag = pos["at"] == "inside" and self.carrier_kind(pos["carrier"]) in SHUT
        return place == person.at and not closed_bag

    def _see(self, rid: str, minute: int) -> None:
        person = self.people[rid]
        if person.at is None:
            return
        for oid in self.objects:
            if self.can_see(rid, oid):
                self._remember(person, oid, minute)

    def _remember(self, person: Resident, oid: str, minute: int) -> None:
        pos = dict(self.where[oid])
        if pos["at"] == "place" and pos.get("ref") and not self.can_see(person.rid, pos["ref"]):
            pos["ref"] = None                       # they see the thing, not what it leans on
            pos["rel"] = self.default_rel(pos["place"])
        old = person.belief.get(oid)
        if old is None or old["pos"] != pos:
            person.noticed[oid] = (self.day, minute)
        person.belief[oid] = {"pos": pos, "day": self.day, "minute": minute}

    def _touch(self, person: Resident, oid: str, minute: int) -> None:
        person.touched[oid] = (self.day, minute)
        self._remember(person, oid, minute)
        for inner in self.contents(oid):
            self._remember(person, inner, minute)

    # --------------------------------------------------------- views for prompts
    def owner_tag(self, oid: str, rid: str) -> str:
        owner = self.objects[oid].get("owner")
        if not owner:
            return ""
        return " (yours)" if owner == rid else f" ({self.names.get(owner, owner)}'s)"

    def away_from_home(self, oid: str) -> Optional[str]:
        """Where oid is usually kept, in words, when it is somewhere else now; else None."""
        h = getattr(self, "home", {}).get(oid)
        if not h:
            return None
        if "carrier" in h:
            pos = self.where[oid]
            return None if pos["at"] == "inside" and pos["carrier"] == h["carrier"] else f"inside {h['carrier']}"
        if self.place_of(oid) == h["place"]:
            return None
        return ("in " if self.layout.places[h["place"]].kind != SURFACE else "on ") + h["place"]

    KEPT_MAX = 8        # "usually kept" notes per view: a reminder, not a to-do list

    def lying_about(self, oid: str) -> bool:
        """Held, or lying on a spot people drop things on (floor, seat, bed, basin,
        stovetop) away from where it is kept. Things that moved to another shelf or
        table may have found a new place, and are left alone."""
        worn_today = oid in self.worn_today and washable(self.objects[oid]["type"])
        if oid in self.dirty or worn_today or not self.away_from_home(oid):
            return False                   # worn today: dirty tonight, not back in the drawer
        pos = self.where[oid]
        if pos["at"] == "hand":
            return True
        place = self.place_of(oid)
        return pos["at"] == "place" and place is not None and \
            _drop_kind(self.layout.places[place], pos.get("rel") or "") != ""

    def kept_notes(self, rid: str) -> set:
        """Which things get a "usually kept" note in this resident's view now: what
        they hold first, then what lies about in the room, at most KEPT_MAX."""
        person = self.people[rid]
        room = self.room_of_person(rid)
        held = [o for o in person.hands if self.lying_about(o)]
        here = [o for p in (self.layout.places_in(room) if room else [])
                for o in self.things_at(p) if self.can_see(rid, o) and self.lying_about(o)]
        return set((held + here)[:self.KEPT_MAX])

    def _label(self, oid: str, rid: str, kept=False) -> str:
        pos, out = self.where[oid], oid + self.owner_tag(oid, rid)
        home = self.away_from_home(oid) if kept and (kept is True or oid in kept) else None
        if home:
            out += f" (usually kept {home})"
        if oid in self.dirty:
            out += " (worn, needs washing)"
        ref = pos.get("ref") if pos["at"] == "place" and pos.get("ref") and self.can_see(rid, pos["ref"]) else None
        if pos["at"] == "place" and (ref or pos["rel"] in ("under", "next_to")):
            out += f" ({pos['rel'].replace('_', ' ')} {ref if ref else 'it'})"
        if self.contents(oid):
            inside = [i for i in self.contents(oid) if self.can_see(rid, i)]
            if inside:
                out += f" [holding: {', '.join(self.tag(i, rid) for i in inside)}]"
        return out

    def room_view(self, rid: str, kept: bool = False) -> str:
        """What the resident sees around them: only places with something visible.
        With kept, things lying away from where they are usually kept say where that
        is (what anyone living there knows; shown during tidying and before bed)."""
        room = self.room_of_person(rid)
        if room is None:
            return "You are out of the house."
        person = self.people[rid]
        here = self.layout.places[person.at]
        kept = self.kept_notes(rid) if kept else set()
        lines = [f"You are in the {room}, at {person.at} ({here.name})."]
        for place in self.layout.places_in(room):
            seen = [o for o in self.things_at(place) if self.can_see(rid, o)]
            if seen:
                full = " (full)" if self._full(place, None, "on_top", None) else ""
                lines.append(f"  {place}{full}: " + ", ".join(self._label(o, rid, kept) for o in seen))
        if len(lines) == 1:
            lines.append("  Nothing is lying out in this room.")
        for other in self.others_in_room(rid):
            held = [self._label(o, rid) for o in other.hands]
            lines.append(f"  {other.rid} is here, at {other.at}, holding "
                         f"{', '.join(held) or 'nothing'}.")
        return "\n".join(lines)

    def memory_items(self, rid: str, needed_types: set, days_back: int = 2) -> list[str]:
        """Objects worth listing from memory right now: touched or noticed in a new
        spot in the last `days_back` days, owned by the resident, or of a type the
        current activity needs. Skips what they hold and what they see now."""
        person = self.people[rid]
        recent = lambda d: d is not None and d[0] >= self.day - days_back
        # a kind the activity needs: their own and shared ones; someone else's only
        # when they have none of that kind themselves
        usable = {o["type"] for o in self.objects.values() if o.get("owner") in (None, rid)}
        keep = []
        for oid, o in self.objects.items():
            if self.holder_of(oid) == rid or self.can_see(rid, oid):
                continue
            needed = o["type"] in needed_types and (o.get("owner") in (None, rid) or o["type"] not in usable)
            if (recent(person.touched.get(oid)) or recent(person.noticed.get(oid))
                    or o.get("owner") == rid or needed):
                keep.append(oid)
        return keep

    def memory_view(self, rid: str, needed_types: set, days_back: int = 2) -> str:
        person = self.people[rid]
        by_type: dict[str, list[str]] = {}
        for oid in self.memory_items(rid, needed_types, days_back):
            b = person.belief[oid]
            when = "where it was at the start" if b["day"] < 0 else f"day {b['day']} {clock(b['minute'])}"
            by_type.setdefault(self.objects[oid]["type"], []).append(
                f"{oid}{self.owner_tag(oid, rid)}{' (needs washing)' if oid in self.dirty else ''} "
                f"{self.describe(b['pos'], rid)} (last seen {when})")
        if not by_type:
            return "  (nothing you need to keep in mind)"
        return "\n".join(f"  {t}: " + "; ".join(items) for t, items in sorted(by_type.items()))

    def pocket_items(self, rid: str) -> list[str]:
        person = self.people[rid]
        out = list(person.pocket)
        for w in person.worn:
            if self.carrier_kind(w) == "pockets":
                out += self.contents(w)
        return out

    def holding_view(self, rid: str, kept: bool = False) -> tuple[str, str, str]:
        person = self.people[rid]
        kept = self.kept_notes(rid) if kept and person.at else set()
        hands = [self._label(o, rid, kept) for o in person.hands]
        worn = [self._label(o, rid) for o in person.worn]
        return (", ".join(hands) or "nothing",
                ", ".join(self.tag(o, rid) for o in self.pocket_items(rid)) or "nothing",
                ", ".join(worn) or "nothing you need to keep track of")

    # -------------------------------------------------------------- acting
    def _reach(self, rid: str, oid: str, minute: int, named: Optional[str] = None) -> tuple[bool, str, list]:
        """Can the resident get their hands on oid from where they stand? Walking
        to another place in the same room is allowed and returned as a step."""
        person = self.people[rid]
        pos = self.where[oid]
        room = self.room_of_person(rid)
        holder = self.holder_of(oid)
        if pos["at"] in ("hand", "pocket", "worn") and pos["person"] == rid:
            return True, "", []
        if holder == rid:                               # inside a carrier they hold
            return True, "", []
        if holder is not None:
            if self.can_see(rid, oid):
                return False, f"{self.tag(oid, rid)} is with {self.names.get(holder, holder)}.", []
            return False, self._not_found(person, oid, minute), []
        place = self.place_of(oid)
        if place is not None and named == place and self.layout.room_of(place) != room:
            return True, "", [place]            # they said where it is: walk there
        if place is None or self.layout.room_of(place) != room:
            return False, self._not_found(person, oid, minute), []
        if pos["at"] == "inside" and self.carrier_kind(pos["carrier"]) in SHUT \
                and place != person.at:
            pass                                        # they walk over and open the bag
        steps = [] if place == person.at else [place]
        return True, "", steps

    def tag(self, oid: str, rid: str) -> str:
        """An id as a resident would think of it: with its owner when it has one."""
        return oid + self.owner_tag(oid, rid)

    def _not_found(self, person: Resident, oid: str, minute: int) -> str:
        """The resident looked for oid where they believed it to be, in this room, and
        it was not there. They walk over and look (a closed drawer is opened), learn
        what is there, and that oid is not; never where it is."""
        room = self.room_of_person(person.rid)
        believed = person.belief[oid]["pos"]
        if believed["at"] == "inside":
            bag = believed["carrier"]
            bag_place = self.place_of(bag)
            if self.holder_of(bag) == person.rid or self.can_see(person.rid, bag) or \
                    (bag_place and self.layout.room_of(bag_place) == room
                     and person.belief[bag]["pos"].get("place") == bag_place):
                if bag_place and bag_place != person.at and self.holder_of(bag) != person.rid:
                    self._step(person.rid, bag_place, minute)
                person.belief[oid] = {"pos": {"at": "unknown", "not_at": f"inside {bag}"},
                                      "day": self.day, "minute": minute}
                self._remember(person, bag, minute)
                for o in self.contents(bag):
                    self._remember(person, o, minute)
                inside = [self.tag(o, person.rid) for o in self.contents(bag)]
                return (f"{self.tag(oid, person.rid)} is not inside {self.tag(bag, person.rid)}. "
                        f"In it you see: {', '.join(inside) or 'nothing'}.")
        believed_place = believed.get("place") if believed["at"] == "place" else None
        if believed_place and self.layout.room_of(believed_place) == room:
            if believed_place != person.at:
                self._step(person.rid, believed_place, minute)   # walk over, open it, look
            person.belief[oid] = {"pos": {"at": "unknown", "not_at": believed_place},
                                  "day": self.day, "minute": minute}
            seen = [o for o in self.things_at(believed_place) if self.can_see(person.rid, o)]
            return (f"{self.tag(oid, person.rid)} is not at {believed_place}. There you see: "
                    f"{', '.join(self.tag(o, person.rid) for o in seen) or 'nothing'}.")
        b = person.belief[oid]
        if b["pos"]["at"] == "unknown":
            last = "and you do not know where it is"
        else:
            when = "at the start" if b["day"] < 0 else f"day {b['day']} {clock(b['minute'])}"
            last = f"you last saw it {self.describe(b['pos'], person.rid)} ({when})"
        return f"You do not see {self.tag(oid, person.rid)} anywhere you can reach in the {room}; {last}."

    def _step(self, rid: str, place: str, minute: int) -> int:
        """A walk the resident's action implies. Returns minutes (1 across rooms)."""
        person = self.people[rid]
        cross = self.layout.room_of(place) != self.room_of_person(rid)
        source, person.at = person.at, place
        self._see(rid, minute)
        why = "(walked to the spot named)" if cross else "(walked over within the room)"
        self.log.append(self._event(rid, {"verb": "go", "place": place, "why": why},
                                    minute, source, place, int(cross), implied=True))
        return int(cross)

    def _settle(self, oid: str) -> list[str]:
        """oid was taken away: things recorded relative to it (on top of it,
        next to it) now just sit at the place."""
        moved = []
        for other, w in self.where.items():
            if w["at"] == "place" and w.get("ref") == oid:
                w["ref"] = None
                w["rel"] = self.default_rel(w["place"])
                moved.append(other)
        return moved

    def _take(self, rid: str, oid: str, minute: int, named: Optional[str] = None) -> tuple[bool, str, int]:
        """Take oid out of wherever it is into the resident's control (not yet
        placed into a hand, pocket or onto them). Returns minutes walked."""
        ok, message, steps = self._reach(rid, oid, minute, named)
        if not ok:
            return False, message, 0
        walked = sum(self._step(rid, place, minute) for place in steps)
        self._release(self.people[rid], oid)
        return True, "", walked

    @staticmethod
    def _release(person: Resident, oid: str) -> None:
        for slot in (person.hands, person.pocket, person.worn):
            if oid in slot:
                slot.remove(oid)

    def apply(self, rid: str, act: dict, minute: int) -> tuple[bool, str, int]:
        """Carry out one action. Returns (done, message, minutes taken)."""
        person, verb = self.people[rid], act.get("verb")
        oid = act.get("object") or None
        if person.at is None:
            return False, "You are out of the house.", 0
        if oid is not None and oid not in self.objects:
            return False, f"There is no object called {oid}.", 0

        if verb == "go":
            place = act.get("place") or ""
            if place not in self.layout.places:
                return False, f"There is no place called {place}.", 0
            steps = 0 if self.layout.room_of(place) == self.room_of_person(rid) else 1
            source, person.at = person.at, place
            self._see(rid, minute + steps)
            return self._done(rid, act, minute, source, place, steps)

        if verb == "pick_up":
            if oid is None:
                return False, "Pick up what?", 0
            if oid in person.hands:
                return False, f"You are already holding {oid}.", 0
            if len(person.hands) >= HANDS:
                return False, f"Your hands are full ({', '.join(person.hands)}).", 0
            source = dict(self.where[oid])
            ok, message, walked = self._take(rid, oid, minute, act.get("place") or None)
            if not ok:
                return False, message, 0
            settled = self._settle(oid)
            self.where[oid] = {"at": "hand", "person": rid}
            person.hands.append(oid)
            self._touch(person, oid, minute)
            return self._done(rid, act, minute, source, self.where[oid], walked, settled=settled)

        if verb == "put_down":
            return self._put_down(rid, act, minute)

        if verb == "pocket":
            if oid is None:
                return False, "Pocket what?", 0
            if not self.objects[oid].get("pocketable"):
                return False, f"{oid} does not fit in a pocket.", 0
            in_pockets = self.pocket_items(rid)
            if oid in in_pockets:
                return False, f"{oid} is already in your pocket.", 0
            if len(in_pockets) >= POCKET_SLOTS:
                return False, f"Your pockets are full ({', '.join(in_pockets)}).", 0
            source = dict(self.where[oid])
            ok, message, walked = self._take(rid, oid, minute, act.get("place") or None)
            if not ok:
                return False, message, 0
            settled = self._settle(oid)
            pocketed = [w for w in person.worn if self.carrier_kind(w) == "pockets"]
            if pocketed:                         # into the pockets of what they wear
                self.where[oid] = {"at": "inside", "carrier": pocketed[-1]}
            else:
                self.where[oid] = {"at": "pocket", "person": rid}
                person.pocket.append(oid)
            self._touch(person, oid, minute)
            return self._done(rid, act, minute, source, self.where[oid], walked, settled=settled)

        if verb == "wear":
            if oid is None:
                return False, "Wear what?", 0
            if oid in person.worn:
                return False, f"You are already wearing {oid}.", 0
            clash = self._clothes_clash(person, oid)
            if clash:
                return False, (f"You are still wearing {', '.join(clash)}; take "
                               f"{'it' if len(clash) == 1 else 'them'} off first (put "
                               f"{'it' if len(clash) == 1 else 'them'} down somewhere)."), 0
            source = dict(self.where[oid])
            ok, message, walked = self._take(rid, oid, minute, act.get("place") or None)
            if not ok:
                return False, message, 0
            settled = self._settle(oid)
            self.where[oid] = {"at": "worn", "person": rid}
            person.worn.append(oid)
            self.worn_today.add(oid)
            self._touch(person, oid, minute)
            return self._done(rid, act, minute, source, self.where[oid], walked, settled=settled)

        if verb == "give":
            if oid is None:
                return False, "Give what?", 0
            other = self.people.get(act.get("person") or "")
            if other is None or other.rid == rid:
                return False, "Give it to whom?", 0
            if self.holder_of(oid) != rid:          # hands, pockets, worn, or in a bag they carry
                return False, self._not_holding(rid, oid), 0
            if other.at is None or self.layout.room_of(other.at) != self.room_of_person(rid):
                return False, f"{other.rid} is not in this room.", 0
            if len(other.hands) >= HANDS:
                return False, f"{other.rid}'s hands are full.", 0
            source = dict(self.where[oid])
            self._release(person, oid)
            self.where[oid] = {"at": "hand", "person": other.rid}
            other.hands.append(oid)
            self._touch(person, oid, minute)
            self._touch(other, oid, minute)
            return self._done(rid, act, minute, source, self.where[oid], 1)

        if verb == "do":
            walked = 0
            named = act.get("place") or ""
            if named in self.layout.places and named != person.at:
                walked = self._step(rid, named, minute)
            washed = self._wash_at(person.at)
            return self._done(rid, act, minute, person.at, person.at,
                              walked + max(1, act.get("minutes") or 1),
                              **({"washed": washed} if washed else {}))
        if verb == "say":
            to = act.get("person") or ""
            if to and (to == rid or to not in self.people):
                return False, f"Say it to whom? {to} is not someone else in the household.", 0
            if not (act.get("text") or "").strip():
                return False, "Say what? The text is empty.", 0
            return self._done(rid, act, minute, person.at, person.at, 1)
        if verb == "leave_home":
            minutes = max(5, act.get("minutes") or 30)
            carried = self._carried(person)
            source, person.at, person.back_at = person.at, None, minute + minutes
            return self._done(rid, act, minute, source, "out of the house", minutes,
                              carried=carried)
        return False, f"Unknown action {verb}.", 0

    def _put_down(self, rid: str, act: dict, minute: int) -> tuple[bool, str, int]:
        person = self.people[rid]
        oid = act.get("object") or None
        if oid is None:
            return False, "Put down what?", 0
        if self.holder_of(oid) != rid:          # hands, pockets, worn, or in a bag they carry
            return False, self._not_holding(rid, oid), 0
        place = act.get("place") or person.at
        if place not in self.layout.places:
            return False, f"There is no place called {place}.", 0
        rel = act.get("relation") or ""
        if rel not in RELATIONS:
            rel = ""
        ref = act.get("ref") or None
        if ref is not None and ref not in self.objects:
            return False, f"There is no object called {ref}.", 0
        if ref == oid:
            return False, f"You cannot put {oid} relative to itself.", 0
        kind = self.layout.places[place].kind
        source = dict(self.where[oid])

        if ref is not None and rel == "inside" and self.carrier_kind(ref) == "none":
            # "inside" a fork or a tomato: what was meant is kept together with it -
            # next to it, or in the bag it is in
            if self.where[ref]["at"] == "inside":
                act = dict(act, ref=self.where[ref]["carrier"], ref_as_said=ref)
                ref = act["ref"]
                if ref == oid:
                    return False, f"{act['ref_as_said']} is inside {oid}; {oid} cannot go inside it.", 0
            else:
                act = dict(act, relation="next_to", relation_as_said="inside")
                rel = "next_to"
        if ref is not None and rel == "inside":
            # inside another thing: a bag, a basket, a mug
            steps = []
            if self.holder_of(ref) != rid:
                ok, message, steps = self._reach(rid, ref, minute, place if act.get("place") else None)
                if not ok:
                    return False, message, 0
                if self.holder_of(ref) is not None:
                    return False, f"{self.tag(ref, rid)} is with {self.names.get(self.holder_of(ref))}.", 0
            outer = ref
            while self.where[outer]["at"] == "inside":
                if self.where[outer]["carrier"] == oid:
                    return False, f"{ref} is inside {oid}; {oid} cannot go inside it.", 0
                outer = self.where[outer]["carrier"]
            walked = sum(self._step(rid, p, minute) for p in steps)
            self._release(person, oid)
            self.where[oid] = {"at": "inside", "carrier": ref}
            self._touch(person, oid, minute)
            return self._done(rid, act, minute, source, self.where[oid], walked)

        walked = 0
        if ref is not None and self.where[ref] == {"at": "hand", "person": rid}:
            # bread on top of the plate still in their other hand: the plate goes down first
            if place != person.at:
                walked = self._step(rid, place, minute)
            self.where[ref] = at_place(place, self.default_rel(place), None)
            person.hands.remove(ref)
            self._touch(person, ref, minute)
            self.log.append(self._event(rid, {"verb": "put_down", "object": ref,
                                              "why": "(set down first, to put something on it)"},
                                        minute, {"at": "hand", "person": rid}, self.where[ref], 0,
                                        implied=True))
        if ref is not None:
            if self.where[ref]["at"] != "place" or self.where[ref]["place"] != place:
                return False, (f"{ref} is not at {place}; you can only put {oid} "
                               f"{(rel or 'next_to').replace('_', ' ')} something that is there."), 0
            if rel == "":
                rel = "next_to"
        else:
            if rel == "" or (rel == "inside" and kind == SURFACE) or (rel == "on_top" and kind != SURFACE):
                rel = self.default_rel(place)
            height = (self.layout.places[place].geometry or {}).get("height")
            if rel == "under" and height is not None and height < 0.15:
                rel = self.default_rel(place)      # nothing goes under a floor
        full = self._full(place, oid, rel, ref)
        if full:
            return False, full, 0
        if place != person.at:
            walked += self._step(rid, place, minute)
        self._release(person, oid)
        self.where[oid] = at_place(place, rel, ref)
        self._touch(person, oid, minute)
        return self._done(rid, act, minute, source, self.where[oid], walked)

    def resting_on(self, place: str) -> list:
        """Things that take room on a spot: directly on it or in it, not stacked on
        another thing and not under it."""
        return [o for o, w in self.where.items()
                if w["at"] == "place" and w["place"] == place and w["rel"] != "under"
                and (w.get("ref") is None or w["rel"] == "next_to")]

    def footprint(self, oid: str) -> float:
        return FOOTPRINT.get(self.objects[oid].get("size"), FOOTPRINT["medium"])

    def _full(self, place: str, oid: str, rel: str, ref) -> str:
        """Why oid does not fit on the spot, or "" if it does. Only spots with a
        measured area (from a 3D home) have a limit."""
        if ref is not None and rel == "on_top" and oid is not None:
            # a stack: room on top of the thing below, not on the spot
            if self.footprint(ref) < self.footprint(oid):
                return f"{oid} is too big to go on top of {ref}. Put it somewhere else."
            return ""
        area = (self.layout.places[place].geometry or {}).get("area")
        if not area or rel == "under" or (ref is not None and rel == "on_top"):
            return ""
        room = area * (DEPTH if self.layout.places[place].kind != SURFACE else 1.0)
        there = self.resting_on(place)
        size = self.footprint(oid) if oid is not None else FOOTPRINT["small"]   # None: room for a small thing?
        if sum(map(self.footprint, there)) + size <= room:
            return ""
        return (f"There is no room for {oid} at {place}: it already holds "
                f"{', '.join(there)}. Put it somewhere else, or on top of something there.")

    def _not_holding(self, rid: str, oid: str) -> str:
        """Not holding it; if they can see it, say where (what they would see)."""
        if self.can_see(rid, oid):
            return f"You are not holding {self.tag(oid, rid)}; it is {self.describe(self.where[oid], rid)}."
        return f"You are not holding {self.tag(oid, rid)}."

    def _wash_at(self, place: Optional[str]) -> list:
        """Time spent at a washing machine washes what is inside it."""
        if not place:
            return []
        p = self.layout.places[place]
        g = p.geometry or {}
        scene_says = "wash" in str(g.get("category") or "").lower() or "drum" in str(g.get("hssd_spot") or "")
        named = "wash" in (place + " " + p.name + " " + p.furniture).lower() and "dish" not in place
        if not (scene_says or named):
            return []
        inside = [o for o in self.objects if self.place_of(o) == place and o in self.dirty]
        self.dirty -= set(inside)
        return inside

    def end_of_day(self) -> None:
        """Clothes worn today are dirty tonight (sleepwear excepted)."""
        self.dirty |= {o for o in self.worn_today if washable(self.objects[o]["type"])}
        self.worn_today = {o for p in self.people.values() for o in p.worn}

    def _carried(self, person: Resident) -> list:
        carried = person.hands + person.pocket + person.worn
        frontier = list(carried)
        while frontier:
            inner = [i for c in frontier for i in self.contents(c)]
            carried += inner
            frontier = inner
        return carried

    def come_home_if_due(self, rid: str, minute: int) -> bool:
        person = self.people[rid]
        if person.at is None and minute >= person.back_at:
            person.at = self.layout.entry
            self._see(rid, minute)
            self.log.append(self._event(rid, {"verb": "come_home"}, minute,
                                        "out of the house", self.layout.entry, 0,
                                        carried=self._carried(person)))
            return True
        return False

    def _event(self, rid, act, minute, source, dest, minutes, **extra) -> dict:
        def show(x):
            return self.describe(x) if isinstance(x, dict) else x
        out = {"day": self.day, "minute": minute, "time": clock(minute), "resident": rid,
               "verb": act.get("verb"), "object": act.get("object") or None,
               "from": show(source), "to": show(dest),
               "to_pos": dest if isinstance(dest, dict) else None,
               "hidden_after": (self.hidden(act["object"]) if act.get("object") in self.objects
                                and act.get("verb") in ("put_down",) else None),
               "minutes": minutes, "text": act.get("text") or None,
               "person": act.get("person") or None, "why": act.get("why")}
        if act.get("verb") == "put_down":
            out["relation"], out["ref"] = act.get("relation") or None, act.get("ref") or None
        for k in ("minutes_filled", "minutes_as_written", "relation_as_said", "ref_as_said"):
            if k in act:
                out[k] = act[k]
        out.update(extra)
        return out

    def _done(self, rid, act, minute, source, dest, minutes, **extra) -> tuple[bool, str, int]:
        self.log.append(self._event(rid, act, minute, source, dest, minutes, **extra))
        oid = act.get("object")
        if oid in self.objects:
            self._witness(rid, [oid] + list(extra.get("settled") or []), minute)
        return True, "", minutes

    def _witness(self, rid: str, oids: list, minute: int) -> None:
        """Everyone in the room who can see the moved things notes where they are now;
        the actor also notes what shifted when they took something away."""
        actor = self.people[rid]
        for o in oids[1:]:
            if self.can_see(rid, o):
                self._remember(actor, o, minute)
        for other in self.others_in_room(rid):
            for o in oids:
                if self.can_see(other.rid, o):
                    self._remember(other, o, minute)

    def positions(self, scene: Optional[str] = None) -> dict:
        """Everything needed to place every object in a 3D scene: for each object its
        room, place, relation and reference (an object, a place or a person), and
        whether it is hidden; for each place its room, furniture and geometry."""
        objs = {}
        for oid, pos in self.where.items():
            o = self.objects[oid]
            rec = {"type": o["type"], "looks": o.get("looks"), "color": o.get("color"),
                   "material": o.get("material"), "size": o.get("size"),
                   "owner": o.get("owner"), "holds": self.carrier_kind(oid),
                   "hidden": self.hidden(oid),
                   "dirty": oid in self.dirty}
            if pos["at"] == "place":
                rec.update(room=self.layout.room_of(pos["place"]), place=pos["place"],
                           relation=pos["rel"],
                           reference=pos["ref"] or pos["place"],
                           reference_kind="object" if pos["ref"] else "place")
            elif pos["at"] == "inside":
                base = self.place_of(oid)
                holder = self.holder_of(oid)
                at = base or (self.people[holder].at if holder else None)
                rec.update(room=self.layout.room_of(at) if at else "out_of_house", place=base or at,
                           relation="inside", reference=pos["carrier"], reference_kind="object")
            else:                                  # on a person: hand, pocket or worn
                who = self.people[pos["person"]]
                rec.update(room=self.layout.room_of(who.at) if who.at else "out_of_house",
                           place=who.at, relation={"worn": "worn_by", "hand": "held_by",
                                                   "pocket": "in_pocket_of"}[pos["at"]],
                           reference=pos["person"], reference_kind="person")
            objs[oid] = rec
        places = {pid: {"room": p.room, "furniture": p.furniture, "name": p.name, "kind": p.kind,
                        **({"geometry": p.geometry} if p.geometry else {})}
                  for pid, p in self.layout.places.items()}
        people = {r: {"room": self.layout.room_of(p.at) if p.at else "out_of_house", "place": p.at}
                  for r, p in self.people.items()}
        at = getattr(self, "minute_now", None)
        return {"scene": scene, "day": self.day, "time": clock(at) if at is not None else "end of day",
                "relations": RELATIONS,
                "hidden_rule": "inside a closed container (place or object), or under something",
                "people": people, "places": places, "objects": objs}

    def snapshot(self) -> dict:
        """Where every object is right now, with the place it sits at (through
        any carrier) and whether it is hidden from someone in the room."""
        out = {}
        for oid, pos in self.where.items():
            out[oid] = {"pos": dict(pos), "text": self.describe(pos),
                        "place": self.place_of(oid), "holder": self.holder_of(oid),
                        "hidden": self.hidden(oid)}
        return out
