"""Photograph every camera position at every question time, once, so that a
search can be run afterwards as lookups.

    python -m rendered_look.searchbench.render_positions --rig go2
    python -m rendered_look.searchbench.render_positions --rig raised

Writes, under results/rendered_look/hh_s151/searchbench/<rig>/:
  positions.json      every camera position: id, room, place, eye, target, and the
                      walking distance between every pair, in metres
  moments.json        the question times used, with where everything is
  observations.jsonl  one line per (moment, position): what the picture shows
  frames/             the pictures, one file per distinct picture

The camera does not aim at the things (a robot does not know where they are):
each position looks where it was set to look. Nobody steps aside for a resident.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

RIGS = {
    # the Go2 Pro's own camera: 0.37 m, about 100 degrees across, 16:9
    "go2": {"RENDERED_LOOK_EYE": "0.37", "RENDERED_LOOK_LENS": "100", "RENDERED_LOOK_SHAPE": "960x540"},
    # a camera raised to 1.0 m, the height the study found sees everything
    "raised": {"RENDERED_LOOK_EYE": "1.00", "RENDERED_LOOK_LENS": "75", "RENDERED_LOOK_SHAPE": "960x720"},
}
PER_PLACE = 5     # the picker's choice plus four alternates
QUESTIONS_A_DAY = 8


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rig", choices=sorted(RIGS), required=True)
    parser.add_argument("--days", type=int, nargs="*", default=None, help="default: every day with questions")
    parser.add_argument("--tag", default="", help="a suffix for the output folder, for small trial runs")
    parser.add_argument("--walkthrough", action="store_true",
                        help="only the whole-room positions at 18:00 on day 0, written to walkthrough.jsonl")
    args = parser.parse_args()
    for key, value in RIGS[args.rig].items():   # must be set before the rendering modules load
        os.environ[key] = value
    os.environ["RENDERED_LOOK_OTHER_POSITIONS"] = "7"

    import numpy as np
    from PIL import Image
    from rendered_look import render as render_module
    from rendered_look.render import Scene

    scene = Scene()
    out = scene.out / "searchbench" / (args.rig + args.tag)
    (out / "frames").mkdir(parents=True, exist_ok=True)

    # ---- the positions
    positions = []
    if args.walkthrough:
        for view in scene.views:
            if view["kind"] == "whole room":
                for n, stand in enumerate([view] + view.get("otherwise", [])):
                    positions.append({"id": f"{view['name']}#{n}", "view": view["name"], "room": view["room"],
                                      "kind": "whole room", "place": None, "eye": stand["eye"], "target": stand["target"]})
        state = scene.set_moment(0, "18:00")
        with (out / "walkthrough.jsonl").open("w") as log:
            log.write(json.dumps({"header": True, "t": 18 * 3600, "things": state["things"]}) + "\n")
            for p in positions:
                shot = scene.picture({"name": p["view"], "kind": "whole room", "eye": p["eye"], "target": p["target"], "otherwise": []})
                log.write(json.dumps({"t": 18 * 3600, "position": p["id"], "in_picture": shot["in_picture"]}) + "\n")
        print(f"walkthrough: {len(positions)} whole-room positions at day 0, 18:00")
        scene.world.close()
        return
    for view in scene.views:
        stands = [view] + view.get("otherwise", [])
        if view["kind"] == "one place":
            stands = stands[:PER_PLACE]
        for n, stand in enumerate(stands):
            positions.append({"id": f"{view['name']}#{n}", "view": view["name"], "room": view["room"],
                              "kind": view["kind"], "place": view.get("place"),
                              "eye": stand["eye"], "target": stand["target"]})
    floor_points = [np.array([p["eye"][0], p["eye"][1] - float(os.environ["RENDERED_LOOK_EYE"]), p["eye"][2]],
                    dtype=np.float32) for p in positions]
    import habitat_sim
    metres = np.zeros((len(positions), len(positions)))
    for i, a in enumerate(floor_points):
        for j, b in enumerate(floor_points):
            if j > i:
                walk = habitat_sim.ShortestPath()
                walk.requested_start, walk.requested_end = a, b
                found = scene.world.sim.pathfinder.find_path(walk)
                metres[i, j] = metres[j, i] = float(walk.geodesic_distance) if found else -1.0
    (out / "positions.json").write_text(json.dumps({
        "rig": args.rig, "settings": RIGS[args.rig], "positions": positions,
        "metres_between": np.round(metres, 2).tolist(),
        "unreachable_pairs": int((metres < 0).sum() // 2)}))
    print(f"{len(positions)} positions, {int((metres < 0).sum() // 2)} unreachable pairs")

    # ---- the moments: some of each day's questions, spread through the day
    by_day = {}
    for q in scene.bank.questions:
        by_day.setdefault(q["day_index"], []).append(q)
    days = args.days if args.days else sorted(by_day)
    moments = []
    for day in days:
        qs = sorted(by_day.get(day, []), key=lambda q: q["t_query"])
        keep = [qs[int(i)] for i in np.linspace(0, len(qs) - 1, min(QUESTIONS_A_DAY, len(qs)))] if qs else []
        for q in keep:
            t = q["t_query"]
            moments.append({"day": t // 86400, "clock": f"{(t % 86400) // 3600:02d}:{(t % 3600) // 60:02d}",
                            "t": t, "question_id": q["question_id"], "asked_about": q["object_id"]})
    print(f"{len(moments)} moments over {len(days)} days")

    # ---- the pictures
    seen_files = set()
    with (out / "observations.jsonl").open("w") as log:
        for k, moment in enumerate(moments):
            state = scene.set_moment(moment["day"], moment["clock"])
            moment["things"] = state["things"]
            moment["people"] = state["people"]
            for p in positions:
                shot = scene.picture({"name": p["view"], "kind": p["kind"], "eye": p["eye"],
                                      "target": p["target"], "otherwise": []})
                said = json.dumps([p["id"]] + sorted((x["what"], x["pixels"], x["box"]) for x in shot["in_picture"]))
                name = hashlib.sha1(said.encode()).hexdigest()[:12] + ".jpg"
                if name not in seen_files and not (out / "frames" / name).exists():
                    Image.fromarray(shot["colour"]).resize((640, 480 if shot["colour"].shape[0] == 720 else 360),
                                                          Image.LANCZOS).save(out / "frames" / name, quality=75)
                seen_files.add(name)
                log.write(json.dumps({"t": moment["t"], "position": p["id"], "frame": name,
                                      "in_picture": shot["in_picture"]}) + "\n")
            if k % 20 == 0:
                print(f"moment {k + 1} of {len(moments)}: day {moment['day']} {moment['clock']}, "
                      f"{len(seen_files)} distinct pictures so far", flush=True)
    (out / "moments.json").write_text(json.dumps(moments))
    print(f"done: {len(seen_files)} distinct pictures")
    scene.world.close()


if __name__ == "__main__":
    main()
