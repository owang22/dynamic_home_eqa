"""Where the robot's camera stands in each room, and what one picture shows."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from rendered_look import home

EYE = 1.3  # metres above the floor; about the head camera of a Stretch robot


def capture(sim, eye, target) -> dict:
    home.look_from(sim, eye, target)
    seen = sim.get_sensor_observations()
    return {"colour": seen["colour"][:, :, :3].copy(), "ids": seen["ids"].copy(),
            "depth": seen["depth"].copy()}


def world_points(sim, depth: np.ndarray, hfov: float = 75.0) -> np.ndarray:
    import quaternion
    height, width = depth.shape
    focal = (width / 2) / np.tan(np.radians(hfov) / 2)
    cols, rows = np.meshgrid(np.arange(width) - width / 2 + 0.5, np.arange(height) - height / 2 + 0.5)
    state = sim.get_agent(0).get_state()
    turn = quaternion.as_rotation_matrix(state.rotation)
    rays = np.stack([cols / focal, -rows / focal, -np.ones_like(cols)], axis=-1)
    return np.asarray(state.position) + (rays * depth[..., None]) @ turn.T


def standing_points(sim, region: dict, step: float, clear: float = 0.3) -> List[Tuple[float, float]]:
    xs = [p[0] for p in region["poly_loop"]]
    zs = [p[2] for p in region["poly_loop"]]
    out = []
    for x in np.arange(min(xs) + 0.2, max(xs), step):
        for z in np.arange(min(zs) + 0.2, max(zs), step):
            point = np.array([x, region["floor_height"], z], dtype=np.float32)
            if (home.inside(x, z, region["poly_loop"]) and sim.pathfinder.is_navigable(point, 0.3)
                    and sim.pathfinder.distance_to_closest_obstacle(point, 1.0) >= clear):
                out.append((float(x), float(z)))
    if len(out) < 6 and clear > 0.11:   # a room crowded with furniture: stand closer to it
        return standing_points(sim, region, step * 0.7, clear - 0.1)
    return out


CROWDED_BY = 0.7   # metres; a picture mostly filled by something this close shows little


def blocked_share(depth: np.ndarray) -> float:
    return float((depth < CROWDED_BY).mean())


def whole_room_views(world, room: str, targets: Dict[str, Tuple[float, float, float]],
                     how_many: int = 2) -> List[dict]:
    """The few camera positions from which most of the room's places can be seen.

    targets: place -> the middle of its surface (x, y, z). A place counts as in
    view when the point drawn at its pixel is within 25 cm of that middle."""
    region = world.regions[world.binding.ROOMS[room]]
    floor = float(region["floor_height"])
    candidates = []
    for x, z in standing_points(world.sim, region, 0.5):
        for heading in np.arange(0, 2 * np.pi, np.pi / 6):
            eye = np.array([x, floor + EYE, z])
            target = eye + np.array([np.cos(heading), -0.35, np.sin(heading)])
            shot = capture(world.sim, eye, target)
            if blocked_share(shot["depth"]) > 0.12:
                continue
            points = world_points(world.sim, shot["depth"])
            in_view = {}
            for place, middle in targets.items():
                near = np.linalg.norm(points - np.array(middle), axis=-1) < 0.25
                if near.sum() >= 150:
                    in_view[place] = int(near.sum())
            inside_room = np.array([home.inside(px, pz, region["poly_loop"]) for px, pz in
                                    points[::24, ::24, [0, 2]].reshape(-1, 2)]).mean()
            candidates.append({"eye": eye.tolist(), "target": target.tolist(), "places": in_view,
                               "share_of_picture_in_the_room": round(float(inside_room), 3)})
    chosen, covered = [], set()
    for _ in range(how_many):
        def worth(c):
            apart = min([np.hypot(c["eye"][0] - o["eye"][0], c["eye"][2] - o["eye"][2])
                         for o in chosen], default=9.0)
            return (len(set(c["places"]) - covered), apart >= 1.0,
                    len(c["places"]), c["share_of_picture_in_the_room"])
        best = max(candidates, default=None, key=worth)
        if best is None:
            break
        candidates.remove(best)
        chosen.append(best)
        covered |= set(best["places"])
    for view in chosen:   # where else to stand for much the same picture, if someone is in the way
        others = sorted((c for c in candidates
                         if 0.8 <= np.hypot(c["eye"][0] - view["eye"][0], c["eye"][2] - view["eye"][2])
                         and set(c["places"]) >= set(list(view["places"])[:1])),
                        key=lambda c: (-len(set(c["places"]) & set(view["places"])),
                                       -c["share_of_picture_in_the_room"]))
        view["otherwise"], used = [], [view["eye"]]
        for c in others:
            if all(np.hypot(c["eye"][0] - u[0], c["eye"][2] - u[2]) >= 0.8 for u in used):
                view["otherwise"].append({"eye": c["eye"], "target": c["target"]})
                used.append(c["eye"])
            if len(view["otherwise"]) == 3:
                break
    for n, view in enumerate(chosen):
        view.update(name=f"{room}_whole_{n + 1}", room=room, kind="whole room")
    return chosen


def close_view(world, room: str, place: str, middle: Tuple[float, float, float]) -> Optional[dict]:
    """The camera position from which the most of one place's surface is seen."""
    floor = float(world.regions[world.binding.ROOMS[room]]["floor_height"])
    best, tried, every = None, 0, []
    for distance in (0.8, 1.1, 1.4, 1.9, 2.5):
        for bearing in np.arange(0, 2 * np.pi, np.pi / 8):
            x = middle[0] + distance * np.cos(bearing)
            z = middle[2] + distance * np.sin(bearing)
            point = np.array([x, floor, z], dtype=np.float32)
            if not world.sim.pathfinder.is_navigable(point, 0.3):
                continue
            if not home.inside(x, z, world.regions[world.binding.ROOMS[room]]["poly_loop"]):
                continue
            eye = np.array([x, floor + EYE, z])
            shot = capture(world.sim, eye, middle)
            points = world_points(world.sim, shot["depth"])
            flat = np.hypot(points[..., 0] - middle[0], points[..., 2] - middle[2]) < 0.4
            level = np.abs(points[..., 1] - middle[1]) < 0.06
            shown = int((flat & level).sum())
            steep = np.degrees(np.arctan2(EYE + floor - middle[1], distance))
            score = int(shown * distance ** 2 / (1 + 0.3 * distance)
                        * (1.0 - min(1.0, 3 * blocked_share(shot["depth"])))
                        * (1.0 if steep <= 40 else (40.0 / steep) ** 2))
            if shown < 120:
                score = 0
            tried += 1
            if score > 0:
                every.append({"eye": eye.tolist(), "target": list(middle), "score": score})
            if best is None or score > best["score"]:
                best = {"eye": eye.tolist(), "target": list(middle), "score": score, "pixels_of_the_surface": shown}
    if best is None or best["score"] < 120:
        print(f"{place}: {tried} camera positions tried, best shows "
              f"{best['score'] if best else 0} pixels of the surface")
        return None
    best["otherwise"], used = [], [best["eye"]]
    for c in sorted(every, key=lambda c: -c["score"]):
        if all(np.hypot(c["eye"][0] - u[0], c["eye"][2] - u[2]) >= 0.6 for u in used):
            best["otherwise"].append({"eye": c["eye"], "target": c["target"]})
            used.append(c["eye"])
        if len(best["otherwise"]) == 3:
            break
    best.update(name=f"{room}_{place}", room=room, kind="one place", place=place)
    return best
