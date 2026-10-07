"""The truth of the home: where every object is and what each resident holds.

Every object is in exactly one spot: a place, a resident's hand, or a resident's
pocket. Objects move only when a resident acts on them, so nothing teleports.
Each resident also keeps their own memory of where they last saw each object,
which can be out of date when someone else moved it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from lived_home.home_layout import CONTAINER, Layout

HANDS = 2
ENTRY_PLACE = "entry_table"


def clock(minute: int) -> str:
    return f"{(minute // 60) % 24:02d}:{minute % 60:02d}"


@dataclass
class Resident:
    rid: str
    at: Optional[str]                     # place id, or None while out of the house
    hands: list = field(default_factory=list)
    pocket: list = field(default_factory=list)
    back_at: int = -1                     # minute of return while out
    belief: dict = field(default_factory=dict)  # object -> (spot text, day, minute)


class World:
    def __init__(self, layout: Layout, objects: dict, resident_ids: list[str],
                 start_place: dict) -> None:
        """objects: id -> {name, owner, home, pocketable}."""
        self.layout, self.objects = layout, objects
        self.where = {oid: ("place", o["home"]) for oid, o in objects.items()}
        self.people = {r: Resident(r, start_place[r]) for r in resident_ids}
        for person in self.people.values():
            person.belief = {oid: (o["home"], -1, 0) for oid, o in objects.items()}
        self.day, self.log = 0, []

    # ---- what people see ----
    def room_of_person(self, rid: str) -> Optional[str]:
        at = self.people[rid].at
        return self.layout.room_of[at] if at else None

    def things_at(self, place: str) -> list[str]:
        return [o for o, w in self.where.items() if w == ("place", place)]

    def _see_room(self, rid: str, minute: int) -> None:
        person, room = self.people[rid], self.room_of_person(rid)
        if room is None:
            return
        for place in self.layout.places_in(room):
            if self.layout.kind_of[place] == CONTAINER and place != person.at:
                continue
            for oid in self.things_at(place):
                person.belief[oid] = (place, self.day, minute)
        for other in self.people.values():
            if other.rid != rid and other.at and self.layout.room_of[other.at] == room:
                for oid in other.hands:
                    person.belief[oid] = (f"in {other.rid}'s hand", self.day, minute)

    def room_view(self, rid: str) -> str:
        """What the resident sees around them, for their prompt."""
        room = self.room_of_person(rid)
        if room is None:
            return "You are out of the house."
        lines = [f"You are in the {room}, at {self.people[rid].at}."]
        empty = []
        for place in self.layout.places_in(room):
            things = self.things_at(place)
            if things:
                lines.append(f"  {place}: {', '.join(things)}")
            else:
                empty.append(place)
        if empty:
            lines.append(f"  Empty: {', '.join(empty)}")
        for other in self.people.values():
            if other.rid != rid and other.at and self.layout.room_of[other.at] == room:
                lines.append(f"  {other.rid} is here, holding {', '.join(other.hands) or 'nothing'}")
        return "\n".join(lines)

    def memory_view(self, rid: str) -> str:
        person, lines = self.people[rid], []
        for oid, (spot, day, minute) in person.belief.items():
            if oid in person.hands or oid in person.pocket:
                continue
            when = "its usual spot" if day < 0 else f"day {day} {clock(minute)}"
            lines.append(f"  {oid}: {spot} (last seen: {when})")
        return "\n".join(lines)

    # ---- acting ----
    def apply(self, rid: str, act: dict, minute: int) -> tuple[bool, str, int]:
        """Carry out one action. Returns (done, message, minutes taken)."""
        person, verb = self.people[rid], act["verb"]
        oid, place = act.get("object"), act.get("place")
        if person.at is None:
            return False, "You are out of the house.", 0
        if verb == "go":
            if place not in self.layout.room_of:
                return False, f"There is no place called {place}.", 0
            steps = 0 if self.layout.room_of[place] == self.room_of_person(rid) else 1
            source, person.at = person.at, place
            self._see_room(rid, minute + steps)
            return self._done(rid, act, minute, source, place, steps)
        if verb == "pick_up":
            if oid not in self.objects:
                return False, f"There is no object called {oid}.", 0
            if self.where[oid] != ("place", person.at):
                person.belief[oid] = (f"not at {person.at}", self.day, minute)
                here = ", ".join(self.things_at(person.at)) or "nothing"
                return False, f"{oid} is not at {person.at}. Here you see: {here}.", 0
            if len(person.hands) >= HANDS:
                return False, f"Your hands are full ({', '.join(person.hands)}).", 0
            self.where[oid] = ("hand", rid)
            person.hands.append(oid)
            return self._done(rid, act, minute, person.at, "hand", 0)
        if verb in ("put_down", "pocket", "give"):
            if oid in person.pocket:
                source = "pocket"
            elif oid in person.hands:
                source = "hand"
            else:
                return False, f"You are not holding {oid}.", 0
            if verb == "put_down":
                self._release(person, oid)
                self.where[oid] = ("place", person.at)
                person.belief[oid] = (person.at, self.day, minute)
                return self._done(rid, act, minute, source, person.at, 0)
            if verb == "pocket":
                if not self.objects[oid].get("pocketable"):
                    return False, f"{oid} does not fit in a pocket.", 0
                self._release(person, oid)
                self.where[oid] = ("pocket", rid)
                person.pocket.append(oid)
                return self._done(rid, act, minute, source, "pocket", 0)
            other = self.people.get(act.get("person") or "")
            if other is None or other.rid == rid:
                return False, "Give it to whom?", 0
            if other.at is None or self.layout.room_of[other.at] != self.room_of_person(rid):
                return False, f"{other.rid} is not in this room.", 0
            if len(other.hands) >= HANDS:
                return False, f"{other.rid}'s hands are full.", 0
            self._release(person, oid)
            self.where[oid] = ("hand", other.rid)
            other.hands.append(oid)
            other.belief[oid] = (f"in your hand", self.day, minute)
            return self._done(rid, act, minute, source, f"{other.rid}'s hand", 1)
        if verb == "do":
            return self._done(rid, act, minute, person.at, person.at, max(1, act.get("minutes") or 1))
        if verb == "say":
            return self._done(rid, act, minute, person.at, person.at, 1)
        if verb == "leave_home":
            minutes = max(5, act.get("minutes") or 30)
            source, person.at, person.back_at = person.at, None, minute + minutes
            return self._done(rid, act, minute, source, "out of the house", minutes)
        return False, f"Unknown action {verb}.", 0

    def come_home_if_due(self, rid: str, minute: int) -> None:
        person = self.people[rid]
        if person.at is None and minute >= person.back_at:
            person.at = ENTRY_PLACE
            self._see_room(rid, minute)

    def _release(self, person: Resident, oid: str) -> None:
        if oid in person.hands:
            person.hands.remove(oid)
        if oid in person.pocket:
            person.pocket.remove(oid)

    def _done(self, rid, act, minute, source, dest, minutes) -> tuple[bool, str, int]:
        self.log.append({
            "day": self.day, "minute": minute, "time": clock(minute), "resident": rid,
            "verb": act["verb"], "object": act.get("object"), "from": source, "to": dest,
            "minutes": minutes, "text": act.get("text"), "person": act.get("person"),
            "why": act.get("why"),
        })
        return True, "", minutes

    def snapshot(self) -> dict:
        """Where every object is right now, as plain strings."""
        out = {}
        for oid, (kind, spot) in self.where.items():
            out[oid] = spot if kind == "place" else f"{kind}:{spot}"
        return out
