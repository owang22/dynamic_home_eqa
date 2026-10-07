"""The truth of the home: where every object is and what each resident holds.

Every object is in exactly one spot:
  {"at": "place",  "place": p, "rel": r, "ref": o or None}   on/in/under/... a place
  {"at": "hand",   "person": rid}                              in a hand (two each)
  {"at": "pocket", "person": rid}
  {"at": "worn",   "person": rid}                              clothes, shoes, a watch, a backpack on
  {"at": "inside", "carrier": o}                              in a bag, box or basket
Carriers hold one level: a carrier that is inside another carrier holds nothing,
and a carrier that holds something cannot go inside another, except clothes
with pockets (a pair of jeans with a wallet in it can go in the laundry basket).
pocket puts a thing into the pockets of what the resident wears; taking those
clothes off leaves it there. Moving a carrier
moves what is inside it. A resident who leaves the house takes what they hold,
their pockets, and what is inside the carriers they hold.

A position is hidden from someone standing in the room when it is in a closed
container place, on a hidden place (under the bed), under or behind something,
or inside a closed carrier. Residents see hidden positions only at the place
they stand at, and see inside a closed carrier only when they hold it.

Each resident keeps their own memory of where they last saw each object, which
is out of date when someone else moved it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from lived_home.layout import CONTAINER, Layout

HANDS = 2
POCKET_SLOTS = 5
RELATIONS = ["on", "in", "under", "behind", "next_to", "on_top_of"]
HIDING_RELATIONS = {"under", "behind"}
CARRIER_KINDS = ["none", "open", "closed", "pockets"]   # pockets: clothes with pockets
SHUT = ("closed", "pockets")                               # contents not seen from outside


def clock(minute: int) -> str:
    return f"{(minute // 60) % 24:02d}:{minute % 60:02d}"


def at_place(place: str, rel: str = "on", ref: Optional[str] = None) -> dict:
    return {"at": "place", "place": place, "rel": rel, "ref": ref}


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
        for person in self.people.values():
            person.belief = {oid: {"pos": dict(o["start"]), "day": -1, "minute": 0}
                             for oid, o in objects.items()}
        self.day, self.log = 0, []

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
        return (not place.seen_from_room) or pos["rel"] in HIDING_RELATIONS

    def room_of_person(self, rid: str) -> Optional[str]:
        at = self.people[rid].at
        return self.layout.room_of(at) if at else None

    def others_in_room(self, rid: str) -> list[Resident]:
        room = self.room_of_person(rid)
        return [p for p in self.people.values()
                if p.rid != rid and p.at and room and self.layout.room_of(p.at) == room]

    def things_at(self, place: str) -> list[str]:
        return [o for o, w in self.where.items() if w["at"] == "place" and w["place"] == place]

    def describe(self, pos: dict, rid: Optional[str] = None) -> str:
        if pos["at"] == "place":
            rel = pos["rel"].replace("_", " ")
            if pos.get("ref"):
                return f"{rel} {pos['ref']} at {pos['place']}"
            return f"{rel} {pos['place']}"
        if pos["at"] == "inside":
            return f"inside {pos['carrier']}"
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
        # at the place itself: open the drawer, look behind the toaster,
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

    def _label(self, oid: str, rid: str) -> str:
        pos, out = self.where[oid], oid + self.owner_tag(oid, rid)
        if pos["at"] == "place" and (pos["ref"] or pos["rel"] not in ("on", "in")):
            out += f" ({pos['rel'].replace('_', ' ')}{' ' + pos['ref'] if pos['ref'] else ''})"
        if self.carrier_kind(oid) != "none":
            inside = [i for i in self.contents(oid) if self.can_see(rid, i)]
            if inside:
                out += f" [holding: {', '.join(self.tag(i, rid) for i in inside)}]"
        return out

    def room_view(self, rid: str) -> str:
        """What the resident sees around them: only places with something visible."""
        room = self.room_of_person(rid)
        if room is None:
            return "You are out of the house."
        person = self.people[rid]
        here = self.layout.places[person.at]
        lines = [f"You are in the {room}, at {person.at} ({here.name})."]
        for place in self.layout.places_in(room):
            seen = [o for o in self.things_at(place) if self.can_see(rid, o)]
            if seen:
                lines.append(f"  {place}: " + ", ".join(self._label(o, rid) for o in seen))
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
        keep = []
        for oid, o in self.objects.items():
            if self.holder_of(oid) == rid or self.can_see(rid, oid):
                continue
            if (recent(person.touched.get(oid)) or recent(person.noticed.get(oid))
                    or o.get("owner") == rid or o["type"] in needed_types):
                keep.append(oid)
        return keep

    def memory_view(self, rid: str, needed_types: set, days_back: int = 2) -> str:
        person = self.people[rid]
        by_type: dict[str, list[str]] = {}
        for oid in self.memory_items(rid, needed_types, days_back):
            b = person.belief[oid]
            when = "where it was at the start" if b["day"] < 0 else f"day {b['day']} {clock(b['minute'])}"
            by_type.setdefault(self.objects[oid]["type"], []).append(
                f"{oid}{self.owner_tag(oid, rid)} {self.describe(b['pos'], rid)} (last seen {when})")
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

    def holding_view(self, rid: str) -> tuple[str, str, str]:
        person = self.people[rid]
        hands = [self._label(o, rid) for o in person.hands]
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
        """The resident looked for oid where they are and it was not there. They
        learn only that it is not here, never where it is."""
        room = self.room_of_person(person.rid)
        believed = person.belief[oid]["pos"]
        if believed["at"] == "inside":
            # remembered in a bag or basket: if that bag is here in the room, they look inside
            bag = believed["carrier"]
            if self.place_of(bag) and self.layout.room_of(self.place_of(bag)) == room \
                    or self.holder_of(bag) == person.rid:
                person.belief[oid] = {"pos": {"at": "unknown", "not_at": f"inside {bag}"},
                                      "day": self.day, "minute": minute}
                inside = [self.tag(o, person.rid) for o in self.contents(bag)]
                return (f"{self.tag(oid, person.rid)} is not inside {self.tag(bag, person.rid)}. "
                        f"In it you see: {', '.join(inside) or 'nothing'}.")
        believed_place = believed.get("place") if believed["at"] == "place" else None
        if believed_place and self.layout.room_of(believed_place) == room:
            person.belief[oid] = {"pos": {"at": "unknown", "not_at": believed_place},
                                  "day": self.day, "minute": minute}
            seen = [o for o in self.things_at(believed_place) if self.can_see(person.rid, o)
                    or believed_place == person.at]
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
        behind it) now just sit at the place."""
        moved = []
        for other, w in self.where.items():
            if w["at"] == "place" and w.get("ref") == oid:
                place = self.layout.places[w["place"]]
                w["ref"] = None
                w["rel"] = "in" if place.kind == CONTAINER else "on"
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
            source = dict(self.where[oid])
            ok, message, walked = self._take(rid, oid, minute, act.get("place") or None)
            if not ok:
                return False, message, 0
            settled = self._settle(oid)
            self.where[oid] = {"at": "worn", "person": rid}
            person.worn.append(oid)
            self._touch(person, oid, minute)
            return self._done(rid, act, minute, source, self.where[oid], walked, settled=settled)

        if verb == "give":
            if oid is None:
                return False, "Give what?", 0
            other = self.people.get(act.get("person") or "")
            if other is None or other.rid == rid:
                return False, "Give it to whom?", 0
            if self.holder_of(oid) != rid:          # hands, pockets, worn, or in a bag they carry
                return False, f"You are not holding {oid}.", 0
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
            return self._done(rid, act, minute, person.at, person.at,
                              walked + max(1, act.get("minutes") or 1))
        if verb == "say":
            to = act.get("person") or ""
            if to and (to == rid or to not in self.people):
                return False, f"Say it to whom? {to} is not someone else in the household.", 0
            return self._done(rid, act, minute, person.at, person.at, 1)
        if verb == "leave_home":
            minutes = max(5, act.get("minutes") or 30)
            carried = person.hands + person.pocket + person.worn
            frontier = list(carried)
            while frontier:
                inner = [i for c in frontier for i in self.contents(c)]
                carried += inner
                frontier = inner
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
            return False, f"You are not holding {oid}.", 0
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

        if ref is not None and rel == "in":
            # into a bag, box or basket
            if self.carrier_kind(ref) == "none":
                return False, f"{ref} cannot hold things.", 0
            if self.where[ref]["at"] == "inside":
                return False, f"{ref} is itself inside {self.where[ref]['carrier']}; take it out first.", 0
            if self.carrier_kind(oid) not in ("none", "pockets") and self.contents(oid):
                return False, f"{oid} has things in it; it cannot go inside {ref}.", 0
            walked = 0
            if self.holder_of(ref) != rid:
                ok, message, steps = self._reach(rid, ref, minute, place if act.get("place") else None)
                if not ok:
                    return False, message, 0
                if self.holder_of(ref) is not None:
                    return False, f"{ref} is with {self.holder_of(ref)}.", 0
                walked = sum(self._step(rid, p, minute) for p in steps)
            self._release(person, oid)
            self.where[oid] = {"at": "inside", "carrier": ref}
            self._touch(person, oid, minute)
            return self._done(rid, act, minute, source, self.where[oid], walked)

        if ref is not None and self.where[ref] == {"at": "hand", "person": rid} and rel != "in":
            # bread on top of the plate still in their other hand: the plate goes down first
            self.where[ref] = at_place(place, "in" if kind == CONTAINER else "on", None)
            person.hands.remove(ref)
            self._touch(person, ref, minute)
            self.log.append(self._event(rid, {"verb": "put_down", "object": ref,
                                              "why": "(set down first, to put something on it)"},
                                        minute, {"at": "hand", "person": rid}, self.where[ref], 0,
                                        implied=True))
        if ref is not None:
            if self.where[ref]["at"] != "place" or self.where[ref]["place"] != place:
                return False, (f"{ref} is not at {place}; you can only put {oid} "
                               f"{rel or 'next to'} something that is there."), 0
            if rel in ("", "on", "in"):
                rel = "on_top_of" if rel in ("", "on") else rel
        if rel == "":
            rel = "in" if kind == CONTAINER else "on"
        if ref is None and rel in ("in", "on", "on_top_of"):
            rel = "in" if kind == CONTAINER else "on"
        walked = self._step(rid, place, minute) if place != person.at else 0
        self._release(person, oid)
        self.where[oid] = at_place(place, rel, ref)
        self._touch(person, oid, minute)
        return self._done(rid, act, minute, source, self.where[oid], walked)

    def come_home_if_due(self, rid: str, minute: int) -> bool:
        person = self.people[rid]
        if person.at is None and minute >= person.back_at:
            person.at = self.layout.entry
            self._see(rid, minute)
            self.log.append(self._event(rid, {"verb": "come_home"}, minute,
                                        "out of the house", self.layout.entry, 0,
                                        carried=person.hands + person.pocket + person.worn))
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
        for k in ("minutes_filled", "minutes_as_written"):
            if k in act:
                out[k] = act[k]
        out.update(extra)
        return out

    def _done(self, rid, act, minute, source, dest, minutes, **extra) -> tuple[bool, str, int]:
        self.log.append(self._event(rid, act, minute, source, dest, minutes, **extra))
        return True, "", minutes

    def snapshot(self) -> dict:
        """Where every object is right now, with the place it sits at (through
        any carrier) and whether it is hidden from someone in the room."""
        out = {}
        for oid, pos in self.where.items():
            out[oid] = {"pos": dict(pos), "text": self.describe(pos),
                        "place": self.place_of(oid), "holder": self.holder_of(oid),
                        "hidden": self.hidden(oid)}
        return out
