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
from lived_home.schemas import (fixtures_schema, layout_schema, residents_schema, room_objects_schema,
                                situations_schema)
from lived_home.world import at_place

ID = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
PLACES_LO, PLACES_HI = 100, 200
OBJECTS_LO, OBJECTS_HI, OBJECTS_TARGET = 150, 300, 220
PERSONAL_LO, PERSONAL_HI = 18, 32
FIXTURES_LO, FIXTURES_HI = 4, 24


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


STOVE_WORDS = ("stove", "stovetop", "range", "hob", "cooktop", "burner", "burners")


def check_fixtures(lay: dict, lo: int, hi: int):
    """The additions must be new, well-formed spots, and afterwards the kitchen
    must have somewhere to cook and somewhere to wash up."""
    existing = {s["id"] for r in lay["rooms"] for f in r["furniture"] for s in f["spots"]}

    def check(ans: dict) -> str:
        new = [s for a in ans["additions"] for s in a["spots"]]
        problems = []
        ids = [s["id"] for s in new]
        clash = sorted({i for i in ids if i in existing or ids.count(i) > 1})
        if clash:
            problems.append(f"spot ids already used: {clash[:10]}")
        bad = [i for i in ids if not ID.match(i)]
        if bad:
            problems.append(f"spot ids must be lowercase with underscores: {bad[:10]}")
        if not lo <= len(new) <= hi:
            problems.append(f"{len(new)} spots added; add {lo} to {hi}")
        for room in (r["id"] for r in lay["rooms"] if "kitchen" in r["id"]):
            words = set()
            for r in lay["rooms"]:
                if r["id"] == room:
                    for f in r["furniture"]:
                        for s in f["spots"]:
                            words |= set(slug(s["id"] + " " + s["name"]).split("_"))
            for a in ans["additions"]:
                if a["room"] == room:
                    for s in a["spots"]:
                        words |= set(slug(s["id"] + " " + s["name"] + " " + a["fixture"]).split("_"))
            if not words & set(STOVE_WORDS):
                problems.append(f"the {room} still has no spot on the stove")
            if "sink" not in words:
                problems.append(f"the {room} still has no spot in the sink")
        return "" if not problems else f"{len(problems)} problems: " + "; ".join(problems) + "."
    return check


def add_fixtures(lay: dict, ans: dict) -> None:
    rooms = {r["id"]: r for r in lay["rooms"]}
    for a in ans["additions"]:
        rooms[a["room"]]["furniture"].append({"name": a["fixture"], "spots": a["spots"], "added_as_fixture": True})


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


def check_room_objects(room_places: set):
    """The rules the model must decide: numbering, references, carriers.
    Ids are not the model's job (see compose_ids)."""
    def check(ans: dict) -> str:
        objs = ans["objects"]
        by_n = {o["n"]: o for o in objs}
        problems = []
        if len(by_n) != len(objs):
            problems.append("each thing needs its own n")
        for o in objs:
            if not o["type"].strip():
                problems.append(f"thing {o['n']} has no type")
            if o["place"] not in room_places:
                problems.append(f"thing {o['n']} is at {o['place']}, which is not a spot in this room")
            ref = o["ref"]
            if not ref:
                continue
            target = by_n.get(ref)
            if target is None or ref == o["n"]:
                problems.append(f"thing {o['n']} has ref {ref}, which is not another thing in your list")
                continue
            chain, cur = {o["n"]}, ref
            while cur and cur in by_n and cur not in chain:
                chain.add(cur)
                cur = by_n[cur]["ref"]
            if cur in chain:
                problems.append(f"things {o['n']} and {ref} refer to each other in a loop")
            elif o["relation"] == "in":
                if target["carrier"] == "none":
                    problems.append(f"thing {o['n']} is in thing {ref}, which has carrier none and cannot hold things")
                elif target["relation"] == "in" and target["ref"] and target["carrier"] != "pockets":
                    problems.append(f"thing {ref} is itself inside something; thing {o['n']} cannot go inside it")
                if o["carrier"] not in ("none", "pockets"):
                    problems.append(f"thing {o['n']} is a bag or basket and cannot start inside thing {ref}")
        if not problems:
            return ""
        return f"{len(problems)} problems: " + "; ".join(problems) + "."
    return check


def compose_ids(objects: list, taken: dict, rids) -> list:
    """id = type + looks, in place; resident names are dropped from the looks.
    References (ref = another thing's n) become ids, and a thing placed
    relative to another takes that thing's spot.

    taken: id -> {owner, place, type, looks} for things already in the home. A
    thing is the same thing described again, and is dropped and returned, when
    its id matches one already placed and either is owned, or when a thing of
    the same type already sits at the same spot sharing a word of its looks.
    Otherwise a clash takes the next attribute that tells it apart (material,
    condition, pattern, color), then a number."""
    by_num = {o["n"]: o for o in objects}
    for o in objects:      # spot from the thing referred to (both were asked for; they can disagree)
        root, seen = o, set()
        while root["ref"] and root["ref"] in by_num and root["n"] not in seen:
            seen.add(root["n"])
            root = by_num[root["ref"]]
        if root is not o and root["place"] != o["place"]:
            o["place_as_written"] = o["place"]
            o["place"] = root["place"]
    used = dict(taken)
    by_n, dropped = {}, []
    for o in objects:
        o["type"] = o["type"].strip().lower()
        kind = slug(o["type"])
        look = [w for w in slug(o["looks"]).split("_") if w and w not in rids and w not in kind.split("_")]
        oid = "_".join([kind] + look) if look else f"{kind}_{slug(o['color'])}"
        owner = None if o.get("owner") in (None, "none") else o["owner"]
        same = taken.get(oid)
        twin = next((tid for tid, x in taken.items() if x["type"] == o["type"]
                     and x["place"] == o["place"] and set(look) & x["looks"]), None)
        if (same and (same["owner"] or owner)) or twin:
            o["id"], o["same_as"] = oid, (oid if same else twin)
            dropped.append(o)
            by_n[o["n"]] = None
            continue
        for extra in (o["material"], o["condition"], o["pattern"], o["color"]):
            if oid not in used:
                break
            words = [w for w in slug(extra).split("_") if w and w not in oid.split("_")]
            if words:
                oid = "_".join([oid] + words)
        base, k = oid, 2
        while oid in used:
            oid, k = f"{base}_{k}", k + 1
        used[oid] = {"owner": owner, "place": o["place"], "type": o["type"], "looks": set(look)}
        o["id"], o["look_words"] = oid, look
        by_n[o["n"]] = oid
    for o in objects:
        o["ref"] = (by_n.get(o["ref"]) or "") if o["ref"] else ""
    for o in dropped:
        objects.remove(o)
    return dropped


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


ESSENTIALS = {"phone": ("phone",), "keys": ("key", "keys"),
              "wallet or purse": ("wallet", "purse", "cardholder", "card_holder")}


def missing_essentials(objects: list, rid: str) -> list[str]:
    """Everyday things a person always has, checked by the words of their types."""
    mine = [slug(o["type"]).split("_") for o in objects if o["owner"] == rid]
    out = []
    for name, words in ESSENTIALS.items():
        if name == "phone":
            ok = any(w[-1] == "phone" for w in mine)
        else:
            ok = any(set(w) & set(words) or "_".join(w) in words for w in mine)
        if not ok:
            out.append(name)
    return out


def _personal(caller, layout, home, residents, r, so_far, dropped) -> list[dict]:
    rid, name = r["id"], r["name"].split()[0]
    others = [o for o in so_far if o["owner"] and o["owner"] != rid]
    others_text = ("\nAlready listed for the others (do not list these for " + name + "): "
                   + ", ".join(o["id"] for o in others) + ".\n") if others else ""
    taken = {o["id"]: {"owner": o["owner"], "place": o["place"], "type": o["type"],
                       "looks": set(o.get("look_words") or [])} for o in so_far}
    ans = caller.call(f"create/personal/{rid}", prompts.CREATE_SYSTEM,
                      prompts.PERSONAL_USER.format(
                          home=home, layout=layout.describe(), residents=residents_text(residents),
                          name=name, rid=rid, routine=routines_text([r]), others=others_text,
                          lo=PERSONAL_LO, hi=PERSONAL_HI, fields=prompts.FIELDS),
                      room_objects_schema(layout.place_ids, [rid], PERSONAL_LO, PERSONAL_HI,
                                          owner_required=True),
                      check_room_objects(set(layout.place_ids)), max_tokens=40000)
    dropped += compose_ids(ans["objects"], taken, [x["id"] for x in residents])
    out = [_finish(o, layout) for o in ans["objects"]]
    missing = missing_essentials(out, rid)
    if missing:
        for o in out:
            taken[o["id"]] = {"owner": o["owner"], "place": o["place"], "type": o["type"],
                              "looks": set(o.get("look_words") or [])}
        add = caller.call(f"create/personal/{rid}/essentials", prompts.CREATE_SYSTEM,
                          prompts.ESSENTIALS_USER.format(
                              layout=layout.describe(), name=name, rid=rid,
                              about=residents_text([r]), missing=" and ".join(missing),
                              fields=prompts.FIELDS),
                          room_objects_schema(layout.place_ids, [rid], len(missing), len(missing) + 1,
                                              owner_required=True),
                          check_room_objects(set(layout.place_ids)), max_tokens=20000)
        dropped += compose_ids(add["objects"], taken, [x["id"] for x in residents])
        extra = [_finish(o, layout) for o in add["objects"]]
        for o in extra:
            o["added_as_essential"] = True
        out += extra
    return out


def routines_text(residents: list[dict]) -> str:
    out = []
    for r in residents:
        out.append(f"{r['id']}:")
        out += [f"  {', '.join(x['days'])} {x['start']}-{x['end']} {x['activity']} ({x['room']})"
                for x in r["weekly_routine"]]
    return "\n".join(out)


def room_targets(layout: Layout, already: int = 0) -> dict:
    total = len(layout.places)
    left = max(OBJECTS_TARGET - already, 40)
    return {room: max(3, round(left * len(ids) / total))
            for room, ids in layout.rooms.items()}


def _finish(o: dict, layout: Layout) -> dict:
    o = dict(o)
    o["owner"] = None if o["owner"] == "none" else o["owner"]
    o["start"] = start_position(o, layout)
    return o


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
                      prompts.RESIDENTS_USER.format(home=lay["home"], layout=layout.describe()),
                      residents_schema(layout.place_ids, rooms), check_residents(layout),
                      max_tokens=40000)
    residents = res["residents"]
    rids = [r["id"] for r in residents]

    # appliances and fixtures (stovetop, sink, oven) that the layout call treated as
    # not furniture; added after the residents so the spots they sleep at are unchanged
    fix = caller.call("create/fixtures", prompts.CREATE_SYSTEM,
                      prompts.FIXTURES_USER.format(home=lay["home"], layout=layout.describe(),
                                                   lo=FIXTURES_LO, hi=FIXTURES_HI),
                      fixtures_schema(rooms, FIXTURES_LO, FIXTURES_HI),
                      check_fixtures(lay, FIXTURES_LO, FIXTURES_HI), max_tokens=30000)
    add_fixtures(lay, fix)
    layout = Layout.from_generated(lay)

    objects, dropped = [], []
    for r in residents:
        objects += _personal(caller, layout, lay["home"], residents, r, objects, dropped)
    targets = room_targets(layout, len(objects))
    for room in rooms:
        objects += _room_objects(caller, layout, residents, rids, room, targets[room], objects, "",
                                 dropped)
    passes = 0
    while len(objects) < OBJECTS_LO and passes < 3:
        passes += 1
        counts = collections.Counter(layout.room_of(o["place"]) for o in objects)
        room = min(rooms, key=lambda r: counts[r] / len(layout.rooms[r]))
        need = OBJECTS_LO - len(objects) + 10
        objects += _room_objects(caller, layout, residents, rids, room, need, objects,
                                 f"/more{passes}", dropped)

    sit = caller.call("create/situations", prompts.CREATE_SYSTEM,
                      prompts.SITUATIONS_USER.format(residents=residents_text(residents)),
                      situations_schema(rids), check_situations, max_tokens=40000)

    spec = {"seed": seed, "home": home, "layout_thinking": lay["thinking"],
            "layout": layout.to_json(), "residents": residents, "objects": objects,
            "situations": sit["situations"], "small_disturbances": sit["small_disturbances"],
            "dropped_duplicates": [{"id": o["id"], "owner": o["owner"], "place": o["place"]}
                                   for o in dropped]}
    out.mkdir(parents=True, exist_ok=True)
    (out / "household.json").write_text(json.dumps(spec, indent=1))
    (out / "household_summary.md").write_text(summarize(spec))
    return spec


def _room_objects(caller, layout, residents, rids, room, target, so_far, suffix,
                  dropped: list) -> list[dict]:
    room_places = layout.places_in(room)
    taken = {o["id"]: {"owner": o["owner"], "place": o["place"], "type": o["type"],
                       "looks": set(o.get("look_words") or [])} for o in so_far}
    spots = "\n".join(f"  {p} ({layout.places[p].name}"
                      f"{', closed' if layout.places[p].kind == CONTAINER else ''}"
                      f"{', out of sight' if layout.places[p].hidden else ''})" for p in room_places)
    if so_far:
        by_type = collections.defaultdict(list)
        for o in so_far:
            by_type[o["type"]].append(o["id"])
        here = [f"{o['id']} ({o['start'].get('place') or 'inside ' + o['start']['carrier']})"
                for o in so_far if layout.room_of(_base_place(o, so_far)) == room]
        taken_text = (("\nAlready in this room (do not list these again): " + ", ".join(here) + ".\n"
                       if here else "")
                      + "\nAlready placed in the home, and staying there (type: names). Do not "
                      "add a second one of something a person has only one of (their phone, "
                      "wallet, house keys, work laptop, everyday glasses); do add more instances "
                      "of types a home has several of (mugs, chargers, towels, books), looking "
                      "different from these:\n"
                      + "\n".join(f"  {t}: {', '.join(ids)}" for t, ids in sorted(by_type.items())))
    else:
        taken_text = ""
    lo, hi = max(3, round(target * 0.75)), round(target * 1.3) + 2
    ans = caller.call(f"create/objects/{room}{suffix}", prompts.CREATE_SYSTEM,
                      prompts.OBJECTS_USER.format(layout=layout.describe(),
                                                  residents=residents_text(residents),
                                                  room=room, spots=spots, lo=lo, hi=hi,
                                                  fields=prompts.FIELDS, taken=taken_text),
                      room_objects_schema(room_places, rids, lo, hi),
                      check_room_objects(set(room_places)), max_tokens=40000)
    dropped += compose_ids(ans["objects"], taken, rids)
    return [_finish(o, layout) for o in ans["objects"]]


def _base_place(o: dict, objects: list) -> str:
    if o["start"]["at"] == "place":
        return o["start"]["place"]
    carrier = next(x for x in objects if x["id"] == o["start"]["carrier"])
    return carrier["start"]["place"]


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
    owned = collections.Counter((o["owner"], o["type"]) for o in spec["objects"] if o["owner"])
    lines += ["", "## One person owning several of a type (check none is a duplicate of a one-off thing)", ""]
    lines += [f"- {owner}: {t} x{c}: " + ", ".join(o["id"] for o in spec["objects"]
                                                  if o["owner"] == owner and o["type"] == t)
              for (owner, t), c in sorted(owned.items()) if c > 1] or ["- none"]
    lines += ["", "## Types with several instances", ""]
    lines += [f"- {t}: {c}" for t, c in types.most_common() if c >= 2]
    return "\n".join(lines) + "\n"
