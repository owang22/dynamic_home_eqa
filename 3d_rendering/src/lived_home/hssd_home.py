"""A household layout from an HSSD home: rooms, furniture and spots come from the 3D
scene (lived_home.hssd_layout); the model only names them.

Two kinds of call:
- home: the whole home at once; returns a short description of the home, a plain
  name for each piece of furniture ("tv console", "left nightstand") and the spot
  just inside the front door.
- room: one per room; returns a name and 2 to 4 descriptions for each spot.

The model refers to furniture and spots by list number; ids are built in code
from the room, the furniture name and the spot name. Kind (surface / open /
closed) and geometry stay as the 3D scene gives them, so positions.json can be
placed back into the same scene.
"""
from __future__ import annotations

import collections
import math

from lived_home import prompts
from lived_home.household import slug
from lived_home.layout import CLOSED, OPEN, Layout, Place
from lived_home.schemas import STR, _arr, _enum, _obj

NEIGHBOURS = 2          # nearby furniture named for each piece


def _part(spot: dict) -> str:
    """The asset maker's label for the part a spot comes from ("cabinet_left_bottom")."""
    src = spot.get("source") or ""
    word = src.split(" ")[0]
    if "_receptacle_mesh" in word:
        word = word.split("_receptacle_mesh")[0]
        word = word.split("_", 1)[1] if "_" in word else word
        return word
    return ""


def number(home: dict) -> tuple[list[dict], list[dict]]:
    """Furniture and spots in prompt order (room by room); each gets n from 1."""
    rooms = [r["id"] for r in home["rooms"]]
    furniture = sorted(home["furniture"], key=lambda f: (rooms.index(f["room"]), f["id"]))
    for i, f in enumerate(furniture, 1):
        f["n"] = i
    order = {f["id"]: f["n"] for f in furniture}
    spots = sorted(home["spots"], key=lambda s: (rooms.index(s["room"]),
                                                 order.get(s["furniture"], 0),
                                                 s.get("height", 0.0)))
    for i, s in enumerate(spots, 1):
        s["n"] = i
    return furniture, spots


def _neighbours(f: dict, furniture: list[dict]) -> list[dict]:
    same = [g for g in furniture if g["room"] == f["room"] and g is not f]
    d = lambda g: math.dist((f["position"][0], f["position"][2]), (g["position"][0], g["position"][2]))
    return sorted(same, key=d)[:NEIGHBOURS]


def _spot_line(s: dict) -> str:
    tags = [s["kind"] if s["kind"] != "surface" else "surface",
            f"{s.get('height', 0):.2f} m up", f"{s.get('area', 0):.2f} m2"]
    if s.get("of", 1) > 1:
        tags.append(f"height {s['index']} of {s['of']}")
    if s.get("behind_door"):
        tags.append("behind a door")
    if _part(s):
        tags.append(f"maker's label {_part(s)}")
    return f"S{s['n']} (" + ", ".join(tags) + ")"


def home_text(home: dict, furniture: list[dict], spots: list[dict],
              names: dict | None = None) -> str:
    """Rooms, furniture and spots as the model sees them. With names, furniture is
    shown by the name already given."""
    by_f = collections.defaultdict(list)
    for s in spots:
        by_f[s["furniture"]].append(s)
    lines = []
    for r in home["rooms"]:
        lines.append(f"{r['id']} ({r.get('area', 0):.0f} m2):")
        floor = [s for s in by_f[None] if s["room"] == r["id"]]
        for s in floor:
            lines.append(f"  the floor: S{s['n']}")
        for f in furniture:
            if f["room"] != r["id"]:
                continue
            label = names[f["n"]] if names else f"F{f['n']} {f['category']}"
            what = f"'{f['name']}'" if f.get("name") else ""
            near = ", ".join((names[g['n']] if names else f"F{g['n']} {g['category']}")
                             for g in _neighbours(f, furniture))
            parts = "; ".join(_spot_line(s) for s in by_f[f["id"]]) or "no spots"
            lines.append(f"  {label} {what}{' (its doors and drawers can be opened)' if f.get('articulated') else ''}"
                         f"{', near ' + near if near else ''}: {parts}")
    return "\n".join(lines)


def home_schema(furniture: list[dict], spots: list[dict]) -> dict:
    item = _obj({"n": {"type": "integer", "enum": [f["n"] for f in furniture]}, "name": STR})
    return _obj({"thinking": STR, "home": STR,
                 "furniture": _arr(item, len(furniture), len(furniture)),
                 "entry_spot": {"type": "integer", "enum": [s["n"] for s in spots]}})


def room_schema(room_spots: list[dict]) -> dict:
    item = _obj({"n": {"type": "integer", "enum": [s["n"] for s in room_spots]},
                 "name": STR, "descriptions": _arr(STR, 2, 4)})
    return _obj({"thinking": STR, "spots": _arr(item, len(room_spots), len(room_spots))})


def check_cover(key: str, wanted: list[int]):
    """Every number once: the schema fixes the count and the allowed numbers, so the
    only way to miss one is to repeat another."""
    def check(ans: dict) -> str:
        got = collections.Counter(x["n"] for x in ans[key])
        twice = sorted(n for n, c in got.items() if c > 1)
        missing = sorted(set(wanted) - set(got))
        if twice or missing:
            return (f"Each number exactly once. Repeated: {twice}. "
                    f"Missing: {missing}.")
        return ""
    return check


def check_kitchen(layout: Layout) -> str:
    """A kitchen needs somewhere to cook and a sink basin to wash up in."""
    from lived_home.hssd_layout import STOVE_CATEGORIES, STOVE_NAME_WORDS
    kitchen = [p for p in layout.places.values() if "kitchen" in p.room]
    if not kitchen:
        return "no kitchen"
    def cooks(p):
        g = p.geometry
        text = f"{g.get('category') or ''} {g.get('source') or ''}".lower()
        return g.get("category") in STOVE_CATEGORIES or any(w in text for w in STOVE_NAME_WORDS)
    missing = [what for what, ok in (("a cooker spot", any(map(cooks, kitchen))),
                                     ("an open sink basin", any(p.kind == OPEN for p in kitchen)))
               if not ok]
    return "the kitchen lacks " + " and ".join(missing) if missing else ""


def _unique(base: str, taken: set) -> str:
    out, k = base, 2
    while out in taken:
        out, k = f"{base}_{k}", k + 1
    taken.add(out)
    return out


def geometry(scene: str, s: dict, f: dict | None) -> dict:
    """Enough to find the spot in the 3D scene again."""
    g = {"scene": scene, "hssd_spot": s["id"], "source": s.get("source"),
         "center": s.get("center"), "height": s.get("height"), "area": s.get("area")}
    if f:
        g.update({"hssd_furniture": f["id"], "category": f.get("category"),
                  "template": f.get("template"), "instance_list": f.get("instance_list"),
                  "instance_index": f.get("instance_index"), "articulated": f.get("articulated"),
                  "position": f.get("position"), "rotation": f.get("rotation"),
                  "scale": f.get("scale")})
    return g


def build(home: dict, furniture: list[dict], spots: list[dict], fnames: dict,
          snames: dict, entry_n: int) -> Layout:
    """Places with ids composed from room, furniture name and spot name.
    fnames: n -> name; snames: n -> {"name", "descriptions"}."""
    fby = {f["id"]: f for f in furniture}
    taken: set = set()
    places, by_n = [], {}
    for s in spots:
        f = fby.get(s["furniture"])
        fname = fnames[f["n"]] if f else "floor"
        sn = snames[s["n"]]
        if f:
            pid = _unique(slug(f"{s['room']} {fname} {sn['name']}"), taken)
        else:
            pid = _unique(slug(f"{s['room']} floor"), taken)
        kind = s["kind"] if s["kind"] in (OPEN, CLOSED) else "surface"
        p = Place(pid, s["room"], fname, sn["name"], kind, False, list(sn["descriptions"]),
                  geometry(home["scene"], s, f))
        places.append(p)
        by_n[s["n"]] = pid
    return Layout(places, by_n[entry_n])


def create_layout(caller, home: dict) -> tuple[Layout, dict]:
    """The two kinds of naming call; returns the layout and a record of the answers."""
    furniture, spots = number(home)
    text = home_text(home, furniture, spots)
    ans = caller.call("create/hssd_home", prompts.CREATE_SYSTEM,
                      prompts.HSSD_HOME_USER.format(home=text),
                      home_schema(furniture, spots),
                      check_cover("furniture", [f["n"] for f in furniture]), max_tokens=30000)
    fnames = _distinct({x["n"]: x["name"].strip() for x in ans["furniture"]}, furniture)
    named = home_text(home, furniture, spots, fnames)
    snames, rooms = {}, {}
    for r in home["rooms"]:
        rs = [s for s in spots if s["room"] == r["id"]]
        if not rs:
            continue
        ra = caller.call(f"create/hssd_room/{r['id']}", prompts.CREATE_SYSTEM,
                         prompts.HSSD_ROOM_USER.format(home=ans["home"], layout=named,
                                                       room=r["id"]),
                         room_schema(rs), check_cover("spots", [s["n"] for s in rs]),
                         max_tokens=20000)
        rooms[r["id"]] = ra["thinking"]
        for x in ra["spots"]:
            snames[x["n"]] = {"name": x["name"].strip(), "descriptions": x["descriptions"]}
    layout = build(home, furniture, spots, fnames, snames, ans["entry_spot"])
    record = {"scene": home["scene"], "home": ans["home"], "thinking": ans["thinking"],
              "room_thinking": rooms}
    return layout, record


def _distinct(names: dict, furniture: list[dict]) -> dict:
    """Two pieces in one room never share a name: the second gets 'second', and so on."""
    out, seen = {}, collections.Counter()
    for f in furniture:
        name = names[f["n"]] or f["category"]
        key = (f["room"], name.lower())
        seen[key] += 1
        out[f["n"]] = name if seen[key] == 1 else f"{name} {seen[key]}"
    return out
