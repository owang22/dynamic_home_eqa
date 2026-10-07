"""Where the robot's camera stands in each room, and what one picture shows."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from rendered_look import home

import os

# Metres above the floor. 1.3 is about the head camera of a Stretch robot; a
# quadruped's camera is far lower. Set RENDERED_LOOK_EYE to render from another height.
EYE = float(os.environ.get("RENDERED_LOOK_EYE", "1.3"))
# A tall camera looks a little down to take in a room; a low one looks level.
WHOLE_ROOM_LOOK = -0.35 if EYE >= 1.0 else 0.0
LENS = float(os.environ.get("RENDERED_LOOK_LENS", "75"))


def capture(sim, eye, target) -> dict:
    home.look_from(sim, eye, target)
    seen = sim.get_sensor_observations()
    return {"colour": seen["colour"][:, :, :3].copy(), "ids": seen["ids"].copy(),
            "depth": seen["depth"].copy()}


def world_points(sim, depth: np.ndarray, hfov: Optional[float] = None) -> np.ndarray:
    hfov = LENS if hfov is None else hfov
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
            target = eye + np.array([np.cos(heading), WHOLE_ROOM_LOOK, np.sin(heading)])
            shot = capture(world.sim, eye, target)
            points = world_points(world.sim, shot["depth"])
            # Something close to the camera blocks the view; the floor does not. A low camera
            # looking level has the floor within 0.7 m in over 12% of the picture, and this
            # rule used to reject every whole-room position at 0.30 m because of it.
            if float(((shot["depth"] < CROWDED_BY) & (points[..., 1] > floor + 0.08)).mean()) > 0.12:
                continue
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


def lines_of_sight(sim, depth: np.ndarray, points: np.ndarray, hfov: Optional[float] = None) -> np.ndarray:
    """For each world point: is it inside the picture with nothing in front of it?"""
    hfov = LENS if hfov is None else hfov
    import quaternion
    height, width = depth.shape
    focal = (width / 2) / np.tan(np.radians(hfov) / 2)
    state = sim.get_agent(0).get_state()
    seen_from = (points - np.asarray(state.position)) @ quaternion.as_rotation_matrix(state.rotation)
    ahead = -seen_from[:, 2]
    clear = np.zeros(len(points), dtype=bool)
    for i in np.flatnonzero(ahead > 0.15):
        col = int(width / 2 + focal * seen_from[i, 0] / ahead[i])
        row = int(height / 2 - focal * seen_from[i, 1] / ahead[i])
        if 20 <= col < width - 20 and 20 <= row < height - 20:
            clear[i] = depth[row, col] >= ahead[i] - 0.05   # the depth picture is distance along the view
    return clear


OTHER_POSITIONS = int(os.environ.get("RENDERED_LOOK_OTHER_POSITIONS", "3"))
LOW, TALL = 0.04, 0.12   # metres above the surface: the top of a flat thing, the top of a small upright one


def close_view(world, room: str, place: str, middle: Tuple[float, float, float],
               spots: Optional[np.ndarray] = None) -> Optional[dict]:
    """Where to stand so that a thing resting on this place would show.

    The same rule at every camera height: over a spread of spots on the
    surface, count how many have a clear line to a point 4 cm and 12 cm above
    them. A tall camera sees the surface itself; a low one sees only what
    sticks up above the edge, and sees it best from further back.
    """
    region = world.regions[world.binding.ROOMS[room]]
    floor = float(region["floor_height"])
    if spots is None or not len(spots):
        spots = np.array([[middle[0], middle[2]]])
    marks = np.array([[x, middle[1] + lift, z] for x, z in spots for lift in (LOW, TALL)])
    every, tried = [], 0
    for distance in (0.8, 1.1, 1.4, 1.9, 2.5, 3.2):
        for bearing in np.arange(0, 2 * np.pi, np.pi / 8):
            x = middle[0] + distance * np.cos(bearing)
            z = middle[2] + distance * np.sin(bearing)
            if not world.sim.pathfinder.is_navigable(np.array([x, floor, z], dtype=np.float32), 0.3):
                continue
            if not home.inside(x, z, region["poly_loop"]):
                continue
            eye = np.array([x, floor + EYE, z])
            aim = np.array(middle) + np.array([0.0, (LOW + TALL) / 2, 0.0])
            shot = capture(world.sim, eye, aim)
            clear = lines_of_sight(world.sim, shot["depth"], marks)
            tried += 1
            low, tall = float(clear[0::2].mean()), float(clear[1::2].mean())
            if tall <= 0:
                continue
            steep = abs(np.degrees(np.arctan2(EYE + floor - middle[1], distance)))
            worth = ((0.6 * low + 0.4 * tall) / (0.6 + distance)
                     * (1.0 - min(1.0, 3 * blocked_share(shot["depth"])))
                     * (1.0 if steep <= 40 else (40.0 / steep) ** 2))
            every.append({"eye": eye.tolist(), "target": aim.tolist(), "score": worth,
                          "share_of_spots_a_flat_thing_shows": round(low, 2),
                          "share_of_spots_an_upright_thing_shows": round(tall, 2),
                          "metres_back": distance})
    if not every:
        print(f"{place}: {tried} camera positions tried; from none would a thing on it show")
        return None
    every.sort(key=lambda c: -c["score"])
    best = every[0]
    best["otherwise"], used = [], [best["eye"]]
    for c in every[1:]:
        if all(np.hypot(c["eye"][0] - u[0], c["eye"][2] - u[2]) >= 0.6 for u in used):
            best["otherwise"].append({"eye": c["eye"], "target": c["target"]})
            used.append(c["eye"])
        if len(best["otherwise"]) == OTHER_POSITIONS:
            break
    best.update(name=f"{room}_{place}", room=room, kind="one place", place=place)
    return best
