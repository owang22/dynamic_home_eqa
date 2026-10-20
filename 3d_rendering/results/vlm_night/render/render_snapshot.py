"""Place one household-A snapshot in the HSSD home and photograph every fixed spot view.

    ~/miniconda3/envs/dynamic_eqa/bin/python render_snapshot.py <day> <HHMM> [--force]
    e.g.  render_snapshot.py 7 1800

Reads spot_views.json (made by choose_views.py). Writes, under
/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a/day_XX/HHMM/:
  <spot>.jpg        the picture (640x480, 75 deg lens, eye 1.0 m)
  <spot>_ids.png    16-bit picture of object ids (value = semantic id; truth.json maps ids to objects)
  truth.json        what each picture shows, every object's fate, and the lists a question-writer
                    needs (see README.md)
A snapshot whose truth.json exists is skipped unless --force is given.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict

import numpy as np
from PIL import Image

import lib


def not_placed_reason(why):
    """Short reason for an object that is not in the 3D scene."""
    why = why or ""
    for start, reason in (("no 3D model", "no 3D model"),
                          ("with a person", "with a person (worn, held, pocketed, or in or on something a person has)"),
                          ("worn by", "with a person (worn, held, pocketed, or in or on something a person has)"),
                          ("in pocket of", "with a person (worn, held, pocketed, or in or on something a person has)"),
                          ("out of the house", "out of the house"),
                          ("larger than the box of its closed container", "larger than its closed container"),
                          ("no room left inside its closed container", "no room left in its closed container"),
                          ("its container", "its container is not drawn"),
                          ("no free room", "no free room on its place"),
                          ("no cells found", "drawer bottom not found")):
        if why.startswith(start):
            return reason
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("day", type=int)
    ap.add_argument("hhmm")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    snap_file = lib.snapshot_path(a.day, a.hhmm)
    out = lib.PICS / f"day_{a.day:02d}" / a.hhmm
    if (out / "truth.json").exists() and not a.force:
        print(f"skip day {a.day} {a.hhmm}: done")
        return 0
    out.mkdir(parents=True, exist_ok=True)
    spot_views = json.load(lib.SPOT_VIEWS.open())
    views = spot_views["views"]
    viewed = {v["spot"] for v in views}

    t0 = time.time()
    cams = [dict(uuid="colour", kind="colour", width=lib.W, height=lib.H, hfov=lib.HFOV),
            dict(uuid="ids", kind="ids", width=lib.W, height=lib.H, hfov=lib.HFOV)]
    home = lib.open_home(snap_file, cams)
    home.place_everything()
    t_placed = time.time()
    snap = home.snap
    objs = snap["objects"]
    sid_to_oid = {f["sid"]: oid for oid, f in home.facts.items()}

    def fact(oid):
        o, r = objs[oid], home.records[oid]
        m = r.get("model") or {}
        return {"type": o["type"], "looks": o.get("looks"), "relation": o["relation"],
                "reference": o["reference"], "reference_kind": o["reference_kind"],
                "place": o["place"], "room": o.get("room"), "hidden_in_snapshot": bool(o["hidden"]),
                "placed": bool(r.get("placed")), "did_not_fit": bool(r.get("did_not_fit", False)),
                "model_source": m.get("source"), "model_is_stand_in": bool(m.get("stand_in", False)),
                "model_looks_like": m.get("looks_like")}

    pictures = {}
    max_px = defaultdict(int)
    best_pic = {}
    visible_in = defaultdict(list)
    t_render = 0.0
    for v in views:
        spot = v["spot"]
        t1 = time.time()
        lib.common.look_from(home.sim, np.array(v["eye"]), np.array(v["target"]))
        shot = home.shoot("colour", "ids")
        colour, ids = shot["colour"][:, :, :3], shot["ids"]
        t_render += time.time() - t1
        Image.fromarray(colour).save(out / f"{spot}.jpg", quality=90)
        Image.fromarray(ids.astype(np.uint16)).save(out / f"{spot}_ids.png")
        vals, counts = np.unique(ids, return_counts=True)
        px = {sid_to_oid[s]: int(c) for s, c in zip(vals.tolist(), counts.tolist()) if s in sid_to_oid}
        on_spot = [oid for oid, o in objs.items() if o["place"] == spot]
        listed = []
        for oid in sorted(set(px) | set(on_spot), key=lambda k: (-px.get(k, 0), k)):
            n = px.get(oid, 0)
            listed.append({"object": oid, "pixels": n, "visible": n >= lib.VISIBLE_PX,
                           "on_this_spot": objs[oid]["place"] == spot,
                           "semantic_id": home.facts.get(oid, {}).get("sid"), **fact(oid)})
            if n > max_px[oid]:
                max_px[oid], best_pic[oid] = n, spot
            if n >= lib.VISIBLE_PX:
                visible_in[oid].append(spot)
        pictures[spot] = {
            "picture": f"{spot}.jpg", "ids_picture": f"{spot}_ids.png", "spot_name": v["spot_name"],
            "room": v["room"], "eye": v["eye"], "target": v["target"],
            "visible_objects": sum(1 for t in listed if t["visible"]),
            "visible_objects_on_this_spot": sum(1 for t in listed if t["visible"] and t["on_this_spot"]),
            "objects_on_this_spot": len(on_spot),
            "objects": listed,
        }

    objects, not_placed, overlapping, open_unseen, hidden_seen = {}, [], [], [], []
    repairs = getattr(home, "repairs", None)      # recorded by lib.SnapshotHomeV2 only
    hidden_unseen = 0
    for oid in sorted(objs):
        f = fact(oid)
        r = home.records[oid]
        f.update(why_not_placed=None if f["placed"] else r.get("why"),
                 max_pixels=max_px.get(oid, 0), best_picture=best_pic.get(oid),
                 visible_in=visible_in.get(oid, []))
        if repairs is not None:
            f["repairs"] = [{k: x[k] for k in ("kind", "what", "from", "to")} for x in r.get("repairs", [])]
        objects[oid] = f
        short = {"object": oid, "type": f["type"], "place": f["place"], "relation": f["relation"],
                 "reference": f["reference"]}
        if not f["placed"]:
            not_placed.append({**short, "reason": not_placed_reason(r.get("why")), "why": r.get("why"),
                               "has_model": oid in home.things})
            continue
        if f["did_not_fit"]:
            overlapping.append(short)
        seen = max_px.get(oid, 0) >= lib.VISIBLE_PX
        if f["hidden_in_snapshot"]:
            if seen:
                hidden_seen.append({**short, "max_pixels": max_px[oid], "best_picture": best_pic[oid]})
            else:
                hidden_unseen += 1
        elif not seen:
            why = "its spot has no view (closed place or skipped spot)" if f["place"] not in viewed else \
                "out of frame or blocked in its spot's picture, and in no other picture"
            open_unseen.append({**short, "max_pixels": max_px.get(oid, 0), "why": why})

    timings = {"place_s": round(t_placed - t0, 1), "render_s": round(t_render, 2),
               "total_s": round(time.time() - t0, 1), **home.timings}
    truth = {
        "snapshot": str(snap_file), "day": a.day, "time": a.hhmm, "scene": snap["scene"],
        "visible_rule": f"an object is visible in a picture when it covers >= {lib.VISIBLE_PX} pixels "
                        "of the ids picture; every count is kept so the rule can change",
        "people": {"note": "people are not drawn", **snap["people"]},
        "pictures": pictures,
        "objects": objects,
        "summary": {
            "objects": len(objs), "placed": sum(1 for f in objects.values() if f["placed"]),
            "not_placed": len(not_placed), "placed_overlapping_or_overhanging": len(overlapping),
            "placed_not_hidden_in_no_picture": len(open_unseen),
            "hidden_in_snapshot_in_no_picture": hidden_unseen,
            "hidden_in_snapshot_but_visible": len(hidden_seen),
            "visible_somewhere": sum(1 for f in objects.values() if f["max_pixels"] >= lib.VISIBLE_PX),
            "not_placed_by_reason": dict(Counter(x["reason"] for x in not_placed).most_common()),
            "no_3d_model": [{"object": x["object"], "type": x["type"]} for x in not_placed
                            if x["reason"] == "no 3D model"],
            "with_a_person_not_drawn": [{"object": x["object"], "type": x["type"], "why": x["why"]}
                                        for x in not_placed if x["reason"] == "with a person (worn, held, "
                                        "pocketed, or in or on something a person has)"],
        },
        "not_placed": not_placed,
        "placed_overlapping_or_overhanging": overlapping,
        "placed_not_hidden_in_no_picture": open_unseen,
        "hidden_in_snapshot_but_visible": hidden_seen,
        "timings": timings,
    }
    if repairs is not None:
        truth["summary"].update(
            repairs=len(repairs), objects_repaired=len({x["object"] for x in repairs}),
            repairs_by_kind=dict(Counter(x["kind"] for x in repairs).most_common()))
        truth["repairs"] = [{k: x[k] for k in ("object", "kind", "what", "from", "to")} for x in repairs]
        truth["repairs_note"] = ("every change the renderer made to what the snapshot says, per object: "
                                 "kind, what was done, from (what the snapshot asked), to (what was drawn)")
    line_summary = {k: v for k, v in truth["summary"].items() if not isinstance(v, (list, dict))}
    lib.json_dump(truth, out / "truth.json")
    line = {"day": a.day, "time": a.hhmm, **timings, **line_summary, "pictures": len(pictures),
            "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(lib.CODE / "logs" / "render_times.jsonl", "a") as fh:
        fh.write(json.dumps(line) + "\n")
    print(json.dumps(line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
