"""Rooms, furniture and the places on and in each piece.

A place is a surface (things on top of it are seen from anywhere in the room),
an open container (a sink, a basket shelf: what is inside is seen) or a closed
container (a drawer, a cabinet, the fridge: what is inside is seen only by
someone standing at it). "Under the bed" is not a place: it is the relation
under, with the bed's spot as reference. Each place has 2 to 4 plain
descriptions a person might use for it.

Layouts are made per household (lived_home.household), from an HSSD scene
(lived_home.hssd_home) or invented by the model. PILOT_HOME, the draft's
hand-written home, stays as the fallback for tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SURFACE, OPEN, CLOSED = "surface", "open", "closed"
CONTAINER = CLOSED                     # older layouts said "container" for closed ones
KINDS = [SURFACE, OPEN, CLOSED]


@dataclass
class Place:
    id: str
    room: str
    furniture: str
    name: str
    kind: str                       # SURFACE, OPEN or CLOSED
    hidden: bool = False            # older layouts only; no longer used
    descriptions: list = field(default_factory=list)
    geometry: dict = field(default_factory=dict)   # from a 3D home: furniture, centre, height

    def __post_init__(self):
        if self.kind == "container":
            self.kind = CLOSED

    @property
    def is_container(self) -> bool:
        return self.kind in (OPEN, CLOSED)


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
                    tags = [t for t, on in (("closed", p.kind == CLOSED),
                                            ("open container", p.kind == OPEN)) if on]
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
                                        s["kind"], s.get("hidden", False), list(s["descriptions"]),
                                        dict(s.get("geometry") or {})))
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
        ("kitchen_sink", "sink", OPEN),
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
        ("laundry_hamper", "laundry hamper", CLOSED),
        ("laundry_washer", "washing machine drum", CLOSED),
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
