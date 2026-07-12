"""
Change events and semantic slot definitions for Dynamic EQA.

SLOT_ANCHORS  — our semantic slot names (used in manifests).
SLOT_TO_FURNITURE_TYPE — maps our slots to PARTNR WorldGraph Furniture.properties["type"]
                         values so the adapter can translate between representations.
SLOT_DESCRIPTIONS — human-readable labels used in MCQ answer text.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from .state import SceneState, ObjectInstance


MAX_MOVE_DIST = 3.0

# ---------------------------------------------------------------------------
# Semantic slot registry
# ---------------------------------------------------------------------------

SLOT_ANCHORS: dict[str, dict] = {
    "dining.table":               {"cats": ["table"],          "offset": "on_surface",       "dist": 0.0},
    "dining.table_pulled_out":    {"cats": ["table"],          "offset": "away_from_anchor", "dist": 0.65},
    "dining.table_tucked":        {"cats": ["table"],          "offset": "toward_anchor",    "dist": 0.30},
    "kitchen.counter":            {"cats": ["cabinet", "counter"], "offset": "on_surface",   "dist": 0.0},
    "kitchen.counter_tucked":     {"cats": ["stool", "chair"], "offset": "current",          "dist": 0.0},
    "kitchen.counter_pulled_out": {"cats": ["cabinet", "counter"], "offset": "away_from_anchor", "dist": 0.55},
    "living_room.sofa":           {"cats": ["couch", "bench"], "offset": "on_surface",       "dist": 0.0},
    "living_room.open_floor":     {"cats": ["couch", "table"], "offset": "floor_near",       "dist": 1.4},
    "living_room.corner":         {"cats": ["potted_plant"],   "offset": "current",          "dist": 0.0},
    "living_room.window_sill":    {"cats": ["potted_plant", "table"], "offset": "away_from_anchor", "dist": 0.8},
    "living_room.shelf":          {"cats": ["shelves", "cabinet"], "offset": "on_surface",   "dist": 0.0},
    "office.desk":                {"cats": ["table"],          "offset": "on_surface",       "dist": 0.0},
    "office.shelf":               {"cats": ["shelves", "cabinet"], "offset": "on_surface",   "dist": 0.0},
    "kitchen.cabinet":            {"cats": ["cabinet"],        "offset": "on_surface",       "dist": 0.0},
    "bedroom.bed":                {"cats": ["bed"],            "offset": "on_surface",       "dist": 0.0},
    "bedroom.nightstand":         {"cats": ["stand", "table"], "offset": "on_surface",       "dist": 0.0},
}

# Maps our semantic slots → PARTNR Furniture.properties["type"] values.
# Used by world_graph_adapter to convert WorldGraph ↔ SceneState.
SLOT_TO_FURNITURE_TYPE: dict[str, list[str]] = {
    "dining.table":               ["table_dining", "table"],
    "dining.table_pulled_out":    ["table_dining", "table"],
    "dining.table_tucked":        ["table_dining", "table"],
    "kitchen.counter":            ["counter", "kitchen_counter"],
    "kitchen.counter_tucked":     ["counter", "kitchen_counter"],
    "kitchen.counter_pulled_out": ["counter", "kitchen_counter"],
    "living_room.sofa":           ["sofa", "couch"],
    "living_room.open_floor":     ["floor"],
    "living_room.corner":         ["floor"],
    "living_room.window_sill":    ["windowsill", "shelf"],
    "living_room.shelf":          ["shelf", "bookcase", "shelves"],
    "office.desk":                ["desk", "table_office"],
    "office.shelf":               ["shelf", "bookcase"],
    "kitchen.cabinet":            ["cabinet", "kitchen_cabinet"],
    "bedroom.bed":                ["bed"],
    "bedroom.nightstand":         ["stand", "chest_of_drawers", "nightstand"],
}

# Reverse map: PARTNR furniture type → our slot (first matching wins).
FURNITURE_TYPE_TO_SLOT: dict[str, str] = {}
for _slot, _types in SLOT_TO_FURNITURE_TYPE.items():
    for _t in _types:
        if _t not in FURNITURE_TYPE_TO_SLOT:
            FURNITURE_TYPE_TO_SLOT[_t] = _slot

# Human-readable descriptions for MCQ answer options.
SLOT_DESCRIPTIONS: dict[str, str] = {
    "dining.table":               "the dining table",
    "dining.table_pulled_out":    "the dining table (pulled out)",
    "dining.table_tucked":        "the dining table (tucked in)",
    "kitchen.counter":            "the kitchen counter",
    "kitchen.counter_tucked":     "the kitchen counter (tucked)",
    "kitchen.counter_pulled_out": "the kitchen counter (pulled out)",
    "living_room.sofa":           "the living room sofa",
    "living_room.open_floor":     "the open living room floor",
    "living_room.corner":         "the living room corner",
    "living_room.window_sill":    "the window sill",
    "living_room.shelf":          "the living room shelf",
    "office.desk":                "the office desk",
    "office.shelf":               "the office shelf",
    "kitchen.cabinet":            "the kitchen cabinet",
    "bedroom.bed":                "the bedroom bed",
    "bedroom.nightstand":         "the bedroom nightstand",
}


def slot_desc(slot: str) -> str:
    """Human-readable description for a slot key."""
    return SLOT_DESCRIPTIONS.get(slot, slot.replace(".", " ").replace("_", " ") if slot else "unknown location")


# ---------------------------------------------------------------------------
# State-variable registry (M3: state-change dynamics)
# ---------------------------------------------------------------------------

# {variable: {"cats": [furniture categories this variable applies to],
#             "values": (off_value, on_value)}} — mirrors SLOT_ANCHORS's
# shape. Values are deliberately richer than bare "on"/"off": rooms.py's
# resolve_slot() fallback synthesizes f"{anchor}.on" as a *location* slot
# (rooms.py) when no other resolution applies, so a state value literally
# named "on"/"off" would be ambiguous with that synthesized location-slot
# suffix. tests/test_state_variable_naming.py lints every value here
# against that collision, not just this docstring's promise.
#
# v1 wires two variables (power, door) to concrete trigger rules in
# generation/state_rules.py and exercises them in the generated state
# stratum; a third axis (e.g. full/empty for trashcan) fits the same shape
# but isn't wired to a rule yet — adding it is a registry entry plus a
# trigger rule, not a new mechanism.
STATE_VARIABLES: dict[str, dict] = {
    "power": {"cats": ["oven", "tv"], "values": ("unpowered", "powered")},
    "door":  {"cats": ["fridge", "wardrobe"], "values": ("closed", "open")},
}


# ---------------------------------------------------------------------------
# Change dataclass
# ---------------------------------------------------------------------------

@dataclass
class DeltaSpec:
    change_type: str        # "move_existing" | "insert_new" | "remove"
    object_category: str
    from_semantic: str
    to_semantic: str
    reason: str


@dataclass
class Change:
    """A committed scene change from the day timeline."""
    activity:        str
    phase:           str       # "enter" | "exit"
    instance_id:     str
    change_type:     str       # "move_existing" | "insert_new" | "remove" | "state_change"
    object_category: str
    from_semantic:   str
    to_semantic:     str
    reason:          str
    t:               float     # hour of day (24h clock)
    # Populated only for change_type == "state_change" (M3); None for a
    # location change. from_semantic/to_semantic still carry the object's
    # (unchanged) location for that event, so slot_room()-based attendance
    # checks work unmodified — a state_change event moves nothing, it only
    # flips one of STATE_VARIABLES's variables.
    state_variable:  Optional[str] = None
    from_state:      Optional[str] = None
    to_state:        Optional[str] = None
    # The LLM proposal's own spatial relation (on/on_top/inside/within/
    # near/next_to), carried through the manifest since the Floor-Bound
    # Realization round: the builder needs it to realize near/next_to as a
    # floor placement BESIDE the anchor instance rather than on its
    # surface — before this field existed, "chair next_to kitchen.table_1"
    # was realized as a chair ON the table, because the slot string alone
    # cannot distinguish the two. None on legacy manifests and state
    # changes; the builder treats None as the old on-surface behavior.
    target_relationship: Optional[str] = None


PositionFn  = Callable[[str], Optional[np.ndarray]]
AnchorPosFn = Callable[[str], Optional[np.ndarray]]


def resolve_instance(
    category: str,
    target_semantic: str,
    state: SceneState,
    rng: np.random.Generator,
) -> Optional[str]:
    """Find or create an instance_id for the given category at target_semantic."""
    candidates = [
        iid for iid, inst in state.instances.items()
        if inst.category == category and inst.current_semantic == target_semantic
    ]
    if candidates:
        return rng.choice(candidates)
    all_cat = [iid for iid, inst in state.instances.items() if inst.category == category]
    return rng.choice(all_cat) if all_cat else None
