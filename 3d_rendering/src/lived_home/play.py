"""A search task a person (or a method) can play, built from a finished run.

The robot knows the home's layout and who owns what. Everything else it learns by
looking:
- Patrols: at fixed times each day it walks through a few rooms (not all) and
  notes what it can see on each piece of furniture there: things on surfaces and
  in open basins, not inside drawers or cupboards, not under things. It sees the
  residents who are in those rooms and what they hold.
- Searches: each question asks where a thing is, at a time between patrols.
  The player looks at pieces of furniture one at a time (each look walks the
  robot there and shows what is visible on it right now) until the thing shows
  up, or answers without seeing it: put away inside a closed spot, someone has
  it, out of the house, or cannot tell. What a look shows is kept as evidence
  for later questions.

Things are named by how they look ("the white chipped coffee mug"); some
questions name them by owner ("Julian's travel mug"). A few questions are
deliberately ambiguous (an owner with two of a kind) to test how people read
them; the answer key accepts any thing that fits.

Usage: python -m lived_home.play <run folder> [--questions 30] [--seed 0] [--out folder]
writes <run>/play/play_data.json (everything the page needs) and index.html.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import random
import re

PATROL_TIMES = ["0800", "1200", "1600", "2000"]
QUESTION_TIMES = ["1000", "1400", "1800", "2200"]
ROOMS_SHARE = 1 / 3        # each patrol visits about a third of the rooms (at least 3)
SETTLE_DAYS = 3
MAX_LOOKS = 8
CARRIED = ("held_by", "worn_by", "in_pocket_of")
REL_WORDS = {"on_top": "on top of", "next_to": "next to", "inside": "inside", "under": "under"}


def hhmm(t: str) -> str:
    return f"{t[:2]}:{t[2:]}"


def load(run: pathlib.Path):
    spec = json.loads((run / "household.json").read_text())
    states = {}
    for d in sorted(run.glob("day_*")):
        day = int(d.name.split("_")[1])
        for f in d.glob("positions_*.json"):
            states[(day, f.stem.split("_")[1])] = json.loads(f.read_text())
    if not states:
        raise SystemExit(f"{run} has no positions_HHMM.json snapshots (runs from before 2026-10-08)")
    return spec, states


def phrase(o: dict) -> str:
    """How a thing is named by its look: 'white chipped coffee mug'."""
    looks = (o.get("looks") or "").strip().lower()
    t = o["type"].lower()
    counts = {"one", "two", "three", "four", "five", "six", "pair", "of", "single", "set"}
    words = [w for w in looks.split() if w not in t.split() and w not in counts and not w.isdigit()]
    return " ".join(words + [t]).strip()


def asked_name(oid: str, objects: dict, names: dict, first_names: dict) -> str:
    """How a question names a thing. When another thing looks the same, say whose
    it is, or failing that use its full description (from its id)."""
    twins = [x for x in objects if x != oid and names[x] == names[oid]]
    if not twins:
        return f"the {names[oid]}"
    owner = objects[oid].get("owner")
    if owner in first_names and all(objects[x].get("owner") != owner for x in twins):
        return f"{first_names[owner]}'s {names[oid]}"
    type_words = objects[oid]["type"].lower().split()
    extra = [w for w in oid.split("_") if w not in type_words]
    return "the " + " ".join(extra + type_words)


def is_plural(type_: str) -> bool:
    last = type_.lower().split()[-1]
    return last.endswith("s") and not last.endswith(("ss", "us", "os", "is", "as"))


def where_is(name: str, type_: str) -> str:
    return f"Where {'are' if is_plural(type_) else 'is'} {name}?"


def furniture_key(place: dict) -> str:
    return f"{place['room']}|{place['furniture']}"


def build_layout(spec: dict, states: dict) -> dict:
    """Rooms (with outlines when the home is a 3D scene), furniture and spots."""
    any_state = next(iter(states.values()))
    places = any_state["places"]
    furniture = {}
    for pid, p in places.items():
        k = furniture_key(p)
        g = p.get("geometry") or {}
        f = furniture.setdefault(k, {"key": k, "room": p["room"], "name": p["furniture"],
                                     "spots": [], "xs": [], "zs": []})
        f["spots"].append({"id": pid, "name": p["name"], "kind": p["kind"],
                           "descriptions": next((q.get("descriptions") for q in spec["layout"]["places"]
                                                 if q["id"] == pid), []),
                           "height": g.get("height")})
        if g.get("center"):
            f["xs"].append(g["center"][0])
            f["zs"].append(g["center"][2])
    for f in furniture.values():
        f["x"] = sum(f["xs"]) / len(f["xs"]) if f["xs"] else None
        f["z"] = sum(f["zs"]) / len(f["zs"]) if f["zs"] else None
        del f["xs"], f["zs"]
    rooms = sorted({p["room"] for p in places.values()})
    outlines = {}
    scene = spec.get("scene")
    if scene:
        try:
            from lived_home.hssd_layout import _rooms
            outlines = {r["id"]: r["polygon"] for r in _rooms(scene)}
        except Exception:
            outlines = {}
    return {"scene": scene, "rooms": [{"id": r, "polygon": outlines.get(r)} for r in rooms],
            "furniture": sorted(furniture.values(), key=lambda f: f["key"]),
            "entry": spec["layout"]["entry"]}


def visible_at(state: dict, names: dict, first: dict | None = None) -> tuple[dict, dict]:
    """What a look at each piece of furniture would show at this moment, and who is
    in each room holding what. Things are given by their look, never by id.
    What a resident holds while standing at a piece of furniture (a notebook at the
    desk she writes at) shows in a look at that furniture too: a camera pointed
    there sees it in her hands."""
    places = state["places"]
    first = first or {}
    shown = collections.defaultdict(list)
    for oid, o in state["objects"].items():
        if o["relation"] in CARRIED or o["hidden"] or not o.get("place") or o["place"] not in places:
            continue
        p = places[o["place"]]
        rel = o["relation"]
        if o.get("reference_kind") == "object" and o.get("reference") in state["objects"]:
            where = f"{REL_WORDS.get(rel, rel)} the {names[o['reference']]}"
        elif rel == "inside":
            where = "in it"
        else:
            where = ""
        shown[furniture_key(p)].append({"spot": o["place"], "thing": names[oid], "oid": oid,
                                        "where": where})
    people = collections.defaultdict(list)
    for rid, w in state["people"].items():
        if w.get("room") and w["room"] != "out_of_house":
            held_ids = [oid for oid, o in state["objects"].items()
                        if o["relation"] == "held_by" and o.get("reference") == rid]
            people[w["room"]].append({"who": rid, "holding": [names[oid] for oid in held_ids]})
            if w.get("place") in places:
                for oid in held_ids:
                    shown[furniture_key(places[w["place"]])].append(
                        {"spot": w["place"], "thing": names[oid], "oid": oid,
                         "where": f"in {first.get(rid, rid.title())}'s hands"})
    return shown, people


def patrols(states: dict, layout: dict, names: dict, rng: random.Random, first: dict | None = None) -> list:
    rooms = [r["id"] for r in layout["rooms"]]
    per = max(3, math.ceil(len(rooms) * ROOMS_SHARE))
    days = sorted({d for d, _ in states})
    out, cycle = [], []
    for day in days:
        for t in PATROL_TIMES:
            if (day, t) not in states:
                continue
            if len(cycle) < per:
                more = list(rooms)
                rng.shuffle(more)
                cycle += more
            visit, cycle = cycle[:per], cycle[per:]
            visit = list(dict.fromkeys(visit))
            shown, people = visible_at(states[(day, t)], names, first)
            seen = []
            for f in layout["furniture"]:
                if f["room"] in visit:
                    seen.append({"furniture": f["key"],
                                 "things": [{k: v for k, v in s.items() if k != "oid"} for s in shown.get(f["key"], [])],
                                 "oids": [s["oid"] for s in shown.get(f["key"], [])]})
            out.append({"day": day, "time": hhmm(t), "rooms": visit, "seen": seen,
                        "people": {r: people.get(r, []) for r in visit}})
    return out


def last_patrol_sighting(patrol_log: list, oid: str, before: tuple) -> str | None:
    last = None
    for p in patrol_log:
        if (p["day"], p["time"]) >= before:
            break
        for s in p["seen"]:
            if oid in s["oids"]:
                last = s["furniture"]
    return last


def answer_key(state: dict, oid: str) -> dict:
    o = state["objects"][oid]
    outer, seen = o, set()
    while outer["relation"] == "inside" and outer.get("reference_kind") == "object" \
            and outer["reference"] in state["objects"] and outer["reference"] not in seen:
        seen.add(outer["reference"])
        outer = state["objects"][outer["reference"]]
    if outer["relation"] in CARRIED and o["relation"] not in CARRIED:
        o = dict(o, relation=outer["relation"], reference=outer["reference"], inside=True)
    if o["relation"] in CARRIED:
        who = o["reference"]
        out = state["people"].get(who, {}).get("room") in (None, "out_of_house")
        return {"kind": "out of the house" if out else "someone has it", "who": who,
                "how": o["relation"], "room": o.get("room"), "spot": o.get("place")}
    p = state["places"][o["place"]]
    kind = "put away" if o["hidden"] else "visible"
    return {"kind": kind, "spot": o["place"], "furniture": furniture_key(p), "room": o["room"],
            "relation": o["relation"], "reference": o.get("reference"),
            "reference_kind": o.get("reference_kind")}


def spot_words(furniture: str, name: str) -> str:
    """A spot named with its furniture, without repeats: 'glass desk' + 'desk top'
    is 'glass desk top'; 'floor' + 'floor' is 'floor'."""
    if furniture.lower() in name.lower():
        return name
    fw, nw = furniture.split(), name.split()
    if fw and nw and fw[-1].lower() == nw[0].lower():
        return " ".join(fw + nw[1:])
    return f"{furniture} {name}"


MOVE_VERBS = {"pick_up": "picked up", "put_down": "put down", "pocket": "pocketed",
              "wear": "put on", "give": "handed over"}


def load_moves(run: pathlib.Path) -> tuple[list, dict]:
    """Every action that moved a thing (events.jsonl), and each day's plans, to say
    after an answer how the thing got where it was."""
    events = []
    path = run / "events.jsonl"
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                e = json.loads(line)
                if e.get("verb") in MOVE_VERBS and e.get("object"):
                    events.append(e)
    plans = {}
    for d in run.glob("day_*"):
        f = d / "plans.json"
        if f.exists():
            plans[int(d.name.split("_")[1])] = json.loads(f.read_text())
    return events, plans


def how_it_got_there(oids: list, state: dict, slot: tuple, events: list, plans: dict,
                     names: dict, first: dict, places: dict, hours: int = 24) -> list:
    """The moves of the things asked for in the hours before the question, in plain
    words, with the mover's own reason and the activity they were in. A bag the
    thing was inside at the question's time is followed too, but only from when the
    thing went into it. Moves at the question's minute come after the snapshot and
    are left out."""
    day, t = slot
    end = day * 1440 + int(t[:2]) * 60 + int(t[2:])
    start = end - hours * 60
    at = lambda e: e["day"] * 1440 + e["minute"]
    track = {oid: (None, start) for oid in oids}       # thing -> (the thing asked for, followed since)
    for oid in oids:
        o, inner, seen = state["objects"][oid], oid, set()
        while o["relation"] == "inside" and o.get("reference_kind") == "object" \
                and o["reference"] in state["objects"] and o["reference"] not in seen:
            bag = o["reference"]
            seen.add(bag)
            went_in = max((at(e) for e in events if e["object"] == inner and at(e) < end
                           and (e.get("to_pos") or {}).get("carrier") == bag), default=start)
            since = max(went_in, track[inner][1])
            if bag not in track:
                track[bag] = (oid, since)
            inner, o = bag, state["objects"][bag]
    ids = sorted(list(names) + list(places), key=len, reverse=True)

    def words(text: str) -> str:
        for i in ids:
            if i in text:
                if i in names:
                    text = text.replace(i, f"the {names[i]}")
                else:
                    pl = places[i]
                    text = text.replace(i, f"the {spot_words(pl['furniture'], pl['name'])} "
                                           f"({pl['room'].replace('_', ' ')})")
        for rid, nm in first.items():
            text = re.sub(rf"\b{re.escape(rid)}'s\b", f"{nm}'s", text)
            text = re.sub(rf"\b{re.escape(rid)}\b", nm, text)
        return text.replace("on top ", "on top of ").replace("_", " ")

    out = []
    for e in events:
        if e["object"] not in track:
            continue
        asked, since = track[e["object"]]
        if not (since <= at(e) < end):
            continue
        acts = (plans.get(e["day"]) or {}).get(e["resident"]) or []
        doing = next((a["activity"] for a in acts if a["start_min"] <= e["minute"] < a["end_min"]), "")
        what = MOVE_VERBS[e["verb"]]
        if e["verb"] == "pick_up" and (e.get("from") or "").startswith("worn by"):
            what, where = "took off", ""
        elif e["verb"] == "pick_up":
            where = f"from {words(e.get('from') or '')}"
        elif e["verb"] in ("pocket", "wear"):
            where = f"(it was {words(e.get('from') or '')})"
        else:
            where = words(e.get("to") or "")
        thing = f"the {names[e['object']]}" + (f" (with the {names[asked]} inside)" if asked else "")
        out.append({"day": e["day"], "time": e["time"], "who": e["resident"],
                    "text": f"{what} {thing} {where}".strip(),
                    "why": (e.get("why") or "").strip(), "doing": doing})
    return out[-10:]


def questions(spec, states, patrol_log, layout, names, n, rng, settle=SETTLE_DAYS,
              history=None) -> list:
    objects = {o["id"]: o for o in spec["objects"]}
    days = sorted({d for d, _ in states})
    first = states[min(states)]
    moves = collections.Counter()
    keys = sorted(states)
    for a, b in zip(keys, keys[1:]):
        for oid in objects:
            if states[a]["objects"][oid].get("place") != states[b]["objects"][oid].get("place"):
                moves[oid] += 1
    movers = [oid for oid in objects if moves[oid] >= 2]
    owners = collections.defaultdict(lambda: collections.defaultdict(list))
    for oid, o in objects.items():
        if o.get("owner") and o["owner"] in {r["id"] for r in spec["residents"]}:
            owners[o["owner"]][o["type"]].append(oid)
    first_names = {r["id"]: r["name"].split()[0] for r in spec["residents"]}
    slots = [(d, t) for d in days if d > settle for t in QUESTION_TIMES if (d, t) in states]
    want = {"moved since last seen": 0.4, "seen where it is": 0.08, "put away": 0.15,
            "someone has it": 0.12, "never seen": 0.1, "by owner": 0.1, "ambiguous by owner": 0.05}
    chosen = sorted(rng.sample(slots, min(n, len(slots))))
    plan = [k for k, w in want.items() for _ in range(max(1, round(w * len(chosen))))]
    rng.shuffle(plan)
    out, recent, used_owner = [], collections.deque(maxlen=6), set()
    for i, slot in enumerate(chosen):
        state = states[slot]
        before = (slot[0], hhmm(slot[1]))
        def cat(oid):
            key = answer_key(state, oid)
            if key["kind"] in ("someone has it", "out of the house"):
                worn_clothes = key["how"] == "worn_by" and objects[oid]["carrier"] in ("none", "pockets")
                return None if worn_clothes else "someone has it"
            if key["kind"] == "put away":
                # only fair if the patrols have seen it somewhere at least once
                return "put away" if last_patrol_sighting(patrol_log, oid, before) else None
            last = last_patrol_sighting(patrol_log, oid, before)
            if last is None:
                return "never seen"
            return "seen where it is" if last == key["furniture"] else "moved since last seen"
        pool = collections.defaultdict(list)
        for oid in movers:
            if oid in recent or not asked_name(oid, objects, names, first_names).startswith(("the ", *[f"{v}'s" for v in first_names.values()])):
                continue
            if asked_name(oid, objects, names, first_names) != f"the {names[oid]}" and \
                    not any(asked_name(oid, objects, names, first_names).startswith(f"{v}'s") for v in first_names.values()):
                continue                          # look-alike nobody owns: no way to tell which
            c = cat(oid)
            if c:
                pool[c].append(oid)
        kind = plan[i % len(plan)]
        text, accept, probe = None, None, None
        if kind in ("by owner", "ambiguous by owner"):
            opts = []
            for who, types in owners.items():
                for t, ids in types.items():
                    ids_m = [x for x in ids if x in movers and cat(x)]
                    if not ids_m:
                        continue
                    if (kind == "ambiguous by owner") == (len(ids) > 1) and (who, t) not in used_owner:
                        opts.append((who, t, ids))
            if opts:
                who, t, ids = rng.choice(opts)
                used_owner.add((who, t))
                text = where_is(f"{first_names[who]}'s {t}", t)
                accept, probe = ids, (kind == "ambiguous by owner")
        if text is None:
            k2 = kind if pool.get(kind) else max(pool, key=lambda c: len(pool[c]))
            oid = rng.choice(pool[k2])
            text = where_is(asked_name(oid, objects, names, first_names), objects[oid]["type"])
            accept, probe, kind = [oid], False, k2
        recent.extend(accept)
        keys_ = {oid: answer_key(state, oid) for oid in accept}
        shown, people = visible_at(state, names, first_names)
        story = how_it_got_there(accept, state, slot, *history, names, first_names, state["places"]) \
            if history else []
        out.append({"n": len(out) + 1, "day": slot[0], "time": hhmm(slot[1]), "text": text,
                    "kind": kind, "probe": probe, "accept": accept, "answer": keys_, "moves": story,
                    "type": objects[accept[0]]["type"],
                    "looks": {f: [{k: v for k, v in s.items()} for s in shown.get(f, [])]
                              for f in shown},
                    "people": {r: v for r, v in people.items()}})
    return out


def build(run: pathlib.Path, n: int, seed: int, settle: int = SETTLE_DAYS) -> dict:
    spec, states = load(run)
    rng = random.Random(seed)
    objects = {o["id"]: o for o in spec["objects"]}
    names = {oid: phrase(o) for oid, o in objects.items()}
    layout = build_layout(spec, states)
    first_names = {r["id"]: r["name"].split()[0] for r in spec["residents"]}
    patrol_log = patrols(states, layout, names, rng, first_names)
    qs = questions(spec, states, patrol_log, layout, names, n, rng, settle, load_moves(run))
    owned = collections.defaultdict(list)
    for oid, o in objects.items():
        if o.get("owner") in {r["id"] for r in spec["residents"]}:
            owned[o["owner"]].append(names[oid])
    first = " and ".join(r["name"].split()[0] for r in spec["residents"])
    return {"run": run.name, "scene": spec.get("scene"), "session": f"{run.name}-s{seed}",
            "title": f"Where Is It at {first}'s", "names": names,
            "residents": [{"id": r["id"], "name": r["name"], "job": r["job"],
                           "household": r.get("household"), "owns": sorted(owned[r["id"]])}
                          for r in spec["residents"]],
            "layout": layout, "patrols": patrol_log, "questions": qs,
            "rules": {"patrol_times": [hhmm(t) for t in PATROL_TIMES],
                      "rooms_per_patrol": max(3, math.ceil(len(layout["rooms"]) * ROOMS_SHARE)),
                      "max_looks": MAX_LOOKS,
                      "settle_days": settle}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=pathlib.Path)
    ap.add_argument("--questions", type=int, default=30)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--settle", type=int, default=SETTLE_DAYS, help="days before questions start")
    ap.add_argument("--out", type=pathlib.Path, help="folder to write to (default <run>/play)")
    ap.add_argument("--force", action="store_true", help="overwrite a session even if its questions change")
    args = ap.parse_args()
    data = build(args.run, args.questions, args.seed, args.settle)
    out = args.out or args.run / "play"
    out.mkdir(parents=True, exist_ok=True)
    old = out / "play_data.json"
    if old.exists() and not args.force:
        prev = json.loads(old.read_text())
        key = lambda d: [(q["day"], q["time"], q["text"]) for q in d["questions"]]
        if prev.get("session") == data["session"] and key(prev) != key(data):
            raise SystemExit(f"{old} holds session {data['session']} with different questions; saved "
                             "answers are keyed by session and question number, so they would land on "
                             "other questions. Use another --seed or --out, or --force.")
    (out / "play_data.json").write_text(json.dumps(data, indent=1))
    template = (pathlib.Path(__file__).parent / "play_template.html").read_text()
    page = template.replace("/*__TITLE__*/", data["title"]).replace(
        "/*__DATA__*/", json.dumps(data).replace("</", "<\\/"))
    (out / "index.html").write_text(page)
    kinds = collections.Counter(q["kind"] for q in data["questions"])
    print(f"wrote {out / 'play_data.json'}: {len(data['questions'])} questions {dict(kinds)}, "
          f"{len(data['patrols'])} patrols")


if __name__ == "__main__":
    main()
