"""The residents as figures in the home: which pose, where, facing which way."""
from __future__ import annotations

import csv
from typing import Dict, List

import numpy as np

from rendered_look import home
from rendered_look.world import FIRST_PERSON_ID, steady_number

DAY = 86400


def figure_meshes(binding) -> Dict[str, Dict[str, str]]:
    by_name = {}
    with (home.HSSD / "semantics/objects.csv").open() as handle:
        for row in csv.DictReader(handle):
            if row["main_category"] == "person":
                by_name.setdefault(row["name"].strip(), row["id"])
    out = {}
    for resident, person in binding.PEOPLE.items():
        out[resident] = {pose: str(home.HSSD / "objects" / by_name[name][0] / f"{by_name[name]}.glb")
                         for pose, name in person["poses"].items()}
    return out


def _metres_from_line(point, start, end) -> float:
    p, a, b = np.array(point), np.array(start), np.array(end)
    along = np.clip(np.dot(p - a, b - a) / max(np.dot(b - a, b - a), 1e-9), 0.0, 1.0)
    return float(np.linalg.norm(p - (a + along * (b - a))))


class People:
    def __init__(self, world, bank) -> None:
        import magnum as mn
        self.world, self.bank = world, bank
        self.figures: Dict[str, Dict[str, object]] = {}
        self.boxes: Dict[str, Dict[str, tuple]] = {}
        self.ids: Dict[str, int] = {}
        for n, (resident, poses) in enumerate(sorted(figure_meshes(world.binding).items())):
            self.ids[resident] = FIRST_PERSON_ID + n
            self.figures[resident], self.boxes[resident] = {}, {}
            for pose, mesh in poses.items():
                figure = world.add_model(mesh, 1.0, FIRST_PERSON_ID + n)
                box = figure.root_scene_node.cumulative_bb
                self.figures[resident][pose] = figure
                self.boxes[resident][pose] = (np.array(box.min), np.array(box.max))
                figure.translation = mn.Vector3(0, -80 - 3 * n - len(self.figures[resident]), 0)
        self.standing_spots = {room: self._standing_spots(region)
                               for room, region in ((r, world.regions[name])
                                                    for r, name in world.binding.ROOMS.items())}

    def _standing_spots(self, region: dict) -> List[tuple]:
        xs = [p[0] for p in region["poly_loop"]]
        zs = [p[2] for p in region["poly_loop"]]
        spots = []
        for x in np.arange(min(xs) + 0.3, max(xs), 0.3):
            for z in np.arange(min(zs) + 0.3, max(zs), 0.3):
                point = np.array([x, region["floor_height"], z], dtype=np.float32)
                if (home.inside(x, z, region["poly_loop"]) and
                        self.world.sim.pathfinder.is_navigable(point, 0.3) and
                        self.world.sim.pathfinder.distance_to_closest_obstacle(point, 1.0) >= 0.2):
                    spots.append((float(x), float(z)))
        return spots

    def pose_for(self, resident: str, room: str, t: int, stage: str) -> str:
        hour = (t % DAY) / 3600.0
        own_bedroom = next(p["bedroom"] for p in self.bank.header["protocol"]["residents"]
                           if p["resident_id"] == resident)
        if room == own_bedroom and (hour >= 22.5 or hour < 7.0):
            return "lying"
        unwell = "sick" in stage and resident == "resident_1"
        if unwell and room == own_bedroom:
            return "lying"
        return "walking" if steady_number("pose", resident, t) < 0.3 else "standing"

    def stand_only_where_a_camera_sees(self, whole_room_views: List[dict]) -> None:
        """Keeps, in each room, the standing spots where a person's chest would
        show in one of that room's whole-room pictures. Without this a resident
        can be in the room and in none of its pictures."""
        import quaternion
        from rendered_look import views
        for room, spots in self.standing_spots.items():
            seen = np.zeros(len(spots), dtype=bool)
            floor = float(self.world.regions[self.world.binding.ROOMS[room]]["floor_height"])
            for view in whole_room_views:
                if view["room"] != room or not len(spots):
                    continue
                shot = views.capture(self.world.sim, np.array(view["eye"]), np.array(view["target"]))
                depth = shot["depth"]
                height, width = depth.shape
                focal = (width / 2) / np.tan(np.radians(75.0) / 2)
                state = self.world.sim.get_agent(0).get_state()
                turn = quaternion.as_rotation_matrix(state.rotation)
                for i, (x, z) in enumerate(spots):
                    chest = (np.array([x, floor + 1.1, z]) - np.asarray(state.position)) @ turn
                    if chest[2] > -0.6:      # behind the camera, or too close to it
                        continue
                    col = int(width / 2 + focal * chest[0] / -chest[2])
                    row = int(height / 2 - focal * chest[1] / -chest[2])
                    if 40 <= col < width - 40 and 40 <= row < height - 40:
                        seen[i] |= bool(depth[row, col] >= -chest[2] - 0.35)
            print(f"{room}: a person would show at {int(seen.sum())} of {len(spots)} standing spots")
            if seen.sum() >= 1:
                self.standing_spots[room] = [s for s, ok in zip(spots, seen) if ok]

    def place_all(self, t: int, stage: str, keep_clear: List[tuple],
                  sight_lines: List[tuple] = ()) -> List[dict]:
        """Puts every resident where the bank says. keep_clear: (x, z) of camera
        positions nobody should stand on."""
        import magnum as mn
        shown, taken = [], list(keep_clear)
        self.in_use = {}
        for n, resident in enumerate(sorted(self.figures)):
            for k, figure in enumerate(self.figures[resident].values()):
                figure.translation = mn.Vector3(0, -80 - 3 * n - k, 0)
            row = self.bank.room_of_resident(resident, t)
            name = self.world.binding.PEOPLE[resident]["name"]
            fact = {"resident": resident, "name": name, "room": row["room"], "since": row["t"],
                    "looks_like": self.world.binding.PEOPLE[resident]["looks_like"],
                    "semantic_id": self.ids[resident]}
            if row["room"] not in self.world.binding.ROOMS:
                fact.update(shown=False, why_not_shown="out of the house" if row["room"] == "AWAY"
                            else f"in a room this home does not have ({row['room']})")
                shown.append(fact)
                continue
            pose = self.pose_for(resident, row["room"], t, stage)
            figure = self.figures[resident][pose]
            person = self.world.binding.PEOPLE[resident]
            if pose == "lying":
                bed_place = "bed_b1" if row["room"] == "bedroom_1" else "bed_b2"
                spec = self.world.binding.PLACES[bed_place]
                surface = self.world.surfaces[bed_place]
                head = np.array(spec["head_toward"], dtype=float)
                across = np.array([-head[1], head[0]])
                bed_low, bed_high = home.world_box(self.world.furniture_for(bed_place))
                middle = np.array([(bed_low[0] + bed_high[0]) / 2, (bed_low[2] + bed_high[2]) / 2])
                x, z = middle + across * 0.38 - head * 0.12
                y = surface.usual_height_under(x, z, 0.35) - 0.02 - person["lying_sinks"]
                # the head of a figure laid on its back points along -z before it is turned
                yaw = float(np.arctan2(-head[0], -head[1]))
                turn = mn.Quaternion.rotation(mn.Rad(yaw), mn.Vector3(0, 1, 0))
                if person["lying_is"] == "standing figure laid on its back":
                    turn = turn * mn.Quaternion.rotation(mn.Rad(-np.pi / 2), mn.Vector3(1, 0, 0))
            else:
                def room_to_spare(s):
                    return min([np.hypot(s[0] - c[0], s[1] - c[1]) for c in taken] +
                               [2 * _metres_from_line(s, a, b) for a, b in sight_lines] + [9.0])
                ranked = sorted(self.standing_spots[row["room"]], key=room_to_spare, reverse=True)
                spots = ranked[:max(1, len(ranked) // 4)]
                x, z = spots[int(steady_number("spot", resident, row["t"]) * len(spots))]
                y = float(self.world.regions[self.world.binding.ROOMS[row["room"]]]["floor_height"])
                outline = np.array(self.world.regions[self.world.binding.ROOMS[row["room"]]]["poly_loop"])
                middle = outline[:, [0, 2]].mean(axis=0)
                # the figures face +z before they are turned; turn them to face the middle of the room
                yaw = float(np.arctan2(middle[0] - x, middle[1] - z)) + (steady_number("face", resident, row["t"]) - 0.5)
                turn = mn.Quaternion.rotation(mn.Rad(yaw), mn.Vector3(0, 1, 0))
            taken.append((x, z))
            self.world.rest(figure, turn, x, y, z)
            self.in_use[resident] = figure
            fact.update(shown=True, pose=pose, x=float(x), y=float(y), z=float(z), yaw=float(yaw))
            shown.append(fact)
        return shown
