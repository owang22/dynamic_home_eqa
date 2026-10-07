"""Household creation in several calls: layout, residents, objects room by room,
then situations. References between calls are checked in code, and a failed
check is retried with the problem named."""
from __future__ import annotations

import collections
import json
import pathlib
import random
import re

from lived_home import prompts
from lived_home.calls import Caller, to_minute
from lived_home.layout import CONTAINER, Layout
from lived_home.schemas import (layout_schema, residents_schema, room_objects_schema,
                                situations_schema)
from lived_home.world import at_place

ID = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
PLACES_LO, PLACES_HI = 100, 200
OBJECTS_LO, OBJECTS_HI, OBJECTS_TARGET = 150, 300, 220


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


# ------------------------------------------------------------------ checks
def check_layout(spec: dict) -> str:
    rooms = [r["id"] for r in spec["rooms"]]
    if len(set(rooms)) != len(rooms):
        return "Room ids must be unique."
    bad_rooms = [r for r in rooms if not ID.match(r)]
    if bad_rooms:
        return f"Room ids must be lowercase with underscores: {bad_rooms}."
    spots = [s["id"] for r in spec["rooms"] for f in r["furniture"] for s in f["spots"]]
    dupes = sorted({s for s in spots if spots.count(s) > 1})
    if dupes:
        return f"Spot ids must be unique across the home; repeated: {dupes[:20]}."
    bad = [s for s in spots if not ID.match(s)]
    if bad:
        return f"Spot ids must be lowercase with underscores: {bad[:20]}."
    if not PLACES_LO <= len(spots) <= PLACES_HI:
        return (f"The home has {len(spots)} spots; it needs {PLACES_LO} to {PLACES_HI}. "
                + ("Add the spots on and in each piece of furniture (each shelf, each drawer, "
                   "each end of a counter)." if len(spots) < PLACES_LO else "Merge some."))
    if spec["entry_spot"] not in spots:
        return f"entry_spot {spec['entry_spot']} is not one of the spot ids."
    return ""


def check_residents(layout: Layout):
    def check(spec: dict) -> str:
        ids = [r["id"] for r in spec["residents"]]
        if len(set(ids)) != len(ids):
            return "The two residents need different ids."
        for r in spec["residents"]:
            if not re.match(r"^[a-z]+$", r["id"]):
                return f"Resident id {r['id']} must be a lowercase first name."
            habit_ids = [h["id"] for h in r["response_habits"]]
            if len(set(habit_ids)) != len(habit_ids):
                return f"{r['id']}'s response habit ids must be unique."
            if layout.places[r["sleeps_at"]].kind == CONTAINER:
                return f"{r['id']} sleeps_at {r['sleeps_at']}, which is a closed container."
            for item in r["weekly_routine"]:
                if to_minute(item["start"]) is None or to_minute(item["end"]) is None:
                    return f"Routine times must be HH:MM, got {item['start']} and {item['end']}."
        return ""
    return check


def check_room_objects(room_places: set, taken: set, layout: Layout):
    def check(ans: dict) -> str:
        seen: dict[str, dict] = {}
        for o in ans["objects"]:
            oid, kind = o["id"], slug(o["type"])
            if not ID.match(oid):
                return f"Object id {oid} must be lowercase with underscores."
            if oid in seen or oid in taken:
                return f"Object id {oid} is already used; make it describe what sets this one apart."
            if not kind or not oid.startswith(kind):
                return f"Object id {oid} must start with its type ({kind})."
            if oid == kind:
                return f"Object id {oid} must add what sets it apart from other {o['type']}s."
            if o["place"] not in room_places:
                return f"{oid} is at {o['place']}, which is not a spot in this room."
            ref = o["ref"]
            if ref:
                if ref not in seen:
                    return f"{oid} has ref {ref}, which is not an object listed before it in this room."
                if seen[ref]["place"] != o["place"]:
                    return f"{oid} is at {o['place']} but its ref {ref} is at {seen[ref]['place']}."
                if o["relation"] == "in":
                    if seen[ref]["carrier"] == "none":
                        return f"{oid} is in {ref}, but {ref} has carrier none; it cannot hold things."
                    if seen[ref]["relation"] == "in" and seen[ref]["ref"]:
                        return f"{ref} is itself inside something; {oid} cannot go inside it."
                    if o["carrier"] != "none":
                        return f"{oid} is a carrier; it cannot start inside {ref}."
            seen[oid] = o
        return ""
    return check


def check_situations(spec: dict) -> str:
    ids = [s["id"] for s in spec["situations"]]
    if len(set(ids)) != len(ids):
        return "Situation ids must be unique."
    if "sick" not in ids:
        return "There must be a situation with id 'sick'."
    return ""


# ---------------------------------------------------------------- building
def start_position(o: dict, layout: Layout) -> dict:
    kind = layout.places[o["place"]].kind
    rel, ref = o["relation"], o["ref"] or None
    if ref and rel == "in":
        return {"at": "inside", "carrier": ref}
    if ref and rel == "on":
        rel = "on_top_of"
    if not ref and rel in ("on", "in", "on_top_of", "next_to"):
        rel = "in" if kind == CONTAINER else "on"
    return at_place(o["place"], rel, ref)


def residents_text(residents: list[dict]) -> str:
    out = []
    for r in residents:
        out.append(f"{r['id']} ({r['name']}, {r['age']}, {r['job']}). {r['personality']}\n"
                   + "  Habits with things:\n" + "\n".join(f"  - {h}" for h in r["object_habits"]))
    return "\n".join(out)


def room_targets(layout: Layout) -> dict:
    total = len(layout.places)
    return {room: max(4, round(OBJECTS_TARGET * len(ids) / total))
            for room, ids in layout.rooms.items()}


def create(caller: Caller, seed: int, out: pathlib.Path, effort_note: str = "") -> dict:
    """Runs the creation calls and writes household.json. Returns the spec."""
    rng = random.Random(seed)
    home = rng.choice(prompts.HOMES)

    lay = caller.call("create/layout", prompts.CREATE_SYSTEM,
                      prompts.LAYOUT_USER.format(home=home, lo=PLACES_LO + 20, hi=PLACES_HI - 30),
                      layout_schema(), check_layout, max_tokens=60000)
    layout = Layout.from_generated(lay)
    rooms = list(layout.rooms)

    res = caller.call("create/residents", prompts.CREATE_SYSTEM,
                      prompts.RESIDENTS_USER.format(layout=layout.describe()),
                      residents_schema(layout.place_ids, rooms), check_residents(layout),
                      max_tokens=40000)
    residents = res["residents"]
    rids = [r["id"] for r in residents]

    objects: list[dict] = []
    targets = room_targets(layout)
    for room in rooms:
        objects += _room_objects(caller, layout, residents, rids, room, targets[room], objects, "")
    passes = 0
    while len(objects) < OBJECTS_LO and passes < 3:
        passes += 1
        counts = collections.Counter(layout.room_of(o["place"]) for o in objects)
        room = min(rooms, key=lambda r: counts[r] / len(layout.rooms[r]))
        need = OBJECTS_LO - len(objects) + 10
        objects += _room_objects(caller, layout, residents, rids, room, need, objects,
                                 f"/more{passes}")

    sit = caller.call("create/situations", prompts.CREATE_SYSTEM,
                      prompts.SITUATIONS_USER.format(residents=residents_text(residents)),
                      situations_schema(rids), check_situations, max_tokens=40000)

    spec = {"seed": seed, "home": home, "layout_thinking": lay["thinking"],
            "layout": layout.to_json(), "residents": residents, "objects": objects,
            "situations": sit["situations"], "small_disturbances": sit["small_disturbances"]}
    out.mkdir(parents=True, exist_ok=True)
    (out / "household.json").write_text(json.dumps(spec, indent=1))
    (out / "household_summary.md").write_text(summarize(spec))
    return spec


def _room_objects(caller, layout, residents, rids, room, target, so_far, suffix) -> list[dict]:
    room_places = layout.places_in(room)
    taken = {o["id"] for o in so_far}
    spots = "\n".join(f"  {p} ({layout.places[p].name}"
                      f"{', closed' if layout.places[p].kind == CONTAINER else ''}"
                      f"{', out of sight' if layout.places[p].hidden else ''})" for p in room_places)
    if so_far:
        by_type = collections.defaultdict(list)
        for o in so_far:
            by_type[o["type"]].append(o["id"])
        taken_text = ("\nAlready in other rooms (do not reuse these ids; add more instances "
                      "of a type where the home would have them):\n"
                      + "\n".join(f"  {t}: {', '.join(ids)}" for t, ids in sorted(by_type.items())))
    else:
        taken_text = ""
    lo, hi = max(3, round(target * 0.75)), round(target * 1.3) + 2
    ans = caller.call(f"create/objects/{room}{suffix}", prompts.CREATE_SYSTEM,
                      prompts.OBJECTS_USER.format(layout=layout.describe(),
                                                  residents=residents_text(residents),
                                                  room=room, spots=spots, lo=lo, hi=hi,
                                                  taken=taken_text),
                      room_objects_schema(room_places, rids, lo, hi),
                      check_room_objects(set(room_places), taken, layout), max_tokens=40000)
    out = []
    for o in ans["objects"]:
        o = dict(o)
        o["type"] = o["type"].strip().lower()
        o["owner"] = None if o["owner"] == "none" else o["owner"]
        o["start"] = start_position(o, layout)
        out.append(o)
    return out


def summarize(spec: dict) -> str:
    layout = Layout.from_json(spec["layout"])
    types = collections.Counter(o["type"] for o in spec["objects"])
    hidden = sum(1 for p in layout.places.values() if not p.seen_from_room)
    rooms = collections.Counter(layout.room_of(o["start"].get("place") or "") for o in spec["objects"]
                                if o["start"]["at"] == "place")
    lines = [f"# Household (seed {spec['seed']}): {spec['home']}", "",
             f"- places: {len(layout.places)} ({hidden} closed or out of sight) in {len(layout.rooms)} rooms",
             f"- objects: {len(spec['objects'])} of {len(types)} types; "
             f"{sum(1 for c in types.values() if c >= 2)} types have 2+ instances",
             f"- owned: {sum(1 for o in spec['objects'] if o['owner'])}; "
             f"carriers: {sum(1 for o in spec['objects'] if o['carrier'] != 'none')}; "
             f"starting inside a carrier: {sum(1 for o in spec['objects'] if o['start']['at'] == 'inside')}; "
             f"with a relation to another object: {sum(1 for o in spec['objects'] if o['start'].get('ref'))}",
             f"- residents: " + ", ".join(f"{r['id']} ({r['age']}, {r['job']})" for r in spec["residents"]),
             f"- situations: {len(spec['situations'])}; disturbances: {len(spec['small_disturbances'])}",
             "", "## Objects per room", ""]
    lines += [f"- {room}: {rooms[room]} objects, {len(ids)} places" for room, ids in layout.rooms.items()]
    lines += ["", "## Types with several instances", ""]
    lines += [f"- {t}: {c}" for t, c in types.most_common() if c >= 2]
    return "\n".join(lines) + "\n"
