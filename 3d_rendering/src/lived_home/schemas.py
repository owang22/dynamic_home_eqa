"""Strict JSON schemas. Each response opens with free text, written in character
before any structured choice, so the structure does not shape the reasoning.

Absent values are empty strings (or 0 for minutes), never null, so every field
is always present and strict mode needs no optional properties.
"""
from __future__ import annotations

import json

from lived_home.world import CARRIER_KINDS, RELATIONS

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
VERBS = ["go", "pick_up", "put_down", "pocket", "wear", "give", "do", "say", "leave_home"]
HOW_OFTEN_HABIT = ["almost always", "most times", "sometimes"]
HOW_OFTEN_SITUATION = ["rarely", "about monthly", "about every two weeks", "about weekly"]
SITUATION_KINDS = ["one_off", "recurring", "lasting"]
SIZES = ["small", "medium", "large"]
ENUM_BUDGET = 1000      # OpenAI strict mode: enum values in total, after dedup


def _obj(props: dict) -> dict:
    return {"type": "object", "properties": props,
            "required": list(props), "additionalProperties": False}


def _arr(item: dict, lo: int = 0, hi: int = 0) -> dict:
    out = {"type": "array", "items": item}
    if lo:
        out["minItems"] = lo
    if hi:
        out["maxItems"] = hi
    return out


def _enum(values: list) -> dict:
    return {"type": "string", "enum": list(values)}


STR = {"type": "string"}
BOOL = {"type": "boolean"}
LEVEL = {"type": "integer", "enum": [0, 1, 2, 3]}
INNER_STATE = _obj({
    "stress": LEVEL, "tiredness": LEVEL,
    "mood": LEVEL,     # 0 bad, 3 good
    "health": LEVEL,   # 0 very unwell, 3 well
    "reason": STR,
})


def enum_count(schema: dict) -> int:
    """Enum values OpenAI counts: each distinct enum list once (the hosted
    transform hoists repeated identical enums into $defs)."""
    seen = set()

    def scan(node):
        if isinstance(node, dict):
            if "enum" in node:
                seen.add(json.dumps(node["enum"], sort_keys=True))
            for v in node.values():
                scan(v)
        elif isinstance(node, list):
            for v in node:
                scan(v)
    scan(schema)
    return sum(len(json.loads(e)) for e in seen)


# ------------------------------------------------------------ household creation
def layout_schema() -> dict:
    spot = _obj({
        "id": STR, "name": STR,
        "kind": _enum(["surface", "container"]),
        "hidden": BOOL,
        "descriptions": _arr(STR, 2, 4),
    })
    furniture = _obj({"name": STR, "spots": _arr(spot, 1, 14)})
    room = _obj({"id": STR, "furniture": _arr(furniture, 1, 16)})
    return _obj({"thinking": STR, "home": STR,
                 "rooms": _arr(room, 5, 12), "entry_spot": STR})


def residents_schema(place_ids: list[str], rooms: list[str]) -> dict:
    routine_item = _obj({
        "days": _arr(_enum(WEEKDAYS), 1, 7),
        "start": STR, "end": STR, "activity": STR,
        "room": _enum(rooms + ["out_of_house"]),
    })
    resident = _obj({
        "id": STR, "name": STR, "age": {"type": "integer"}, "job": STR,
        "personality": STR,
        "sleeps_at": _enum(place_ids),
        "weekly_routine": _arr(routine_item, 10, 60),
        "object_habits": _arr(STR, 5, 14),
        "response_habits": _arr(_obj({
            "id": STR, "trigger": STR, "behavior": STR,
            "how_often": _enum(HOW_OFTEN_HABIT),
        }), 4, 10),
        "scheduled_stressors": _arr(STR, 1, 5),
    })
    return _obj({"thinking": STR, "residents": _arr(resident, 2, 2)})


def room_objects_schema(place_ids: list[str], owners: list[str], lo: int, hi: int,
                        owner_required: bool = False) -> dict:
    obj = _obj({
        "n": {"type": "integer"}, "type": STR, "looks": STR,
        "color": STR, "material": STR, "size": _enum(SIZES),
        "pattern": STR, "condition": STR,
        "owner": _enum(owners if owner_required else owners + ["none"]),
        "pocketable": BOOL,
        "carrier": _enum(CARRIER_KINDS),
        "place": _enum(place_ids),
        "relation": _enum(RELATIONS),
        "ref": {"type": "integer"},
    })
    return _obj({"thinking": STR, "objects": _arr(obj, lo, hi)})


def situations_schema(resident_ids: list[str]) -> dict:
    situation = _obj({
        "id": STR,
        "kind": _enum(SITUATION_KINDS),
        "how_often": _enum(HOW_OFTEN_SITUATION),
        "typical_days": {"type": "integer"},
        "happens_to": _arr(_enum(resident_ids), 1, 2),
        "what_it_is_like": STR,
        "what_others_notice": STR,
    })
    return _obj({
        "thinking": STR,
        "situations": _arr(situation, 15, 25),
        "small_disturbances": _arr(_obj({"who": _enum(resident_ids + ["anyone"]),
                                         "text": STR}), 12, 24),
    })


# ------------------------------------------------------------------- daily life
def plan_schema(rooms: list[str], types: list[str]) -> dict:
    activity = _obj({
        "start": STR, "end": STR, "activity": STR,
        "room": _enum(rooms + ["out_of_house"]),
        "intention": STR,
        "uses": _arr(_enum(types), 0, 8),
    })
    return _obj({"thinking": STR, "inner_state": INNER_STATE,
                 "activities": _arr(activity, 6, 30)})


def act_schema(object_ids: list[str], place_ids: list[str], people: list[str],
               habit_ids: list[str], use_enums: bool = True) -> dict:
    """use_enums=False: object and place ids become plain strings, checked in code."""
    obj = _enum(object_ids + [""]) if use_enums else STR
    place = _enum(place_ids + [""]) if use_enums else STR
    action = _obj({
        "verb": _enum(VERBS),
        "object": obj,
        "place": place,
        "relation": _enum(RELATIONS + [""]),
        "ref": obj,
        "person": _enum(people + [""]),
        "minutes": {"type": "integer"},
        "text": STR,
        "why": STR,
    })
    return _obj({
        "thinking": STR,
        "inner_state": INNER_STATE,
        "habit_triggers_now": _arr(_enum(habit_ids), 0, len(habit_ids)),
        "habit_followed": _enum(habit_ids + ["none"]),
        "actions": _arr(action, 1, 30),
    })


def act_schema_fitting(object_ids, place_ids, people, habit_ids) -> tuple[dict, bool]:
    schema = act_schema(object_ids, place_ids, people, habit_ids, True)
    if enum_count(schema) <= ENUM_BUDGET:
        return schema, True
    return act_schema(object_ids, place_ids, people, habit_ids, False), False
