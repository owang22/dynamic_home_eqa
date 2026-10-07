"""Strict JSON schemas. Each response opens with free text, written before any
structured choice, so the structure does not shape the reasoning."""
from __future__ import annotations

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
VERBS = ["go", "pick_up", "put_down", "pocket", "give", "do", "say", "leave_home"]
HOW_OFTEN_HABIT = ["almost always", "most times", "sometimes"]
HOW_OFTEN_SITUATION = ["rarely", "about monthly", "about every two weeks", "about weekly"]
SITUATION_KINDS = ["one_off", "recurring", "lasting"]


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


def _null_or(sub: dict) -> dict:
    return {"anyOf": [sub, {"type": "null"}]}


STR = {"type": "string"}
LEVEL = {"type": "integer", "enum": [0, 1, 2, 3]}
INNER_STATE = _obj({
    "stress": LEVEL, "tiredness": LEVEL,
    "mood": LEVEL,     # 0 bad, 3 good
    "health": LEVEL,   # 0 very unwell, 3 well
    "reason": STR,
})


def household_schema(place_ids: list[str], rooms: list[str]) -> dict:
    routine_item = _obj({
        "days": _arr({"type": "string", "enum": WEEKDAYS}, 1, 7),
        "start": STR, "end": STR, "activity": STR,
        "room": {"type": "string", "enum": rooms + ["out_of_house"]},
    })
    resident = _obj({
        "id": STR, "name": STR, "age": {"type": "integer"}, "job": STR,
        "personality": STR,
        "weekly_routine": _arr(routine_item, 10, 60),
        "object_habits": _arr(STR, 4, 12),
        "response_habits": _arr(_obj({
            "id": STR, "trigger": STR, "behavior": STR,
            "how_often": {"type": "string", "enum": HOW_OFTEN_HABIT},
        }), 4, 10),
        "scheduled_stressors": _arr(STR, 1, 5),
    })
    obj = _obj({
        "id": STR, "name": STR, "owner": STR,
        "home": {"type": "string", "enum": place_ids},
        "pocketable": {"type": "boolean"},
    })
    situation = _obj({
        "id": STR,
        "kind": {"type": "string", "enum": SITUATION_KINDS},
        "how_often": {"type": "string", "enum": HOW_OFTEN_SITUATION},
        "typical_days": {"type": "integer"},
        "happens_to": _arr(STR, 1, 2),
        "what_it_is_like": STR,
        "what_others_notice": STR,
    })
    return _obj({
        "thinking": STR,
        "residents": _arr(resident, 2, 2),
        "objects": _arr(obj, 45, 75),
        "situations": _arr(situation, 15, 25),
        "small_disturbances": _arr(_obj({"who": STR, "text": STR}), 12, 24),
    })


def plan_schema(rooms: list[str]) -> dict:
    activity = _obj({
        "start": STR, "end": STR, "activity": STR,
        "room": {"type": "string", "enum": rooms + ["out_of_house"]},
        "intention": STR,
    })
    return _obj({"thinking": STR, "inner_state": INNER_STATE,
                 "activities": _arr(activity, 6, 30)})


def act_schema(object_ids: list[str], place_ids: list[str], people: list[str],
               habit_ids: list[str]) -> dict:
    action = _obj({
        "verb": {"type": "string", "enum": VERBS},
        "object": _null_or({"type": "string", "enum": object_ids}),
        "place": _null_or({"type": "string", "enum": place_ids}),
        "person": _null_or({"type": "string", "enum": people}),
        "minutes": _null_or({"type": "integer"}),
        "text": _null_or(STR),
        "why": STR,
    })
    return _obj({
        "thinking": STR,
        "inner_state": INNER_STATE,
        "habit_followed": {"type": "string", "enum": habit_ids + ["none"]},
        "actions": _arr(action, 1, 30),
    })
