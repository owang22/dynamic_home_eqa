"""The rooms and places of the pilot home.

A place is either a surface (things on it can be seen from the room) or a
container (closed: a cabinet, drawer, fridge, closet, bin). People know what is
inside containers in the room they are in; the robot does not.
"""
from __future__ import annotations

SURFACE, CONTAINER = "surface", "container"

# room -> list of (place id, plain name, kind)
PILOT_HOME = {
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
        ("living_bookshelf", "bookshelf", SURFACE),
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


class Layout:
    def __init__(self, rooms: dict = PILOT_HOME) -> None:
        self.rooms = rooms
        self.room_of, self.name_of, self.kind_of = {}, {}, {}
        for room, places in rooms.items():
            for pid, name, kind in places:
                self.room_of[pid], self.name_of[pid], self.kind_of[pid] = room, name, kind

    @property
    def place_ids(self) -> list[str]:
        return list(self.room_of)

    def places_in(self, room: str) -> list[str]:
        return [pid for pid, _, _ in self.rooms[room]]

    def describe(self) -> str:
        """Plain listing for prompts: one line per room."""
        lines = []
        for room, places in self.rooms.items():
            parts = [f"{pid} ({name}{', closed' if kind == CONTAINER else ''})"
                     for pid, name, kind in places]
            lines.append(f"{room}: " + "; ".join(parts))
        return "\n".join(lines)
