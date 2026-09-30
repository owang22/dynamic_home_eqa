"""Renders what the robot's camera shows, moment by moment, and records what is in each picture.

    python -m rendered_look.render --days 2 16 --times 07:30 12:30
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import pathlib
from typing import Dict, List

import numpy as np
from PIL import Image

from rendered_look import people as people_module
from rendered_look import timeline, views
from rendered_look.world import FIRST_PERSON_ID, FIRST_THING_ID, REPO, BANKS, World

DAY = 86400
SEEN_AT_LEAST = 200     # pixels, in a 960 x 720 picture, for a thing to count as seen
HARD_TO_MAKE_OUT = 0.35  # less than this share of its pixels differs in brightness from the surroundings
DARK = 0.16              # brightness, 0 to 1, below which a thing on a dark ground is lost
IN_PART = 0.15           # its pixels as a share of the outline of its box; below this only part shows
PERSON_IN_THE_WAY = 0.12  # share of the picture a person within 1.3 m may fill before the camera steps aside
PICTURE = (800, 600)    # what is saved; the counting is done at 960 x 720


class Scene:
    def __init__(self, binding_name: str = "rendered_look.binding_hh_s151") -> None:
        self.binding = importlib.import_module(binding_name)
        self.out = REPO / "results/rendered_look" / self.binding.HOUSEHOLD.split("_t")[0]
        self.out.mkdir(parents=True, exist_ok=True)
        self.bank = timeline.Bank(BANKS / f"{self.binding.HOUSEHOLD}.jsonl")
        self.world = World(self.binding)
        self.world.find_surfaces(self.bank.rooms)
        given = json.load((REPO / "results/rendered_look/asked_about_models/"
                           "which_model_each_object_gets.json").open())[self.binding.HOUSEHOLD]
        self.world.add_things(given)
        self.stays = timeline.Stays(self.bank, self.world)
        self.people = people_module.People(self.world, self.bank)
        self.views = self._views()
        self.people.stand_only_where_a_camera_sees([v for v in self.views if v["kind"] == "whole room"])
        self.by_id = {f["semantic_id"]: o for o, f in self.world.thing_facts.items()}
        self.person_by_id = {i: r for r, i in self.people.ids.items()}

    def middles(self) -> Dict[str, tuple]:
        return {place: (float(s.xz[:, 0].mean()), float(s.height), float(s.xz[:, 1].mean()))
                for place, s in self.world.surfaces.items()}

    def _views(self) -> List[dict]:
        path = self.out / "views.json"
        if path.exists():
            return json.load(path.open())
        middles, found = self.middles(), []
        used = {s["place"] for stays in self.stays.stays.values() for s in stays if s.get("shown")}
        for room in self.binding.ROOMS:
            here = {p: m for p, m in middles.items() if self.bank.rooms[p] == room}
            found += views.whole_room_views(self.world, room, here)
            for place, middle in here.items():
                if place in used:
                    view = views.close_view(self.world, room, place, middle)
                    if view:
                        found.append(view)
                    else:
                        print(f"no camera position gives a clear view of {place}")
        path.write_text(json.dumps(found, indent=1))
        return found

    def set_moment(self, day: int, clock: str) -> dict:
        hours, minutes = clock.split(":")
        t = day * DAY + int(hours) * 3600 + int(minutes) * 60
        things = {}
        for object_id in self.bank.asked:
            stay = self.stays.at(object_id, t)
            facts = self.world.thing_facts[object_id]
            record = {"object_id": object_id, "class": facts["class"], "looks_like": facts["looks_like"]}
            if stay is None:
                record.update(shown=False, why_not_shown="the bank has no place for it yet", place=None)
                self.world.put_away(object_id)
            else:
                spec = self.binding.PLACES.get(stay["place"], {})
                record.update(place=stay["place"], room=self.bank.rooms.get(stay["place"]),
                              furniture=spec.get("called"), stand_in=spec.get("stand_in"),
                              since=stay["from"], shown=stay["shown"])
                if stay["shown"]:
                    record.update(x=stay["x"], y=stay["y"], z=stay["z"], yaw=stay["yaw"],
                                  crowded=stay["crowded"], overhangs=stay["overhangs"], on_top_of=None)
                else:
                    self.world.put_away(object_id)
                    record["why_not_shown"] = stay["why_not_shown"]
            things[object_id] = record
        # things that share a spot are piled in the order they arrived
        piles: Dict[tuple, List[dict]] = {}
        for record in things.values():
            if record.get("shown"):
                piles.setdefault((record["place"], round(record["x"], 3), round(record["z"], 3)), []).append(record)
        for pile in piles.values():
            pile.sort(key=lambda r: (r["since"], r["object_id"]))
            top = pile[0]["y"]
            for n, record in enumerate(pile):
                record["y"] = top
                record["on_top_of"] = pile[n - 1]["object_id"] if n else None
                self.world.put(record["object_id"], record["x"], top, record["z"], record.pop("yaw"))
                top += self.world.thing_facts[record["object_id"]]["height"]
        stage = self.bank.stage_of_day(day)
        cameras = [(v["eye"][0], v["eye"][2]) for v in self.views]
        lines = [((v["eye"][0], v["eye"][2]), (v["target"][0], v["target"][2]))
                 for v in self.views if v["kind"] == "one place"]
        residents = self.people.place_all(t, stage, cameras, lines)
        return {"day": day, "clock": clock, "t": t, "stage": stage, "things": things,
                "people": residents}

    def share_in_view(self, thing, pixels: int, shape) -> dict:
        """How the thing's pixels compare with the outline of its box as the
        camera would see it with nothing in the way and no edge to the picture."""
        import quaternion
        from scipy.spatial import ConvexHull
        from rendered_look import home
        from rendered_look.world import HFOV
        low, high = home.world_box(thing)
        corners = np.array([[x, y, z] for x in (low[0], high[0]) for y in (low[1], high[1])
                            for z in (low[2], high[2])])
        state = self.world.sim.get_agent(0).get_state()
        seen_from = (corners - np.asarray(state.position)) @ quaternion.as_rotation_matrix(state.rotation)
        if (seen_from[:, 2] > -0.05).any():
            return {"share_of_its_outline": 0.0, "cut_by_the_edge": True}
        focal = (shape[1] / 2) / np.tan(np.radians(HFOV) / 2)
        cols = shape[1] / 2 + focal * seen_from[:, 0] / -seen_from[:, 2]
        rows = shape[0] / 2 - focal * seen_from[:, 1] / -seen_from[:, 2]
        outline = ConvexHull(np.stack([cols, rows], axis=1)).volume   # area, for a flat hull
        outside = ((cols < 0) | (cols >= shape[1]) | (rows < 0) | (rows >= shape[0])).mean()
        return {"share_of_its_outline": round(float(pixels / max(outline, 1.0)), 3),
                "cut_by_the_edge": bool(outside >= 0.25)}

    def picture(self, view: dict, aim=None) -> dict:
        from scipy import ndimage
        stood_at, least = None, None
        for n, stand in enumerate([view] + view.get("otherwise", [])):
            stand = dict(stand, target=list(aim)) if aim is not None else stand
            shot = views.capture(self.world.sim, np.array(stand["eye"]), np.array(stand["target"]))
            in_the_way = float(((shot["ids"] >= FIRST_PERSON_ID) & (shot["depth"] < 1.3)).mean())
            if least is None or in_the_way < least[0]:
                least = (in_the_way, n, stand, shot)
            if in_the_way <= PERSON_IN_THE_WAY:
                break
        in_the_way, n, stand, shot = least
        stood_at = {"eye": stand["eye"], "target": stand["target"], "stepped_aside": n > 0,
                    "share_of_picture_a_person_blocks": round(in_the_way, 3)}
        ids = shot["ids"]
        home_look = __import__("rendered_look.home", fromlist=["look_from"])
        home_look.look_from(self.world.sim, stand["eye"], stand["target"])   # the pose share_in_view reads
        light = shot["colour"].astype(float) @ np.array([0.299, 0.587, 0.114]) / 255.0
        in_picture = []
        values, counts = np.unique(ids[ids >= FIRST_THING_ID], return_counts=True)
        for value, count in zip(values.tolist(), counts.tolist()):
            rows, cols = np.nonzero(ids == value)
            who = self.by_id.get(value) or self.person_by_id.get(value)
            own = ids == value
            around = ndimage.binary_dilation(own, iterations=8) & (ids < FIRST_THING_ID)
            # how far its brightness is from what surrounds it, 0 to 1; black on black is near 0
            # the share of its pixels whose brightness differs from what surrounds it;
            # black glasses on a black table score low even with one bright glint
            stands_out = (float((np.abs(light[own] - np.median(light[around])) > 0.12).mean())
                          if around.any() else 1.0)
            its_light = float(light[own].mean())
            light_around = float(np.median(light[around])) if around.any() else 1.0
            dark_on_dark = its_light < DARK and light_around < DARK * 1.6
            body = (self.world.things.get(who) if value < FIRST_PERSON_ID
                    else self.people.in_use.get(who))
            whole = self.share_in_view(body, count, ids.shape) if body is not None else {}
            in_part = bool(whole and (whole["share_of_its_outline"] < IN_PART or whole["cut_by_the_edge"]))
            in_picture.append({
                "what": who, "is_person": value >= FIRST_PERSON_ID, "pixels": count,
                "seen": count >= SEEN_AT_LEAST,
                "stands_out": round(stands_out, 3),
                "brightness": round(its_light, 3), "brightness_around": round(light_around, 3),
                "hard_to_make_out": bool(stands_out < HARD_TO_MAKE_OUT or dark_on_dark),
                "only_part_shows": in_part, **whole,
                "box": [round(cols.min() / ids.shape[1], 4), round(rows.min() / ids.shape[0], 4),
                        round((cols.max() + 1) / ids.shape[1], 4), round((rows.max() + 1) / ids.shape[0], 4)],
                "metres_away": round(float(np.median(shot["depth"][ids == value])), 2)})
        return {"colour": shot["colour"], "in_picture": in_picture, "stood_at": stood_at}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, nargs="+", required=True)
    parser.add_argument("--times", nargs="+", required=True)
    parser.add_argument("--every-view", action="store_true",
                        help="also render close views of places with nothing on them")
    args = parser.parse_args()
    scene = Scene()
    frames = scene.out / "frames"
    frames.mkdir(exist_ok=True)
    moments = []
    for day in args.days:
        for clock in args.times:
            moment = scene.set_moment(day, clock)
            occupied = {t["place"] for t in moment["things"].values() if t.get("shown")}
            moment["views"] = []
            for view in scene.views:
                if view["kind"] == "one place" and view["place"] not in occupied and not args.every_view:
                    continue
                aim = None
                if view["kind"] == "one place":   # look at the things, not at the middle of the furniture
                    there = [t for t in moment["things"].values() if t.get("shown") and t["place"] == view["place"]]
                    if there:
                        aim = np.mean([[t["x"], t["y"] + 0.05, t["z"]] for t in there], axis=0)
                result = scene.picture(view, aim)
                # the same things at the same spots in the same view give the same picture
                said = json.dumps([view["name"], result["stood_at"]["eye"]] + sorted(
                    (p["what"], p["pixels"], p["box"]) for p in result["in_picture"]))
                name = view["name"] + "_" + hashlib.sha1(said.encode()).hexdigest()[:10] + ".jpg"
                if not (frames / name).exists():
                    Image.fromarray(result["colour"]).resize(PICTURE, Image.LANCZOS).save(
                        frames / name, quality=78)
                moment["views"].append({"view": view["name"], "file": name,
                                        "in_picture": result["in_picture"], **result["stood_at"]})
            moments.append(moment)
            seen = {p["what"] for v in moment["views"] for p in v["in_picture"] if p["seen"]}
            print(f"day {day} {clock} [{moment['stage']}]: {len(moment['views'])} pictures, "
                  f"{len(seen)} things and people seen")
    (scene.out / "moments.json").write_text(json.dumps(moments))
    scene.world.close()


if __name__ == "__main__":
    main()
