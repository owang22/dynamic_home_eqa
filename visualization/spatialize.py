#!/usr/bin/env python3
"""Ground a symbolic hh timeline in a baked HSSD scene, room-level.

Self-contained (stdlib + PyYAML only; no habitat, no legacy imports).
Reads a spatial config (room_map + receptacle anchors + relations), the
schedule spec, the baked scene assets (scene.json from bake_scene.py), and a
simulated timeline dir (events.jsonl / hourly.csv from simulate_schedule.py).

Regenerates the timeline dir in place, room-level:

  events.jsonl      each event gains room_from / room_to / relation / pos
                    (world [x, z] of the destination anchor; ELSEWHERE maps
                    to the config's outside-the-door point)
  hourly_rooms.csv  same shape as hourly.csv but values are rooms, with
                    ELSEWHERE -> "outside"
  trace.json        everything the web viewer consumes: map transform, room
                    polygons, receptacle anchors, per-object segment lists
                    [t0, t1, receptacle, room, relation, x, z, cause, kind]
                    (kind: rule / misplace / carry_pickup / carry_putdown),
                    and a `provenance` block carrying the authored `cites`
                    behind each object's rules

Placement semantics carried per receptacle (`relation`): on_surface (object
sits ON the receptacle), floor (on the floor beside things), hook (hung).
Objects co-located at one receptacle get a small deterministic per-object
offset so markers don't stack; floor relations get a larger spread.

Usage:
  python spatialize.py configs/hh_001_102343992.yaml \
      --timeline ../profiles/revamp_v1/claude-fable-5/timelines/hh_001_seed0
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pathlib

import yaml

ELSEWHERE = "ELSEWHERE"
PERSON = "person:"
OUTSIDE_ROOM = "outside"

# The assembled program that DROVE the simulation, most recent pipeline
# first. Order matters and "first file that exists" is not enough:
# story_calendar writes three programs into one household dir and only
# story_program.yaml is the one simulate_program() was handed, so picking
# bound_program.yaml there would quote rules this timeline never ran.
PROGRAM_FILES = ("program.yaml",         # storyfirst
                 "story_program.yaml",   # story_calendar
                 "bound_program.yaml",   # rule_based / freeform
                 "routine_program.yaml")


# ---------------------------------------------------------------- geometry

def point_in_poly(x: float, z: float, poly: list[list[float]]) -> bool:
    inside = False
    for i in range(len(poly)):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % len(poly)]
        if (z1 > z) != (z2 > z):
            xin = x1 + (z - z1) / (z2 - z1) * (x2 - x1)
            if x < xin:
                inside = not inside
    return inside


def centroid(poly: list[list[float]]) -> tuple[float, float]:
    xs = [p[0] for p in poly]
    zs = [p[1] for p in poly]
    return sum(xs) / len(xs), sum(zs) / len(zs)


def object_offset(obj: str, relation: str) -> tuple[float, float]:
    """Deterministic tiny offset so co-located object markers don't stack."""
    h = int(hashlib.md5(obj.encode()).hexdigest(), 16)
    ang = (h % 3600) / 3600.0 * 2 * math.pi
    r = 0.10 + (h // 3600 % 100) / 100.0 * 0.08
    if relation == "floor":
        r += 0.30                       # beside the anchor, not on it
    return r * math.cos(ang), r * math.sin(ang)


# ---------------------------------------------------------------- loading

def resolve_anchor(frac: list[float], region: dict) -> tuple[float, float]:
    """Fraction-of-bbox anchor, nudged inside the region polygon if needed."""
    mn, mx = region["min_bounds"], region["max_bounds"]
    x = mn[0] + frac[0] * (mx[0] - mn[0])
    z = mn[2] + frac[1] * (mx[2] - mn[2])
    poly = region["poly"]
    if poly and not point_in_poly(x, z, poly):
        cx, cz = centroid(poly)
        for step in range(1, 21):       # walk toward the centroid until inside
            t = step / 20.0
            xi, zi = x + (cx - x) * t, z + (cz - z) * t
            if point_in_poly(xi, zi, poly):
                return xi, zi
        return cx, cz
    return x, z


def build_world(cfg: dict, cfg_dir: pathlib.Path) -> dict:
    scene = json.loads((cfg_dir / cfg["scene_assets"] / "scene.json").read_text())
    regions = {r["name"]: r for r in scene["rooms"]}
    spec = yaml.safe_load((cfg_dir / cfg["schedule_spec"]).read_text())
    rec_room = {r["id"]: r["room"] for r in spec["receptacles"]}

    rooms, missing = {}, []
    for sym, region_name in cfg["room_map"].items():
        if region_name not in regions:
            missing.append(region_name)
            continue
        rooms[sym] = regions[region_name]
    assert not missing, f"room_map names not in scene: {missing}"

    recs = {}
    for rid, rcfg in cfg["receptacles"].items():
        room = rec_room[rid]
        x, z = resolve_anchor(rcfg["anchor"], rooms[room])
        recs[rid] = {"room": room, "region": cfg["room_map"][room],
                     "pos": [round(x, 3), round(z, 3)],
                     "relation": rcfg["relation"]}
    unplaced = set(rec_room) - set(recs)
    assert not unplaced, f"spec receptacles missing from spatial config: {unplaced}"

    xs, zs = [], []
    for r in rooms.values():
        xs += [r["min_bounds"][0], r["max_bounds"][0]]
        zs += [r["min_bounds"][2], r["max_bounds"][2]]
    ex, ez = cfg["elsewhere"]["pos"]
    m = cfg.get("view_margin_m", 2.0)
    view = [[min(xs + [ex]) - m, min(zs + [ez]) - m],
            [max(xs + [ex]) + m, max(zs + [ez]) + m]]

    return {"scene": scene, "rooms": rooms, "receptacles": recs, "view_bbox": view}


# ---------------------------------------------------------------- spatialize

def load_resident_tracks(timeline: pathlib.Path, world: dict, cfg: dict,
                         horizon: int) -> dict:
    """resident -> gap-filled position segments [t0, t1, at, room, x, z, activity].
    Between blocks a resident stays where their last block put them; a
    resident whose block is at ELSEWHERE stands at the outside spot."""
    path = timeline / "residents.jsonl"
    tracks = {}
    if not path.exists():
        return tracks
    blocks = {}
    for line in open(path):
        b = json.loads(line)
        blocks.setdefault(b["resident"], []).append(b)
    for res, bl in blocks.items():
        bl.sort(key=lambda b: b["t0"])
        segs, cursor, last_at = [], 0, bl[0].get("at")
        for b in bl:
            at = b.get("at") or last_at
            if b["t0"] > cursor:
                segs.append((cursor, b["t0"], last_at, "idle"))
            segs.append((b["t0"], b["t1"], at, b["activity"]))
            cursor, last_at = b["t1"], at
        if cursor < horizon:
            segs.append((cursor, horizon, last_at, "idle"))
        out = []
        h = int(hashlib.md5(res.encode()).hexdigest(), 16)
        rdx, rdz = 0.25 * math.cos(h % 360), 0.25 * math.sin(h % 360)
        for t0, t1, at, activity in segs:
            if t0 >= t1:
                continue
            if at in (None, ELSEWHERE):
                ex, ez = cfg["elsewhere"]["pos"]
                out.append([t0, t1, at or ELSEWHERE, OUTSIDE_ROOM,
                            round(ex + rdx, 3), round(ez + rdz, 3), activity])
            else:
                r = world["receptacles"][at]
                out.append([t0, t1, at, r["room"],
                            round(r["pos"][0] + rdx, 3),
                            round(r["pos"][1] + rdz, 3), activity])
        tracks[res] = out
    return tracks


def resident_loc_at(tracks: dict, res: str, t: int):
    for t0, t1, at, room, x, z, activity in tracks.get(res, []):
        if t0 <= t < t1:
            return room, x, z
    return OUTSIDE_ROOM, None, None


def locate(rec: str, obj: str, world: dict, cfg: dict,
           tracks: dict | None = None, t: int | None = None):
    """(room, relation, [x, z]) for an object sitting at location `rec`."""
    if rec == ELSEWHERE:
        ex, ez = cfg["elsewhere"]["pos"]
        dx, dz = object_offset(obj, "floor")
        return OUTSIDE_ROOM, "away", [round(ex + dx, 3), round(ez + dz, 3)]
    if rec.startswith(PERSON):
        res = rec[len(PERSON):]
        dx, dz = object_offset(obj, "carried")
        room, x, z = resident_loc_at(tracks or {}, res, t or 0)
        if x is None:
            ex, ez = cfg["elsewhere"]["pos"]
            x, z = ex, ez
        return room, "carried", [round(x + dx, 3), round(z + dz, 3)]
    r = world["receptacles"][rec]
    dx, dz = object_offset(obj, r["relation"])
    return r["room"], r["relation"], [round(r["pos"][0] + dx, 3),
                                      round(r["pos"][1] + dz, 3)]


def _resident_info(timeline: pathlib.Path) -> dict:
    """{resident_id: {name, age, occupation, personality}} from the
    household's persona.yaml (the timeline dir's parent). Missing or
    unreadable persona -> {}, never fatal: the viewer degrades to bare
    ids and everything else still renders."""
    import yaml
    path = timeline.parent / "persona.yaml"
    try:
        persona = yaml.safe_load(path.read_text())
    except (OSError, ValueError):
        return {}
    if not isinstance(persona, dict):
        return {}
    out = {}
    for r in persona.get("residents") or []:
        if not isinstance(r, dict) or not r.get("id"):
            continue
        out[r["id"]] = {
            "name": str(r.get("name") or "").strip(),
            "age": r.get("age"),
            "occupation": str(r.get("occupation") or "").strip(),
            "personality": str(r.get("personality") or "").strip(),
        }
    return out


def _provenance(timeline: pathlib.Path, spec: dict) -> dict:
    """Why each object moves, in the generator's own words.

    The timeline records WHAT moved and which activity moved it; the
    RATIONALE lives a level up, in the assembled program's `object_rules`
    — a `cites` line per object and per rule, written by the model that
    authored the movement pass — plus the household-level reasoning in
    build_log.json. Baked in here rather than fetched by the viewer: the
    viewer has no YAML parser, and the program files are ~75 kB of mostly
    calendar it would have to sift on every household switch.

    Also recorded is which activities are TRIPS (`at: ELSEWHERE`). Most
    carries are not authored at all — an object whose rule names any leg
    of its owner's trips is promoted to a "traveller" and then rides ALL
    of them, so `suitcase_elena` leaves with work_away on the strength of
    a rule about `study`. Without the trip list the viewer can only shrug
    at the majority of carries; with it, it can name the rule that made
    the object a traveller.

    Best-effort throughout: sets built before the movement pass existed
    (revamp_v1, casas) get no provenance block at all, and the viewer says
    the set carries no rationale rather than inventing one.
    """
    import yaml
    hh_dir = timeline.parent
    program, used = None, None
    for name in PROGRAM_FILES:
        path = hh_dir / name
        if not path.exists():
            continue
        try:
            cand = yaml.safe_load(path.read_text())
        except (OSError, ValueError):
            continue
        # `object_rules` is the whole point; a program without it (an early
        # calendar-only draft) is no more use here than no program at all.
        if isinstance(cand, dict) and cand.get("object_rules"):
            program, used = cand, name
            break
    if program is None:
        return {}

    owners = program.get("object_owners") or {}
    objects = {}
    for entry in program["object_rules"]:
        if not isinstance(entry, dict) or not entry.get("object"):
            continue
        rules = []
        for r in entry.get("rules") or []:
            if not isinstance(r, dict):
                continue
            # dist is [{dest, p}, ...]; flattened to pairs because the
            # viewer only ever renders it as a list of "dest — p" lines.
            dist = [[d.get("dest"), d.get("p")]
                    for d in (r.get("dist") or []) if isinstance(d, dict)]
            if not dist and r.get("dest"):
                dist = [[r["dest"], 1.0]]
            rules.append({"activity": r.get("activity"),
                          "phase": r.get("phase"),
                          "cites": r.get("cites"),
                          "dist": dist})
        # `misplace_set` — where drift can actually put it — is added by the
        # expander and never appears in the program, so it comes from the
        # spec. Without it the panel can say an object drifted but not that
        # it drifted into one of six kitchen surfaces by design.
        placed = (spec.get("placements") or {}).get(entry["object"]) or {}
        objects[entry["object"]] = {
            "cites": entry.get("cites"),
            "home": entry.get("home"),
            "p_misplace": entry.get("p_misplace"),
            "misplace_set": placed.get("misplace_set") or [],
            "owner": owners.get(entry["object"]),
            "rules": rules,
        }

    # Trips, by their FULL expanded names: `study` can be a home activity
    # and `study__resident_1` a trip in the same household, so collapsing
    # to the base here would mislabel both.
    motions = spec.get("object_motions") or {}
    away = sorted(name for name, info in motions.items()
                  if isinstance(info, dict) and info.get("at") == ELSEWHERE)

    out = {"program": used, "away_activities": away, "objects": objects}
    try:
        log = json.loads((hh_dir / "build_log.json").read_text())
    except (OSError, ValueError):
        return out
    # The movement pass reasons once for the whole household before it
    # writes any per-object rule; that paragraph is the context the
    # per-rule cites are written against.
    attempts = [a for a in (log.get("movement_attempts") or [])
                if isinstance(a, dict) and a.get("reasoning")]
    if attempts:
        out["movement_reasoning"] = attempts[-1]["reasoning"]
    if log.get("persona_reasoning"):
        out["persona_reasoning"] = log["persona_reasoning"]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("config", type=pathlib.Path)
    ap.add_argument("--timeline", type=pathlib.Path, required=True)
    args = ap.parse_args()

    cfg_dir = args.config.parent.resolve()
    cfg = yaml.safe_load(args.config.read_text())
    world = build_world(cfg, cfg_dir)
    meta = json.loads((args.timeline / "meta.json").read_text())
    horizon = meta["days"] * 1440
    tracks = load_resident_tracks(args.timeline, world, cfg, horizon)

    def room_of(loc, t):
        if loc == ELSEWHERE:
            return OUTSIDE_ROOM
        if loc.startswith(PERSON):
            return resident_loc_at(tracks, loc[len(PERSON):], t)[0]
        return world["receptacles"][loc]["room"]

    # ---- events.jsonl: add room/relation/pos fields (idempotent rewrite)
    events = [json.loads(l) for l in (args.timeline / "events.jsonl").open()]
    for e in events:
        room_t, rel, pos = locate(e["to"], e["object"], world, cfg, tracks, e["t"])
        e.update(room_from=room_of(e["from"], e["t"]), room_to=room_t,
                 relation=rel, pos=pos)
    with open(args.timeline / "events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    # ---- hourly_rooms.csv from hourly.csv
    with open(args.timeline / "hourly.csv") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    objs = header[2:]
    with open(args.timeline / "hourly_rooms.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in body:
            w.writerow(row[:2] + [room_of(v, int(row[0])) for v in row[2:]])

    # ---- per-object segments for the viewer
    spec = yaml.safe_load((cfg_dir / cfg["schedule_spec"]).read_text())
    horizon = meta["days"] * 1440
    segments = {o: [] for o in spec["placements"]}
    state = {o: p["home"] for o, p in spec["placements"].items()}
    # `kind` rides along with the cause: the activity alone cannot tell a
    # rule-driven move from a carry or a random misplace, and those are
    # three different answers to "why did this move" (an authored rule, a
    # traveller riding its owner's trip, and no reason at all).
    opened = {o: (0, "initial", "initial") for o in state}
    for e in events:
        o = e["object"]
        t0, cause, kind = opened[o]
        segments[o].append((t0, e["t"], state[o], cause, kind))
        state[o] = e["to"]
        opened[o] = (e["t"], e["by"], e.get("kind") or "rule")
    for o in state:
        t0, cause, kind = opened[o]
        segments[o].append((t0, horizon, state[o], cause, kind))

    # Object classes come from the persona/profile the spec points at:
    # object_motions files say `source_persona`, retired schedule specs said
    # `source_profile`.
    objects = {}
    persona_ref = spec.get("source_persona") or spec["source_profile"]
    prof = yaml.safe_load((cfg_dir / cfg["schedule_spec"]).parent.joinpath(
        persona_ref).resolve().read_text())
    classes = {o["id"]: o["class"] for o in prof["object_inventory"]}

    for o, segs in segments.items():
        out = []
        for t0, t1, rec, cause, kind in segs:
            if t1 <= t0:
                continue
            if rec.startswith(PERSON):
                # carried: the object is wherever its carrier is, so split
                # the symbolic segment at every carrier position change
                res = rec[len(PERSON):]
                slices = [(max(t0, s0), min(t1, s1))
                          for s0, s1, *_ in tracks.get(res, [])
                          if s0 < t1 and s1 > t0] or [(t0, t1)]
                for s0, s1 in slices:
                    room, rel, pos = locate(rec, o, world, cfg, tracks, s0)
                    out.append([s0, s1, rec, room, rel, pos[0], pos[1],
                                cause, kind])
            else:
                room, rel, pos = locate(rec, o, world, cfg)
                out.append([t0, t1, rec, room, rel, pos[0], pos[1],
                            cause, kind])
        objects[o] = {"class": classes.get(o, "?"), "segments": out}

    trace = {
        "household": spec["household"],
        "scene_id": world["scene"]["scene_id"],
        "days": meta["days"], "seed": meta["seed"],
        "map": {"image": "map.png",
                "meters_per_pixel": world["scene"]["meters_per_pixel"],
                "bounds_min": world["scene"]["bounds_min"],
                "grid_shape": world["scene"]["grid_shape"]},
        "view_bbox": world["view_bbox"],
        "rooms": [{"id": sym, "region": cfg["room_map"][sym],
                   "label": world["rooms"][sym]["label"],
                   "poly": world["rooms"][sym]["poly"]}
                  for sym in world["rooms"]],
        "receptacles": world["receptacles"],
        "elsewhere": {"pos": cfg["elsewhere"]["pos"],
                      "label": cfg["elsewhere"]["label"]},
        "objects": objects,
        "residents": tracks,
        # Who resident_N actually IS. The ids are positional and carry no
        # meaning on their own, so the viewer cannot label a track, a
        # carry or an owner without this. Read from the persona sitting
        # beside the timeline; absent for sets built before it existed,
        # which the viewer renders as a plain id list.
        "resident_info": _resident_info(args.timeline),
        # Why each object moves, in the generator's own words — the
        # per-object and per-rule `cites` behind every segment's cause.
        # {} for sets built before the movement pass wrote any.
        "provenance": _provenance(args.timeline, spec),
    }
    (args.timeline / "trace.json").write_text(json.dumps(trace))

    meta["spatialization"] = {"config": str(args.config),
                              "scene_id": world["scene"]["scene_id"],
                              "room_map": cfg["room_map"]}
    (args.timeline / "meta.json").write_text(json.dumps(meta, indent=2))

    n_seg = sum(len(o["segments"]) for o in objects.values())
    print(f"spatialized {spec['household']} -> {world['scene']['scene_id']}: "
          f"{len(events)} events, {n_seg} segments, "
          f"{len(world['receptacles'])} receptacles in {len(world['rooms'])} rooms")


if __name__ == "__main__":
    main()
