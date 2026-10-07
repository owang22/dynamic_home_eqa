"""Rooms, furniture and the places on and in each piece.

A place is a surface (things on it are seen from anywhere in the room) or a
closed container (a drawer, a cabinet, the fridge: its contents are seen only
by someone standing at it). A surface can also be hidden from the room, like
the floor under the bed. Each place has 2 to 4 plain descriptions a person
might use for it.

Layouts are generated per household (lived_home.household). PILOT_HOME, the
draft's hand-written home, stays as the fallback for tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SURFACE, CONTAINER = "surface", "container"


@dataclass
class Place:
    id: str
    room: str
    furniture: str
    name: str
    kind: str                       # SURFACE or CONTAINER
    hidden: bool = False            # True: not seen from the room (under the bed)
    descriptions: list = field(default_factory=list)

    @property
    def seen_from_room(self) -> bool:
        return self.kind == SURFACE and not self.hidden


class Layout:
    def __init__(self, places: list[Place], entry: str) -> None:
        self.places = {p.id: p for p in places}
        self.rooms: dict[str, list[str]] = {}
        for p in places:
            self.rooms.setdefault(p.room, []).append(p.id)
        if entry not in self.places:
            raise ValueError(f"entry place {entry} is not a place")
        self.entry = entry

    @property
    def place_ids(self) -> list[str]:
        return list(self.places)

    def room_of(self, place: str) -> str:
        return self.places[place].room

    def places_in(self, room: str) -> list[str]:
        return self.rooms[room]

    def describe(self) -> str:
        """Plain listing for prompts: one line per piece of furniture."""
        lines = []
        for room, ids in self.rooms.items():
            lines.append(f"{room}:")
            by_furniture: dict[str, list[Place]] = {}
            for pid in ids:
                p = self.places[pid]
                by_furniture.setdefault(p.furniture, []).append(p)
            for furniture, places in by_furniture.items():
                parts = []
                for p in places:
                    tags = [t for t, on in (("closed", p.kind == CONTAINER),
                                            ("out of sight", p.hidden)) if on]
                    parts.append(f"{p.id} ({p.name}{', ' + ', '.join(tags) if tags else ''})")
                lines.append(f"  {furniture}: " + "; ".join(parts))
        return "\n".join(lines)

    def to_json(self) -> dict:
        return {"entry": self.entry, "places": [vars(p) for p in self.places.values()]}

    @classmethod
    def from_json(cls, data: dict) -> "Layout":
        return cls([Place(**p) for p in data["places"]], data["entry"])

    @classmethod
    def from_generated(cls, spec: dict) -> "Layout":
        """From the layout call's answer (see schemas.layout_schema)."""
        places = []
        for room in spec["rooms"]:
            for piece in room["furniture"]:
                for s in piece["spots"]:
                    places.append(Place(s["id"], room["id"], piece["name"], s["name"],
                                        s["kind"], s["hidden"], list(s["descriptions"])))
        return cls(places, spec["entry_spot"])


# The draft's hand-written home, for tests: room -> (place id, name, kind[, hidden]).
_PILOT = {
    "entryway": [
        ("entry_key_bowl", "bowl on the entry table", SURFACE),
        ("entry_table", "entry table", SURFACE),
        ("entry_coat_hooks", "coat hooks", SURFACE),
        ("entry_shoe_rack", "shoe rack", SURFACE),
        ("entry_closet", "entry closet", CONTAINER),
    ],
    "living_room": [
        ("living_couch", "couch", SURFACE),
        ("living_couch_under_cushions", "under the couch cushions", SURFACE, True),
        ("living_armchair", "armchair", SURFACE),
        ("living_coffee_table", "coffee table", SURFACE),
        ("living_tv_stand", "TV stand", SURFACE),
        ("living_bookshelf_top", "top shelf of the bookshelf", SURFACE),
        ("living_bookshelf_bottom", "bottom shelf of the bookshelf", SURFACE),
        ("living_side_table", "side table by the armchair", SURFACE),
        ("living_tv_cabinet", "cabinet under the TV", CONTAINER),
    ],
    "kitchen": [
        ("kitchen_counter_by_stove", "counter next to the stove", SURFACE),
        ("kitchen_counter_by_sink", "counter next to the sink", SURFACE),
        ("kitchen_stovetop", "stovetop", SURFACE),
        ("kitchen_island", "kitchen island", SURFACE),
        ("kitchen_windowsill", "kitchen windowsill", SURFACE),
        ("kitchen_dish_rack", "dish rack", SURFACE),
        ("kitchen_sink", "sink", SURFACE),
        ("kitchen_upper_cabinet", "upper cabinet", CONTAINER),
        ("kitchen_lower_cabinet", "lower cabinet", CONTAINER),
        ("kitchen_pantry", "pantry", CONTAINER),
        ("kitchen_drawer", "kitchen drawer", CONTAINER),
        ("kitchen_fridge", "fridge", CONTAINER),
        ("kitchen_oven", "oven", CONTAINER),
        ("kitchen_dishwasher", "dishwasher", CONTAINER),
    ],
    "dining_area": [
        ("dining_table", "dining table", SURFACE),
        ("dining_chair", "dining chair", SURFACE),
        ("dining_sideboard", "sideboard", CONTAINER),
    ],
    "main_bedroom": [
        ("bed", "bed", SURFACE),
        ("under_bed", "under the bed", SURFACE, True),
        ("nightstand_left", "left nightstand", SURFACE),
        ("nightstand_right", "right nightstand", SURFACE),
        ("dresser_top", "top of the dresser", SURFACE),
        ("bedroom_chair", "chair in the bedroom", SURFACE),
        ("dresser_drawers", "dresser drawers", CONTAINER),
        ("bedroom_closet", "bedroom closet", CONTAINER),
    ],
    "office": [
        ("office_desk", "desk", SURFACE),
        ("office_chair", "desk chair", SURFACE),
        ("office_shelf", "office shelf", SURFACE),
        ("office_sofa_bed", "sofa bed", SURFACE),
        ("office_desk_drawer", "desk drawer", CONTAINER),
    ],
    "bathroom": [
        ("bathroom_sink_counter", "bathroom sink counter", SURFACE),
        ("bathroom_towel_rack", "towel rack", SURFACE),
        ("bathroom_bathtub_edge", "edge of the bathtub", SURFACE),
        ("bathroom_cabinet", "cabinet behind the mirror", CONTAINER),
        ("laundry_hamper", "laundry hamper", CONTAINER),
    ],
    "balcony": [
        ("balcony_table", "balcony table", SURFACE),
        ("balcony_chair", "balcony chair", SURFACE),
    ],
}


def pilot_layout() -> Layout:
    places = []
    for room, rows in _PILOT.items():
        for row in rows:
            pid, name, kind = row[:3]
            hidden = row[3] if len(row) > 3 else False
            places.append(Place(pid, room, name, name, kind, hidden,
                                [f"the {name}", f"the {name} in the {room.replace('_', ' ')}"]))
    return Layout(places, "entry_table")
