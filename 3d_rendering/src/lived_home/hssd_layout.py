"""Read one HSSD home from disk: its rooms, its furniture and the places small objects can go.

Files only: no habitat-sim, no GPU. Uses the ARTICULATED scenes of hssd-hab
(scenes-articulated/*.scene_instance.json), so cabinets, drawers, fridges and ovens are
URDF assets whose drawers and doors are real links.

What each part comes from
-------------------------
rooms      semantics/scenes/<scene>.semantic_config.json "region_annotations"
           (poly_loop = [[x, floor_y, z], ...], floor_height, extrusion_height).
furniture  scene "object_instances" (rigid) and "articulated_object_instances" (URDF).
           Every articulated object counts. A rigid object counts when it is not
           pickable (metadata/hssd_obj_semantics_condensed.csv) and is not decoration
           (GEOMETRY_SKIP) unless it is a landmark (tv, fridge, ...). Object configs
           are found at any depth under objects/ (decomposed sets such as a dining
           table and its chairs sit in objects/decomposed/<set>/).
           Instances parked outside the house (more than 1 m from every room, or above
           or below every storey) are dropped and listed in notes.furniture_dropped.
           Category: the condensed csv's primary column, else semantics/objects.csv.
           "instance_index" indexes the list named by "instance_list".
spots      the "receptacle_mesh_*" entries in each asset's user_defined config
           (objects/*/<id>.object_config.json for rigid, urdf/<id>/<id>.ao_config.json
           for articulated, where each receptacle names its parent URDF link).
           World placement follows habitat-lab's receptacle code
           (habitat/datasets/rearrange/samplers/receptacle.py): the glTF node
           transforms inside the receptacle .glb are applied, then the parent's
           transform -- for rigid objects translation * rotation * scale, for
           articulated objects translation * rotation * uniform_scale * the link's pose
           from forward kinematics through the URDF joints at joint value 0 (closed).
           Each receptacle is split into one spot per horizontal level; fragments of a
           rigid object's receptacle file (unnamed, e.g. 18 cushion pieces of one sofa)
           are pooled first. Levels under 0.02 m2, above 2.1 m or below the floor
           are dropped.
           scene_filter_files/articulated_scene_filter_files/<scene>.rec_filter.json says
           which receptacles the PARTNR robot benchmark switched off; that status is
           copied into each spot ("hssd_filter"). Spots a human annotator removed
           ("manually_filtered") or that failed physics placement ("stability_filtered")
           are dropped by default; "access_filtered" (PARTNR keeps one drawer per
           cabinet active) and "height_filtered" (above a robot's 1.2 m reach) are kept.
geometry   spots HSSD's receptacle meshes leave out, read from the objects' own render
           meshes (source "geometry", with "geometry_from" naming the mesh): every spot
           of a non-pickable rigid object with no receptacle mesh (not decoration, and a
           chair only when it is its room's one seat); every spot of an articulated
           asset whose ao_config has no usable receptacle (each drawer link -> a closed
           spot); the basin of a sink or tub with no open spot (an HSSD receptacle at
           the same place is relabelled instead of duplicated); a basin at a tap that
           stands on a worktop; a washing-machine drum; a sofa seat HSSD left out.
           See the "spots from render geometry" section for the method.
floors     one spot per room, at the floor height, centred inside the polygon.

Not in HSSD, and approximated here:
  * whether a receptacle is behind a door: a receptacle on a moving link (drawer, door
    shelf, oven rack) is "closed"; one on a fixed link is "closed" when horizontal rays
    from just above it hit the asset's collision boxes in all eight directions and the
    first hit in at least one direction is a moving link (see _behind_door). Checked
    against HSSD's within_set (receptacles PARTNR says need a link opened): 95% agree.
  * "open" containers (sinks, bins, baskets, bathtubs): receptacle names and categories.
  * shelf levels within one receptacle: clustered from triangle heights.
  * room of a piece of furniture: the smallest region polygon on the right storey that
    contains the area-weighted centre of its receptacles (or its origin), else the
    nearest one; a spot keeps its furniture's room when within 0.25 m of it.
  * kitchen sink and cooker: categories and names of objects in the kitchen.

Coordinates are habitat world coordinates: y up, metres.
"""
from __future__ import annotations

import csv
import functools
import json
import math
import os
import pathlib
import re
import struct
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

HSSD = pathlib.Path(os.environ.get(
    "HSSD_DIR", "/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab"))
DATASET_NAME = "hssd-hab articulated"
REPO_RESULTS = pathlib.Path(__file__).resolve().parents[2] / "results"

# ---------------------------------------------------------------- tunable constants
MIN_SPOT_AREA = 0.02        # m^2: smaller horizontal pieces are not spots
LEVEL_GAP = 0.05            # m: triangles whose heights differ by more are separate levels
HORIZONTAL_NY = 0.9         # |normal.y| above this counts as a horizontal triangle
ROOM_MARGIN = 0.25          # m: a point this close outside a polygon still counts as inside
MAX_ROOM_DISTANCE = 1.0     # m: furniture farther than this from every room is dropped
MAX_SPOT_HEIGHT = 2.1       # m above the floor: higher surfaces (tops of tall wall
                            # cabinets at 2.7-3 m) are out of a person's reach
DROP_FILTERS = ("manually_filtered", "stability_filtered")

OPEN_CATEGORIES = {
    "sink", "bath_sink", "washbasin", "basin", "sink/basin", "toilet_sink", "bathtub",
    "basket", "laundry_basket", "trash_bin", "bin", "storage_bin", "box", "storage_box",
    "container", "crate", "towel_basket", "newspaper_basket", "laundry_bag",
}
OPEN_NAME_WORDS = ("sink", "basin", "bin", "basket", "tub", "bowl")
SINK_CATEGORIES = {"sink", "sink_cabinet", "kitchen_sink", "sink/basin", "washbasin",
                   "bath_sink", "basin", "sink_table"}
STOVE_CATEGORIES = {"stove", "oven", "cooker", "oven_and_stove", "stovetop", "cooker_unit",
                    "range", "cooktop"}
STOVE_NAME_WORDS = ("stove", "cooktop", "hob", "burner")

# rigid objects kept as furniture even when HSSD gives them no receptacle
LANDMARK_CATEGORIES = SINK_CATEGORIES | STOVE_CATEGORIES | {
    "fridge", "refrigerator", "mini_fridge", "freezer", "dishwasher", "microwave",
    "toilet", "bathtub", "shower", "shower_cabin", "washing_machine", "washer/dryer",
    "washer_dryer", "tv", "led_tv", "wall_tv", "piano", "fireplace", "counter",
    "kitchen_counter", "kitchen_island", "bed", "couch", "sofa"}

ROOM_TYPES = {
    "kitchen": {"kitchen"},
    "bedroom": {"bedroom"},
    "bathroom": {"bathroom"},
    "toilet": {"toilet"},
    "living": {"living room", "tv", "lounge", "familyroom"},
}


# ================================================================== small readers
def _read_glb_json_bin(path: pathlib.Path) -> Tuple[dict, bytes]:
    data = path.read_bytes()
    magic, _version, _length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise ValueError(f"{path} is not a binary glTF file")
    offset, doc, binary = 12, None, b""
    while offset < len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8: offset + 8 + chunk_len]
        if chunk_type == 0x4E4F534A:
            doc = json.loads(chunk.decode("utf-8"))
        elif chunk_type == 0x004E4942:
            binary = chunk
        offset += 8 + chunk_len
    if doc is None:
        raise ValueError(f"{path} has no JSON chunk")
    return doc, binary


_COMPONENT = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2),
              5125: ("I", 4), 5126: ("f", 4)}
_WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def _accessor(doc: dict, binary: bytes, index: int) -> np.ndarray:
    acc = doc["accessors"][index]
    if "sparse" in acc:
        raise NotImplementedError("sparse glTF accessors are not supported")
    fmt, size = _COMPONENT[acc["componentType"]]
    width = _WIDTH[acc["type"]]
    count = acc["count"]
    view = doc["bufferViews"][acc["bufferView"]]
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = view.get("byteStride") or size * width
    dtype = np.dtype("<" + fmt)
    if stride == size * width:
        out = np.frombuffer(binary, dtype=dtype, count=count * width, offset=start)
        return out.reshape(count, width) if width > 1 else out.copy()
    rows = [np.frombuffer(binary, dtype=dtype, count=width, offset=start + i * stride)
            for i in range(count)]
    out = np.stack(rows)
    return out if width > 1 else out[:, 0]


def _node_matrix(node: dict) -> np.ndarray:
    if "matrix" in node:
        return np.array(node["matrix"], dtype=float).reshape(4, 4).T  # column-major
    m = np.eye(4)
    if "scale" in node:
        m = np.diag(list(node["scale"]) + [1.0]) @ m
    if "rotation" in node:
        x, y, z, w = node["rotation"]  # glTF order
        m = _quat_matrix(w, x, y, z) @ m
    if "translation" in node:
        t = np.eye(4)
        t[:3, 3] = node["translation"]
        m = t @ m
    return m


def read_glb_meshes(path: pathlib.Path) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Triangle meshes of a .glb as [(vertices (n,3), faces (m,3))], node transforms applied.

    Order and transforms follow habitat-lab's import_tri_mesh: one entry per (node, mesh
    primitive) of the default scene, nodes in index order, each with its absolute
    transform. That order gives the ".0000", ".0001" suffix of habitat receptacle names.
    """
    doc, binary = _read_glb_json_bin(path)
    nodes = doc.get("nodes", [])
    parent = {}
    for i, node in enumerate(nodes):
        for child in node.get("children", []):
            parent[child] = i
    scenes = doc.get("scenes")
    if scenes:
        scene = scenes[doc.get("scene", 0)]
        reachable, stack = set(), list(scene.get("nodes", []))
        while stack:
            n = stack.pop()
            if n in reachable:
                continue
            reachable.add(n)
            stack.extend(nodes[n].get("children", []))
    else:
        reachable = set(range(len(nodes)))

    @functools.lru_cache(maxsize=None)
    def world(n: int) -> np.ndarray:
        local = _node_matrix(nodes[n])
        return world(parent[n]) @ local if n in parent else local

    out = []
    items = [(n, nodes[n]["mesh"]) for n in sorted(reachable) if "mesh" in nodes[n]]
    if not nodes:  # meshes without a scene graph
        items = [(None, m) for m in range(len(doc.get("meshes", [])))]
    for n, mesh_index in items:
        matrix = world(n) if n is not None else np.eye(4)
        for prim in doc["meshes"][mesh_index]["primitives"]:
            mode = prim.get("mode", 4)
            verts = _accessor(doc, binary, prim["attributes"]["POSITION"]).astype(float)
            if "indices" in prim:
                idx = _accessor(doc, binary, prim["indices"]).astype(np.int64)
            else:
                idx = np.arange(len(verts))
            if mode == 4:
                faces = idx.reshape(-1, 3)
            elif mode == 5:  # strip
                faces = np.array([[idx[i], idx[i + 1], idx[i + 2]] if i % 2 == 0 else
                                  [idx[i + 1], idx[i], idx[i + 2]] for i in range(len(idx) - 2)])
            elif mode == 6:  # fan
                faces = np.array([[idx[0], idx[i], idx[i + 1]] for i in range(1, len(idx) - 1)])
            else:
                continue
            verts = verts @ matrix[:3, :3].T + matrix[:3, 3]
            faces = faces.reshape(-1, 3)
            if np.linalg.det(matrix[:3, :3]) < 0:  # a mirroring transform flips winding
                faces = faces[:, ::-1]
            out.append((verts, faces))
    return out


# ================================================================== transforms
def _quat_matrix(w: float, x: float, y: float, z: float) -> np.ndarray:
    n = math.sqrt(w * w + x * x + y * y + z * z) or 1.0
    w, x, y, z = w / n, x / n, y / n, z / n
    m = np.eye(4)
    m[:3, :3] = [
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ]
    return m


def _rpy_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr, cp, sp, cy, sy = (math.cos(roll), math.sin(roll), math.cos(pitch),
                              math.sin(pitch), math.cos(yaw), math.sin(yaw))
    rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    m = np.eye(4)
    m[:3, :3] = rz @ ry @ rx  # URDF fixed-axis roll, pitch, yaw
    return m


def instance_matrix(inst: dict, articulated: bool) -> np.ndarray:
    """World matrix of a scene instance. Habitat stores rotation as [w, x, y, z].

    Rigid: translation * rotation * non_uniform_scale (* uniform_scale).
    Articulated: translation * rotation * uniform_scale, translation taken as the URDF
    root-link origin. The articulated instances say translation_origin "COM", but their
    translations put cabinet bottoms on the floor (y ~ 0) and wall cabinets at 1.3 m,
    which is only true if they are root-link origins; the checks in the tests confirm it.
    """
    m = np.eye(4)
    m[:3, 3] = inst.get("translation", [0.0, 0.0, 0.0])
    if "rotation" in inst:
        m = m @ _quat_matrix(*inst["rotation"])
    scale = np.ones(3)
    if not articulated and "non_uniform_scale" in inst:
        scale = scale * np.array(inst["non_uniform_scale"], dtype=float)
    scale = scale * float(inst.get("uniform_scale", 1.0))
    return m @ np.diag(list(scale) + [1.0])


# ================================================================== metadata
@functools.lru_cache(maxsize=None)
def _semantics() -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    with (HSSD / "semantics/objects.csv").open() as handle:
        for row in csv.DictReader(handle):
            cat = row.get("main_category") or ""
            if not cat and row.get("wnsynsetkey"):
                cat = row["wnsynsetkey"].split(".")[0]
            out[row["id"]] = {"category": cat.strip().lower().replace(" ", "_"),
                              "name": row.get("name", ""), "pickable": None}
    with (HSSD / "metadata/hssd_obj_semantics_condensed.csv").open() as handle:
        rows = csv.reader(handle)
        next(rows)
        for row in rows:
            if len(row) < 5:
                continue
            entry = out.setdefault(row[0], {"category": "", "name": "", "pickable": None})
            primary = row[4].strip().lower()
            if primary and primary != "#n/a":
                entry["category"] = primary.replace(" ", "_")
            entry["pickable"] = {"Yes": True, "No": False}.get(row[2].strip())
    return out


def object_facts(template: str) -> dict:
    facts = dict(_semantics().get(template, {"category": "", "name": "", "pickable": None}))
    facts["category"] = facts["category"] or "unknown"
    return facts


@functools.lru_cache(maxsize=None)
def _object_config_index() -> Dict[str, pathlib.Path]:
    """Every rigid object config under objects/, at any depth. Decomposed furniture
    (objects/decomposed/<set>/<set>_part_N.object_config.json, e.g. the table and the
    chairs of one dining set) lives two levels down."""
    index: Dict[str, pathlib.Path] = {}
    for folder, _dirs, files in os.walk(HSSD / "objects"):
        for name in files:
            if name.endswith(".object_config.json"):
                index.setdefault(name[: -len(".object_config.json")], pathlib.Path(folder) / name)
    return index


def _object_config_path(template: str) -> Optional[pathlib.Path]:
    return _object_config_index().get(template)


@functools.lru_cache(maxsize=None)
def _receptacle_entries(config_path: pathlib.Path) -> Tuple[dict, ...]:
    config = json.loads(config_path.read_text())
    out = []
    for key, value in config.get("user_defined", {}).items():
        if key.startswith("receptacle_mesh_"):
            entry = dict(value)
            entry["name"] = value.get("name", key)
            entry["path"] = config_path.parent / value["mesh_filepath"]
            out.append(entry)
        elif key.startswith("receptacle_"):
            print(f"[hssd_layout] skipping non-mesh receptacle {key} in {config_path}",
                  file=sys.stderr)
    return tuple(out)


@functools.lru_cache(maxsize=None)
def _mesh_cached(path: pathlib.Path) -> Tuple[Tuple[np.ndarray, np.ndarray], ...]:
    if not path.exists():  # a few configs name receptacle files that are not shipped
        MISSING_FILES.add(str(path))
        return ()
    return tuple(read_glb_meshes(path))


MISSING_FILES: set = set()


# ================================================================== URDF
class Urdf:
    """Links, joints and forward kinematics of one articulated asset (joint values 0)."""

    def __init__(self, path: pathlib.Path):
        root = ET.parse(path).getroot()
        self.links = {link.get("name"): link for link in root.findall("link")}
        self.joints = {}
        for joint in root.findall("joint"):
            origin = joint.find("origin")
            xyz = [float(v) for v in (origin.get("xyz", "0 0 0") if origin is not None
                                      else "0 0 0").split()]
            rpy = [float(v) for v in (origin.get("rpy", "0 0 0") if origin is not None
                                      else "0 0 0").split()]
            axis_el = joint.find("axis")
            axis = [float(v) for v in (axis_el.get("xyz") if axis_el is not None
                                       else "1 0 0").split()]
            m = _rpy_matrix(*rpy)
            m[:3, 3] = xyz
            child = joint.find("child").get("link")
            self.joints[child] = {"name": joint.get("name"), "type": joint.get("type"),
                                  "parent": joint.find("parent").get("link"),
                                  "origin": m, "axis": np.array(axis)}
        roots = [name for name in self.links if name not in self.joints]
        if len(roots) != 1:
            raise ValueError(f"{path}: expected one root link, found {roots}")
        self.root = roots[0]

    def link_pose(self, link: str) -> np.ndarray:
        """Pose of `link` in the root-link frame with every joint at 0 (closed)."""
        m = np.eye(4)
        while link != self.root:
            joint = self.joints[link]
            m = joint["origin"] @ m
            link = joint["parent"]
        return m

    def moving(self, link: str) -> bool:
        """True if the link, or a link it hangs from, moves (drawer, door, door shelf)."""
        while link != self.root:
            if self.joints[link]["type"] in ("prismatic", "revolute", "continuous"):
                return True
            link = self.joints[link]["parent"]
        return False

    def link_obbs(self, link: str) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Collision shapes of a link as oriented boxes (matrix in the link frame, half
        sizes). Cylinders and spheres become their bounding boxes."""
        out = []
        for col in self.links[link].findall("collision"):
            origin = col.find("origin")
            m = _rpy_matrix(*[float(v) for v in (origin.get("rpy", "0 0 0") if origin is not None
                                                 else "0 0 0").split()])
            m[:3, 3] = [float(v) for v in (origin.get("xyz", "0 0 0") if origin is not None
                                           else "0 0 0").split()]
            geom = col.find("geometry")[0]
            if geom.tag == "box":
                half = np.array([float(v) for v in geom.get("size").split()]) / 2
            elif geom.tag == "cylinder":
                r, length = float(geom.get("radius")), float(geom.get("length"))
                half = np.array([r, r, length / 2])
            elif geom.tag == "sphere":
                half = np.full(3, float(geom.get("radius")))
            else:
                continue
            out.append((m, half))
        return out

    def link_boxes(self, link: str) -> List[np.ndarray]:
        """8-corner boxes (in the link frame) of the link's collision shapes."""
        corners = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
        return [(corners * half) @ m[:3, :3].T + m[:3, 3] for m, half in self.link_obbs(link)]


@functools.lru_cache(maxsize=None)
def _urdf(template: str) -> Tuple[Urdf, pathlib.Path]:
    folder = HSSD / "urdf" / template
    urdfs = sorted(folder.glob("*.urdf"))
    if not urdfs:
        raise FileNotFoundError(f"no URDF for articulated template {template}")
    configs = sorted(folder.glob("*.ao_config.json"))
    return Urdf(urdfs[0]), (configs[0] if configs else None)


@functools.lru_cache(maxsize=None)
def _asset_boxes(template: str) -> Tuple[dict, ...]:
    """Every collision box of an articulated asset in its root-link frame (y up), with
    all joints at 0, marked by link and by whether that link moves."""
    urdf, _ = _urdf(template)
    out = []
    for link in urdf.links:
        pose = urdf.link_pose(link)
        moving = urdf.moving(link)
        for m, half in urdf.link_obbs(link):
            world = pose @ m
            out.append({"link": link, "moving": moving, "rot": world[:3, :3],
                        "pos": world[:3, 3], "half": half})
    return tuple(out)


def _ray_box(origin: np.ndarray, direction: np.ndarray, box: dict,
             pad: float = 0.01) -> Optional[float]:
    """Distance along the ray to an oriented box grown by `pad` on every side, or None
    (slab test). The padding closes the hairline gaps between neighbouring door panels
    and gives zero-thickness panels a thickness."""
    o = box["rot"].T @ (origin - box["pos"])
    d = box["rot"].T @ direction
    half = box["half"] + pad
    t0, t1 = 0.0, math.inf
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if abs(o[i]) > half[i]:
                return None
            continue
        a = (-half[i] - o[i]) / d[i]
        b = (half[i] - o[i]) / d[i]
        if a > b:
            a, b = b, a
        t0, t1 = max(t0, a), min(t1, b)
        if t0 > t1:
            return None
    return t0


# ================================================================== geometry
def polygon_area_centroid(poly: np.ndarray) -> Tuple[float, np.ndarray]:
    x, z = poly[:, 0], poly[:, 1]
    x2, z2 = np.roll(x, -1), np.roll(z, -1)
    cross = x * z2 - x2 * z
    area = cross.sum() / 2
    if abs(area) < 1e-12:
        return 0.0, poly.mean(0)
    cx = ((x + x2) * cross).sum() / (6 * area)
    cz = ((z + z2) * cross).sum() / (6 * area)
    return abs(area), np.array([cx, cz])


def inside(x: float, z: float, poly: np.ndarray) -> bool:
    within = False
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        if (z1 > z) != (z2 > z) and x < (x2 - x1) * (z - z1) / (z2 - z1) + x1:
            within = not within
    return within


def distance_to_polygon(x: float, z: float, poly: np.ndarray) -> float:
    """0 inside, else distance to the nearest edge."""
    if inside(x, z, poly):
        return 0.0
    p = np.array([x, z])
    a, b = poly, np.roll(poly, -1, axis=0)
    ab = b - a
    t = np.clip(((p - a) * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-12), 0, 1)
    nearest = a + ab * t[:, None]
    return float(np.sqrt(((nearest - p) ** 2).sum(1)).min())


def _interior_point(poly: np.ndarray) -> np.ndarray:
    """The area centroid if it lies inside, else the interior grid point nearest to it
    that is farthest from the walls among close candidates."""
    _, c = polygon_area_centroid(poly)
    if inside(c[0], c[1], poly) and distance_to_edges(c, poly) > 0.3:
        return c
    lo, hi = poly.min(0), poly.max(0)
    best, best_score = c, -1e9
    for gx in np.linspace(lo[0], hi[0], 41):
        for gz in np.linspace(lo[1], hi[1], 41):
            if not inside(gx, gz, poly):
                continue
            clearance = distance_to_edges(np.array([gx, gz]), poly)
            score = min(clearance, 0.5) - 0.1 * math.hypot(gx - c[0], gz - c[1])
            if score > best_score:
                best, best_score = np.array([gx, gz]), score
    return best


def distance_to_edges(p: np.ndarray, poly: np.ndarray) -> float:
    a, b = poly, np.roll(poly, -1, axis=0)
    ab = b - a
    t = np.clip(((p - a) * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-12), 0, 1)
    nearest = a + ab * t[:, None]
    return float(np.sqrt(((nearest - p) ** 2).sum(1)).min())


def split_levels(verts: np.ndarray, faces: np.ndarray,
                 tags: Optional[np.ndarray] = None) -> List[dict]:
    """Split a world-space receptacle mesh into horizontal levels.

    Keeps triangles whose normal is within ~25 degrees of vertical (either winding),
    sorts them by height and starts a new level wherever consecutive heights differ by
    more than LEVEL_GAP. If no triangle is horizontal, the whole mesh is one level.
    `tags` (one per face) records which source mesh each triangle came from.
    Returns [{"height_y", "area", "center", "points", "tags"}]: area in square metres of
    horizontal projection, centre the area-weighted centroid, points the level's
    triangle corners, tags the sorted source-mesh tags present in the level."""
    if len(faces) == 0:
        return []
    if tags is None:
        tags = np.zeros(len(faces), dtype=int)
    tri = verts[faces]
    normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    double_area = np.linalg.norm(normal, axis=1)
    ok = double_area > 1e-12
    tri, normal, double_area, tags = tri[ok], normal[ok], double_area[ok], tags[ok]
    if len(tri) == 0:
        return []
    flat = np.abs(normal[:, 1]) / double_area > HORIZONTAL_NY
    if not flat.any():
        flat = np.ones(len(tri), dtype=bool)
    tri, normal, tags = tri[flat], normal[flat], tags[flat]
    area = np.abs(normal[:, 1]) / 2  # horizontal projection
    centroid = tri.mean(1)
    order = np.argsort(centroid[:, 1], kind="stable")
    groups, current = [], [order[0]]
    for a, b in zip(order[:-1], order[1:]):
        if centroid[b, 1] - centroid[a, 1] > LEVEL_GAP:
            groups.append(current)
            current = []
        current.append(b)
    groups.append(current)
    levels = []
    for g in groups:
        g = np.array(g)
        w = area[g]
        total = float(w.sum())
        if total <= 0:
            continue
        center = (centroid[g] * w[:, None]).sum(0) / total
        levels.append({"height_y": float(center[1]), "area": total, "center": center,
                       "points": tri[g].reshape(-1, 3),
                       "tags": sorted({int(t) for t in tags[g]})})
    return levels


# ================================================================== spots from render geometry
# HSSD gives receptacle meshes for only part of its furniture. For the rest, spots are
# read off the object's own render mesh: horizontal triangles, grouped into height
# levels, then probed with rays. A sample point on a level is
#   clear     if nothing of the same object lies within GEOM_CLEARANCE straight above it,
#   enclosed  if horizontal rays 5 cm above it hit the object in all eight directions
#             within GEOM_ENCLOSE_RANGE (it sits in a basin, tub, drum or closed box).
#   sealed    if it is still enclosed just below whatever is above it.
# clear and not enclosed -> surface; clear, enclosed, not sealed -> open (basin, tub);
# clear, enclosed and sealed (or a door link in the way) -> closed (drawer, cupboard,
# drum); not clear -> under something, dropped. Only upward-facing triangles count.
GEOM_CLEARANCE = 0.08       # m of free space needed above a geometry spot
GEOM_ENCLOSE_RANGE = 3.0    # m: rays longer than this count as escaping
GEOM_SAMPLES = 160          # sample points per level

# Categories that never get geometry spots: decoration, building parts, fittings,
# screens, plants. Chairs are handled separately (only a room's sole seat gets one).
GEOMETRY_SKIP = {
    "picture", "painting", "picture_frame", "art_frame", "wall_hanging_decoration",
    "decoration", "decor", "canvas", "poster", "window", "window_frame", "window_shade",
    "window_shutter", "blinds", "curtain", "curtain_rod", "lamp", "table_lamp",
    "floor_lamp", "desk_lamp", "wall_lamp", "ceiling_lamp", "chandelier", "lamp_stand",
    "pathway_light", "radiator", "heater", "boiler", "furnace", "carpet", "doormat",
    "floor_mat", "shower_mat", "plate", "plant", "potted_plant", "decorative_plant",
    "flowerpot", "flower_vase", "vase", "flower", "flower_stand", "mirror",
    "mirror_frame", "door", "garage_door", "gate", "shower_door", "fireplace_wall",
    "tile", "floor", "wall", "wall_panel", "wall_board", "board", "beam", "wall_beam",
    "pillar", "rafter", "roof", "stairs", "staircase", "staircase_handrail", "railing",
    "balcony_railing", "fence", "fencing", "compound_wall", "curb", "grass", "bush",
    "tree", "light_switch", "switch", "electric_outlet", "outlet", "socket", "button",
    "knob", "handle", "electric_box", "ceiling_fan", "fan", "air_conditioning",
    "air_conditioner", "ventilation_hood", "range_hood", "oven_vent", "chimney",
    "showerhead", "shower_tap", "shower_hose", "tap", "towel", "towel_rack",
    "towel_ring", "hanger", "clothes_hanger", "coat_hanger", "clothes_hanger_rod",
    "security_camera", "smoke_alarm", "tv", "led_tv", "wall_tv", "screen",
    "projector_screen", "panel_screen", "speaker", "toilet_paper", "toilet_brush",
    "toilet_brush_holder", "tablecloth", "shelf_/w_art", "unknown", "unknown_wall",
    "bidet", "urinal", "car", "bicycle", "motorcycle", "clothes", "clothing",
    "hanging_clothes", "bathrobe", "blanket", "pillow", "gym_equipment", "weight",
    "statue", "sculpture", "bust", "christmas_tree", "umbrella", "wall_clock", "clock",
    "dartboard", "calendar", "pipe", "post", "water_heater", "swimming_pool", "pool",
}
CHAIR_CATEGORIES = {"chair", "office_chair", "bar_stool", "stool", "semi_chair",
                    "rocking_chair", "seat"}
SEAT_CATEGORIES = {"couch", "sofa", "sofa_chair", "l-shaped_sofa", "chaise", "sofa_set",
                   "loveseat", "armchair", "bench", "ottoman", "pouffe"}
WASHER_CATEGORIES = {"washing_machine", "washer/dryer", "washer_dryer",
                     "washing_machine_and_dryer", "dryer"}
BASIN_NAME = re.compile(r"\b(sink|basin|washbasin|lavabo|lavabos|vanity|washstand|bath|"
                        r"bathtub|tub|badewanne|baignoire|waschtisch|waschplatz)\b", re.I)


@functools.lru_cache(maxsize=128)
def _render_triangles(path: pathlib.Path) -> np.ndarray:
    """All triangles of a render .glb as (n, 3, 3), glTF node transforms applied."""
    if not path.exists():
        MISSING_FILES.add(str(path))
        return np.zeros((0, 3, 3))
    tris = [verts[faces] for verts, faces in read_glb_meshes(path) if len(faces)]
    return np.concatenate(tris) if tris else np.zeros((0, 3, 3))


def _rigid_render_path(template: str) -> Optional[pathlib.Path]:
    cfg = _object_config_path(template)
    if cfg is None:
        return None
    asset = json.loads(cfg.read_text()).get("render_asset", f"{template}.glb")
    return cfg.parent / asset


@functools.lru_cache(maxsize=64)
def _ao_triangles(template: str) -> Tuple[np.ndarray, np.ndarray, Tuple[str, ...]]:
    """Visual triangles of every link of an articulated asset in its root-link frame,
    joints at 0, with the index of the link each triangle belongs to."""
    urdf, _ = _urdf(template)
    folder = HSSD / "urdf" / template
    tris, owner, names = [], [], []
    for link_name, link in urdf.links.items():
        names.append(link_name)
        pose = urdf.link_pose(link_name)
        for vis in link.findall("visual"):
            mesh = vis.find("geometry/mesh")
            if mesh is None:
                continue
            t = _render_triangles(folder / mesh.get("filename"))
            if not len(t):
                continue
            origin = vis.find("origin")
            m = np.eye(4)
            if origin is not None:
                m = _rpy_matrix(*[float(v) for v in origin.get("rpy", "0 0 0").split()])
                m[:3, 3] = [float(v) for v in origin.get("xyz", "0 0 0").split()]
            full = pose @ m
            tris.append(t @ full[:3, :3].T + full[:3, 3])
            owner.append(np.full(len(t), len(names) - 1))
    if not tris:
        return np.zeros((0, 3, 3)), np.zeros(0, dtype=int), tuple(names)
    return np.concatenate(tris), np.concatenate(owner), tuple(names)


def _up_clearance(points: np.ndarray, tris: np.ndarray) -> np.ndarray:
    """Distance straight up from each point to the nearest triangle (inf if none)."""
    out = np.full(len(points), np.inf)
    if not len(tris):
        return out
    xz = tris[:, :, [0, 2]]
    lo, hi = xz.min(1), xz.max(1)
    top = tris[:, :, 1].max(1)
    for i, p in enumerate(points):
        cand = np.where((lo[:, 0] <= p[0]) & (hi[:, 0] >= p[0]) & (lo[:, 1] <= p[2])
                        & (hi[:, 1] >= p[2]) & (top > p[1] + 1e-3))[0]
        if not len(cand):
            continue
        a, b, c = xz[cand, 0], xz[cand, 1], xz[cand, 2]
        v0, v1, v2 = b - a, c - a, np.array([p[0], p[2]]) - a
        d00 = (v0 * v0).sum(1)
        d01 = (v0 * v1).sum(1)
        d11 = (v1 * v1).sum(1)
        d20 = (v2 * v0).sum(1)
        d21 = (v2 * v1).sum(1)
        den = d00 * d11 - d01 * d01
        ok = np.abs(den) > 1e-14
        den = np.where(ok, den, 1.0)
        v = (d11 * d20 - d01 * d21) / den
        w = (d00 * d21 - d01 * d20) / den
        u = 1 - v - w
        hit = ok & (u >= -1e-6) & (v >= -1e-6) & (w >= -1e-6)
        if not hit.any():
            continue
        ys = tris[cand, :, 1]
        y = u * ys[:, 0] + v * ys[:, 1] + w * ys[:, 2]
        t = y[hit] - p[1]
        t = t[t > 1e-3]
        if len(t):
            out[i] = t.min()
    return out


def _horizontal_hits(origin: np.ndarray, direction: np.ndarray, tris: np.ndarray,
                     max_t: float, cand: Optional[np.ndarray] = None) -> Tuple[float, int]:
    """Nearest hit (distance, triangle index) of a horizontal ray; (inf, -1) if none.
    `cand` (triangles spanning the ray's height) can be passed in when several rays
    share one origin."""
    if cand is None:
        ys = tris[:, :, 1]
        cand = np.where((ys.min(1) <= origin[1]) & (ys.max(1) >= origin[1]))[0]
    if not len(cand):
        return math.inf, -1
    v0, v1, v2 = tris[cand, 0], tris[cand, 1], tris[cand, 2]
    e1, e2 = v1 - v0, v2 - v0
    pvec = np.cross(direction, e2)
    det = (e1 * pvec).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    tvec = origin - v0
    u = (tvec * pvec).sum(1) * inv
    qvec = np.cross(tvec, e1)
    v = (qvec @ direction) * inv
    t = (qvec * e2).sum(1) * inv
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-4) & (t <= max_t)
    if not hit.any():
        return math.inf, -1
    j = np.argmin(np.where(hit, t, np.inf))
    return float(t[j]), int(cand[j])


def _sample_levels(tris: np.ndarray, levels_from: np.ndarray, rng_seed: int = 0) -> List[dict]:
    """Horizontal levels of the triangles `levels_from` (indices into tris), each with
    up to GEOM_SAMPLES area-weighted sample points."""
    sub = tris[levels_from]
    if not len(sub):
        return []
    normal = np.cross(sub[:, 1] - sub[:, 0], sub[:, 2] - sub[:, 0])
    dbl = np.linalg.norm(normal, axis=1)
    ok = dbl > 1e-12
    # upward-facing only: render meshes are closed shells, and the underside of a sofa
    # base faces down into the hollow inside (winding agrees with the stored vertex
    # normals for 99.8% of horizontal triangles in a 300-object sample)
    flat = ok & (normal[:, 1] > HORIZONTAL_NY * np.where(ok, dbl, 1.0))
    sub = sub[flat]
    if not len(sub):
        return []
    area = np.abs(np.cross(sub[:, 1] - sub[:, 0], sub[:, 2] - sub[:, 0])[:, 1]) / 2
    cy = sub[:, :, 1].mean(1)
    order = np.argsort(cy, kind="stable")
    groups, cur = [], [order[0]]
    for a, b in zip(order[:-1], order[1:]):
        if cy[b] - cy[a] > LEVEL_GAP:
            groups.append(cur)
            cur = []
        cur.append(b)
    groups.append(cur)
    rng = np.random.default_rng(rng_seed)
    out = []
    for g in groups:
        g = np.array(g)
        total = float(area[g].sum())
        if total < MIN_SPOT_AREA:
            continue
        pick = rng.choice(g, size=GEOM_SAMPLES, p=area[g] / total)
        r1, r2 = rng.random(GEOM_SAMPLES), rng.random(GEOM_SAMPLES)
        flip = r1 + r2 > 1
        r1, r2 = np.where(flip, 1 - r1, r1), np.where(flip, 1 - r2, r2)
        t = sub[pick]
        pts = t[:, 0] + r1[:, None] * (t[:, 1] - t[:, 0]) + r2[:, None] * (t[:, 2] - t[:, 0])
        out.append({"height_y": float((cy[g] * area[g]).sum() / total), "area": total,
                    "samples": pts, "points": sub[g].reshape(-1, 3)})
    return out


def _enclosed(origin: np.ndarray, tris: np.ndarray, moving: Optional[np.ndarray],
              enclose_range: float, yrange: Optional[Tuple[np.ndarray, np.ndarray]] = None
              ) -> Tuple[bool, bool]:
    """(all eight horizontal rays hit, and the first hit of one is a moving link)."""
    lo, hi = yrange if yrange is not None else (tris[:, :, 1].min(1), tris[:, :, 1].max(1))
    cand = np.where((lo <= origin[1]) & (hi >= origin[1]))[0]
    any_door = False
    for d in _RAY_DIRECTIONS:
        _t, j = _horizontal_hits(origin, d, tris, enclose_range, cand)
        if j < 0:
            return False, False
        any_door = any_door or bool(moving is not None and moving[j])
    return True, any_door


def _probe(samples: np.ndarray, tris: np.ndarray, moving: Optional[np.ndarray] = None,
           enclose_range: float = GEOM_ENCLOSE_RANGE) -> Dict[str, np.ndarray]:
    """For each sample point: clear above? enclosed sideways? first sideways hit on a
    moving link (a door)? sealed (still enclosed just under whatever is above it, as in
    a drawer or a cupboard, unlike a basin whose walls stop below the next thing up)?"""
    up = _up_clearance(samples + [0, 0.005, 0], tris)
    clear = up >= GEOM_CLEARANCE
    yrange = (tris[:, :, 1].min(1), tris[:, :, 1].max(1))
    n = len(samples)
    enclosed, door, sealed = (np.zeros(n, dtype=bool) for _ in range(3))
    # sideways rays are costly on big meshes: there, probe 32 points and give each
    # sample the answer of its nearest probe
    n_probe = n if len(tris) <= 60000 else 32
    probe_idx = np.unique(np.linspace(0, n - 1, min(n_probe, n)).astype(int))
    res = []
    for i in probe_idx:
        enc, dr = _enclosed(samples[i] + [0, 0.05, 0], tris, moving, enclose_range, yrange)
        seal = False
        if enc:
            if math.isfinite(up[i]) and up[i] > 0.1:
                seal, dr2 = _enclosed(samples[i] + [0, up[i] - 0.03, 0], tris, moving,
                                      enclose_range, yrange)
                dr = dr or dr2
            # nothing above within the object: a basin or tub, never sealed
        res.append((enc, dr, seal))
    pp = samples[probe_idx][:, [0, 2]]
    for i, p in enumerate(samples[:, [0, 2]]):
        k = int(np.argmin(((pp - p) ** 2).sum(1)))
        enclosed[i], door[i], sealed[i] = res[k]
    return {"clear": clear, "enclosed": enclosed, "door": door, "sealed": sealed, "up": up}


def _clusters(points: np.ndarray, link: float) -> List[np.ndarray]:
    """Single-linkage groups of points in the horizontal plane (index arrays)."""
    n = len(points)
    label = -np.ones(n, dtype=int)
    xz = points[:, [0, 2]]
    k = 0
    for i in range(n):
        if label[i] >= 0:
            continue
        label[i] = k
        stack = [i]
        while stack:
            j = stack.pop()
            near = np.where((label < 0) & (((xz - xz[j]) ** 2).sum(1) <= link * link))[0]
            label[near] = k
            stack.extend(near.tolist())
        k += 1
    return [np.where(label == c)[0] for c in range(k)]


def geometry_levels(tris_world: np.ndarray, select: Optional[np.ndarray] = None,
                    moving: Optional[np.ndarray] = None) -> List[dict]:
    """Spots read from render triangles already in world coordinates.

    `select` limits which triangles may carry a spot (e.g. one drawer link); all
    triangles count as obstacles. Each level's sample points are classified one by one
    (surface / open / closed, see the section comment); the points of one kind are
    grouped where they lie within reach of each other, so the two basins of a double
    vanity become two spots. A group needs 8 samples (5%) and MIN_SPOT_AREA. Height is the
    mean height of the group's points (a curved basin's floor is lower than its rim)."""
    if select is None:
        select = np.arange(len(tris_world))
    out = []
    for lvl in _sample_levels(tris_world, select):
        pr = _probe(lvl["samples"], tris_world, moving)
        enc, clear = pr["enclosed"], pr["clear"]
        kinds = {
            "surface": clear & ~enc,
            "open": clear & enc & ~pr["sealed"] & ~pr["door"],
            # a compartment closed on every side: behind a door link (articulated), or
            # a drawer / cupboard modelled in one rigid mesh, or a washing-machine drum
            "closed": clear & enc & (pr["sealed"] | pr["door"]),
        }
        n = len(lvl["samples"])
        # smooth: each sample takes the most common kind among its 5 nearest neighbours,
        # so a ray slipping through a seam does not cut a tub floor into pieces
        # (covered samples, code 0, neither vote nor change: a basin set into a worktop
        # sits among hidden carcass panels)
        code = np.select([kinds["surface"], kinds["open"], kinds["closed"]], [1, 2, 3], 0)
        live = np.where(code > 0)[0]
        if len(live) >= 5:
            xz = lvl["samples"][live][:, [0, 2]]
            d2 = ((xz[:, None, :] - xz[None, :, :]) ** 2).sum(-1)
            nn = np.argsort(d2, axis=1)[:, :5]
            code[live] = [np.bincount(code[live][row], minlength=4).argmax() for row in nn]
        kinds = {"surface": code == 1, "open": code == 2, "closed": code == 3}
        per_sample = lvl["area"] / n
        link = max(0.25, 2.5 * math.sqrt(per_sample))
        for kind, mask in kinds.items():
            idx = np.where(mask)[0]
            if len(idx) < 8:
                continue
            for grp in _clusters(lvl["samples"][idx], link):
                pts = lvl["samples"][idx[grp]]
                area = per_sample * len(pts)
                if len(pts) < 8 or area < MIN_SPOT_AREA:
                    continue
                y = float(pts[:, 1].mean())
                out.append({"kind": kind, "height_y": y, "area": area,
                            "center": np.array([pts[:, 0].mean(), y, pts[:, 2].mean()]),
                            "points": pts})
    return out


def _flip_if_mirrored(tris: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    return tris[:, ::-1] if np.linalg.det(matrix[:3, :3]) < 0 else tris


def rigid_world_triangles(template: str, world: np.ndarray) -> Tuple[np.ndarray, str]:
    path = _rigid_render_path(template)
    if path is None:
        return np.zeros((0, 3, 3)), ""
    tris = _render_triangles(path)
    tw = _flip_if_mirrored(tris @ world[:3, :3].T + world[:3, 3], world)
    return tw, path.name


def ao_world_triangles(template: str, world: np.ndarray):
    """(triangles in world, owning link name per triangle, moving flag per triangle)."""
    urdf, _ = _urdf(template)
    tris, owner, names = _ao_triangles(template)
    tw = _flip_if_mirrored(tris @ world[:3, :3].T + world[:3, 3], world)
    moving_link = np.array([urdf.moving(n) for n in names], dtype=bool)
    return tw, owner, names, moving_link[owner] if len(owner) else np.zeros(0, dtype=bool)


def _geo_level(lvl: dict, kind: str, detail: str, link: Optional[str] = None,
               moving: bool = False, part: Optional[str] = None) -> dict:
    """A geometry level in the same shape as a receptacle level."""
    return {"receptacle": "geometry", "link": link, "meshes": [detail], "moving_link": moving,
            "covered_by": None, "hssd_filter": None, "within_set": False, "tags": [],
            "height_y": lvl["height_y"], "area": lvl["area"], "center": lvl["center"],
            "points": lvl["points"], "kind": kind, "part": part, "geometry": detail}


def _floor_y(tw: np.ndarray) -> float:
    return float(tw[:, :, 1].min()) if len(tw) else 0.0


def rigid_geometry_spots(template: str, world: np.ndarray, category: str,
                         kinds: Sequence[str] = ("surface", "open", "closed")) -> List[dict]:
    """Spots of a rigid object read from its render mesh (see the section comment)."""
    tw, name = rigid_world_triangles(template, world)
    if not len(tw):
        return []
    bottom = _floor_y(tw)
    out = []
    for lvl in geometry_levels(tw):
        kind = lvl["kind"]
        if kind not in kinds:
            continue
        if kind == "open" and category in ("toilet", "bidet", "urinal"):
            continue  # a toilet bowl is not a place to put things
        if lvl["height_y"] - bottom < 0.04 and lvl["area"] < 0.1:
            continue  # feet and plinths at floor level
        out.append(_geo_level(lvl, kind, f"render mesh {name}"))
    return out


def washer_drum(template: str, world: np.ndarray) -> Optional[dict]:
    """The drum of a washing machine or dryer. A drum is curved, so its floor rarely
    shows as horizontal triangles; any enclosed level 0.1-0.6 m above the machine's
    bottom is taken, else the drum is placed at 30% of the machine's height, centred,
    with a nominal 0.1 m2."""
    tw, name = rigid_world_triangles(template, world)
    if not len(tw):
        return None
    lo, hi = tw.reshape(-1, 3).min(0), tw.reshape(-1, 3).max(0)
    found = [lv for lv in geometry_levels(tw) if lv["kind"] != "surface"
             and 0.1 <= lv["height_y"] - lo[1] <= 0.6]
    if found:
        best = max(found, key=lambda lv: lv["area"])
        lvl = dict(best, area=max(best["area"], 0.1))
        return _geo_level(lvl, "closed", f"render mesh {name}", part="drum")
    y = lo[1] + 0.3 * (hi[1] - lo[1])
    c = np.array([(lo[0] + hi[0]) / 2, y, (lo[2] + hi[2]) / 2])
    lvl = {"height_y": float(y), "area": 0.1, "center": c, "points": c[None]}
    return _geo_level(lvl, "closed", f"approximated from the bounding box of {name}",
                      part="drum")


def ao_geometry_spots(template: str, world: np.ndarray, basins_only: bool = False) -> List[dict]:
    """Spots of an articulated asset that has no receptacle meshes, from its link meshes
    with every joint shut. A drawer link gives one closed spot: its lowest level. Fixed
    links give surface, open and closed levels like a rigid object, a level being closed
    when the first sideways hit in some direction is a door link. With basins_only, only
    open levels of fixed links (a sink basin HSSD did not mark) are returned."""
    tw, owner, names, moving = ao_world_triangles(template, world)
    if not len(tw):
        return []
    urdf, _ = _urdf(template)
    out = []
    fixed = np.where(~moving)[0]
    for lvl in geometry_levels(tw, fixed, moving):
        if basins_only and lvl["kind"] != "open":
            continue
        out.append(_geo_level(lvl, lvl["kind"], f"link meshes of {template}"))
    if basins_only:
        return out
    for li, link in enumerate(names):
        joint = urdf.joints.get(link)
        if joint is None or joint["type"] != "prismatic":
            continue
        levels = geometry_levels(tw, np.where(owner == li)[0], moving)
        if not levels:
            continue
        low = min(levels, key=lambda lv: lv["height_y"])
        out.append(_geo_level(low, "closed", f"link {link}", link=link, moving=True,
                              part=_part_from_receptacle(link) or "drawer"))
    return out


def _local_bbox_rigid(template: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    path = _rigid_render_path(template)
    if path is None or not path.exists():
        return None
    tris = _render_triangles(path)
    if not len(tris):
        return None
    pts = tris.reshape(-1, 3)
    return pts.min(0), pts.max(0)


def _world_bbox(points: np.ndarray, matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    w = points @ matrix[:3, :3].T + matrix[:3, 3]
    return w.min(0), w.max(0)


# ================================================================== naming
def _slug(text: str) -> str:
    text = text.lower().replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_") or "x"


def room_type(label: str) -> str:
    for kind, labels in ROOM_TYPES.items():
        if label in labels:
            return kind
    return "other"


def _room_base_id(region: dict) -> str:
    name = re.sub(r"\.\d+$", "", region["name"]).strip()
    base = _slug(name)
    if base == "tv":
        base = "tv_room"
    return base


def _part_from_receptacle(name: str) -> str:
    """'Wardrobe0067_drawer01_receptacle_mesh' -> 'drawer_1'; 'shelf_02' -> 'shelf_2'."""
    part = re.sub(r"\.\d+$", "", name)
    part = re.sub(r"_?receptacle_mes(h)?$", "", part)
    part = re.sub(r"^receptacle_mesh_?", "", part)
    # drop the asset prefix (e.g. "Wardrobe0067_", "kitchen_cabinet_01_" stays meaningful)
    if re.match(r"^[A-Za-z_]*\d{4}$", part) or re.match(r"^\d{4}$", part):
        return ""  # named after the asset itself: no part name (see _name_spots)
    m = re.match(r"^[A-Za-z_]*?\d{4}_(.*)$", part)
    if m:
        part = m.group(1)
    part = _slug(part)
    part = re.sub(r"([a-z])0*(\d+)", r"\1_\2", part)  # drawer01 -> drawer_1
    part = re.sub(r"_0+(\d)", r"_\1", part)            # shelf_01 -> shelf_1
    return part


# ================================================================== the home
def _load_scene(scene_id: str) -> dict:
    return json.loads((HSSD / "scenes-articulated" / f"{scene_id}.scene_instance.json").read_text())


def _filter_status(scene: dict, scene_id: str) -> Tuple[Dict[str, str], set, set]:
    rel = scene.get("user_defined", {}).get("scene_filter_file")
    path = HSSD / rel if rel else (HSSD / "scene_filter_files/articulated_scene_filter_files"
                                   / f"{scene_id}.rec_filter.json")
    status: Dict[str, str] = {}
    if not path.exists():
        return status, set(), set()
    data = json.loads(path.read_text())
    for name in data.get("active", []):
        status[name] = "active"
    for key in ("height_filtered", "access_filtered", "stability_filtered", "manually_filtered"):
        for name in data.get(key, []):
            status[name] = key  # later keys win: manual judgement is the strongest
    return status, set(data.get("within_set", [])), set(data.get("cook_surface", []))


def _rooms(scene_id: str) -> List[dict]:
    regions = json.loads((HSSD / "semantics/scenes" / f"{scene_id}.semantic_config.json")
                         .read_text())["region_annotations"]
    bases = [_room_base_id(r) for r in regions]
    counts = Counter(bases)
    seen: Counter = Counter()
    rooms = []
    for region, base in zip(regions, bases):
        seen[base] += 1
        rid = base if counts[base] == 1 else f"{base}_{seen[base]}"
        poly = np.array([[p[0], p[2]] for p in region["poly_loop"]], dtype=float)
        area, _ = polygon_area_centroid(poly)
        rooms.append({"id": rid, "name": region["name"], "label": region["label"],
                      "type": room_type(region["label"]),
                      "polygon": [[round(float(x), 4), round(float(z), 4)] for x, z in poly],
                      "floor_height": float(region["floor_height"]),
                      "ceiling_height": float(region["floor_height"] + region["extrusion_height"]),
                      "area": round(area, 3), "_poly": poly, "_area": area})
    return rooms


def _same_storey(room: dict, y: float) -> bool:
    return room["floor_height"] - 0.3 <= y <= room["ceiling_height"] + 0.1


def room_of_point(rooms: List[dict], p: Sequence[float], margin: float = 0.0,
                  prefer: Optional[str] = None) -> Tuple[Optional[dict], float]:
    """Room containing world point p (smallest such polygon on the same storey).

    Returns (room, distance outside its polygon); distance 0 means strictly inside."""
    x, y, z = p
    storey = [r for r in rooms if _same_storey(r, y)] or rooms
    if prefer is not None:
        for r in storey:
            if r["id"] == prefer and distance_to_polygon(x, z, r["_poly"]) <= margin:
                return r, distance_to_polygon(x, z, r["_poly"])
    containing = [r for r in storey if inside(x, z, r["_poly"])]
    if containing:
        return min(containing, key=lambda r: r["_area"]), 0.0
    if not storey:
        return None, float("inf")
    dist = [(distance_to_polygon(x, z, r["_poly"]), r["_area"], i) for i, r in enumerate(storey)]
    d, _, i = min(dist)
    return storey[i], d


def _open_by_name(entry_name: str) -> bool:
    """Receptacle names that describe a basin or container: sink, basin, bin, basket,
    tub, bowl (but not "sink_top", the counter around a sink)."""
    words = _part_from_receptacle(entry_name).split("_")
    return (any(w in words or any(x.startswith(w) for x in words) for w in OPEN_NAME_WORDS)
            and "top" not in words)


def _classify(entry_name: str, category: str, moving_link: bool, covered: bool) -> str:
    """closed: on a drawer or other moving part, or behind a door (see _behind_door);
    open: a basin or container, by receptacle name or object category; else surface.
    Sink basins are open even when the cabinet doors below them reach their height."""
    if moving_link:
        return "closed"
    if _open_by_name(entry_name):
        return "open"
    if covered:
        return "closed"
    if category in OPEN_CATEGORIES:
        return "open"
    return "surface"


_RAY_DIRECTIONS = tuple(np.array([math.cos(a), 0.0, math.sin(a)])
                        for a in np.arange(8) * math.pi / 4)


def _behind_door(center: np.ndarray, boxes: Sequence[dict]) -> Optional[str]:
    """Is a receptacle level of an articulated asset closed in by a door?

    Works in the asset's root-link frame (y up) with every door and drawer shut. From a
    point just above the level's centre, eight horizontal rays go out (the asset's four
    axis directions and the four diagonals). The level is behind a door when every ray
    hits a collision box of the asset within 2 m and the first box hit by at least one
    ray belongs to a moving link (a door, flap or sliding panel). Open shelves fail on
    their open side; tops fail on every side. Boxes that contain the ray's start (the
    shelf board itself, a drawer bottom) are ignored. The test is tried 5 cm and 12 cm
    above the level, because some doors stop a few centimetres above the cabinet floor.
    Returns the door's link name, or None."""
    for lift in (0.05, 0.12):
        origin = np.asarray(center, dtype=float) + np.array([0.0, lift, 0.0])
        door, enclosed = None, True
        for d in _RAY_DIRECTIONS:
            best, best_box = None, None
            for box in boxes:
                t = _ray_box(origin, d, box)
                if t is not None and 0.0 < t <= 2.0 and (best is None or t < best):
                    best, best_box = t, box
            if best_box is None:
                enclosed = False
                break
            if best_box["moving"] and door is None:
                door = best_box["link"]
        if enclosed and door is not None:
            return door
    return None


def _sink_bearing(category: str, name: str, entries: Sequence[dict]) -> bool:
    return (category in SINK_CATEGORIES or category in ("bathtub", "bath_sink")
            or bool(BASIN_NAME.search(name))
            or any("sink" in e["name"].lower() for e in entries))


def _merge_basins(levels: List[dict], basins: List[dict], part: str) -> List[dict]:
    """Add geometry basins, but where HSSD already has a receptacle at the same place
    (within 5 cm of height and 25 cm across, e.g. a sink basin HSSD calls "shelf_02"),
    turn that receptacle into the open basin instead of adding a second spot."""
    new = []
    for b in basins:
        same = [lv for lv in levels if not lv.get("geometry")
                and abs(lv["height_y"] - b["height_y"]) <= 0.05
                and math.hypot(lv["center"][0] - b["center"][0],
                               lv["center"][2] - b["center"][2]) <= 0.25]
        if same:
            for lv in same:
                lv["kind"], lv["part"] = "open", part
                lv["reclassified"] = "open: render geometry shows a basin here"
        else:
            new.append(dict(b, part=part))
    return new


def _geometry_additions(template: str, world: np.ndarray, articulated: bool, category: str,
                        name: str, entries: Sequence[dict], levels: List[dict],
                        mode: Optional[str]) -> List[dict]:
    """Spots HSSD's receptacle meshes leave out, read from render geometry:
    every spot of a rigid object with no receptacle mesh (mode "all"); every spot of an
    articulated asset with no usable receptacle mesh; the basin of a sink or bathtub
    that has no open spot; the seat of a sofa whose receptacles miss it; the drum of a
    washing machine."""
    out: List[dict] = []
    has_files = any(e["path"].exists() for e in entries)
    if articulated:
        if not levels and not has_files:
            out.extend(ao_geometry_spots(template, world))
        elif _sink_bearing(category, name, entries) and not any(
                lv["kind"] == "open" for lv in levels):
            out.extend(_merge_basins(levels, ao_geometry_spots(template, world, basins_only=True),
                                     "sink_basin"))
        return out
    if mode == "all":
        tub = category == "bathtub" or "bath" in name.lower()
        for lv in rigid_geometry_spots(template, world, category):
            if lv["kind"] == "open" and _sink_bearing(category, name, entries):
                lv = dict(lv, part="tub" if tub else "basin")
            out.append(lv)
    elif mode is None and entries:
        tw, _ = rigid_world_triangles(template, world)
        bottom = _floor_y(tw)
        if category in SEAT_CATEGORIES and not any(
                lv["kind"] == "surface" and 0.3 <= lv["height_y"] - bottom <= 0.65
                for lv in levels):
            seats = [lv for lv in rigid_geometry_spots(template, world, category, ("surface",))
                     if 0.3 <= lv["height_y"] - bottom <= 0.65]
            if seats:
                out.append(dict(max(seats, key=lambda lv: lv["area"]), part="seat"))
    if _sink_bearing(category, name, entries) and not any(
            lv["kind"] == "open" for lv in levels + out):
        basins = rigid_geometry_spots(template, world, category, ("open",))
        tub = category == "bathtub" or "bath" in name.lower()
        out.extend(_merge_basins(levels, basins, "tub" if tub else "basin"))
    if category in WASHER_CATEGORIES and not any(
            lv["kind"] == "closed" for lv in levels + out):
        drum = washer_drum(template, world)
        if drum:
            out.append(drum)
    return out


def _piece_bbox(piece: dict) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    if "bbox" not in piece:
        if piece["articulated"]:
            tw = ao_world_triangles(piece["template"], piece["world"])[0]
        else:
            tw = rigid_world_triangles(piece["template"], piece["world"])[0]
        pts = tw.reshape(-1, 3)
        piece["bbox"] = (pts.min(0), pts.max(0)) if len(pts) else None
    return piece["bbox"]


def _sole_chair_seats(pieces: List[dict]) -> None:
    """A chair without a receptacle mesh gets a seat spot only when it is the one seat
    of its room (no sofa, bench, ottoman or other chair there)."""
    seats = defaultdict(list)
    for p in pieces:
        if p["facts"]["category"] in SEAT_CATEGORIES | CHAIR_CATEGORIES:
            seats[p["room"]].append(p)
    for group in seats.values():
        if len(group) != 1 or not group[0]["chair_levels"]:
            continue
        chair = group[0]
        box = _piece_bbox(chair)
        bottom = box[0][1] if box else 0.0
        cand = [lv for lv in chair["chair_levels"] if 0.3 <= lv["height_y"] - bottom <= 0.75]
        if cand:
            chair["levels"].append(dict(max(cand, key=lambda lv: lv["area"]), part="seat"))


def _basins_at_taps(scene: dict, rooms: List[dict], pieces: List[dict]) -> None:
    """A tap standing on a worktop with no open spot near it marks a sink HSSD did not
    model as a receptacle (common in kitchens built as one cabinet unit). The basin is
    read from the worktop's geometry within 0.6 m of the tap; failing that it is placed
    12 cm below the worktop, 15 cm in front of the tap (towards the middle of the
    worktop's depth), with a nominal 0.15 m2."""
    for index, inst in enumerate(scene.get("object_instances", [])):
        facts = object_facts(inst["template_name"])
        if facts["category"] not in ("tap", "faucet", "kitchen_tap"):
            continue
        tap = np.array(inst.get("translation", [0, 0, 0]), dtype=float)
        room, dist = room_of_point(rooms, tap)
        if room is None or dist > ROOM_MARGIN:
            continue

        def near(lv, r=0.7):
            c = lv["center"]
            return math.hypot(c[0] - tap[0], c[2] - tap[2]) <= r and abs(c[1] - tap[1]) <= 0.6

        if any(lv["kind"] == "open" and near(lv) for p in pieces for lv in p["levels"]):
            continue
        hosts = []
        for p in pieces:
            if p["room"] != room["id"]:
                continue
            box = _piece_bbox(p)
            if box is None:
                continue
            lo, hi = box
            if (lo[0] - 0.15 <= tap[0] <= hi[0] + 0.15 and lo[2] - 0.15 <= tap[2] <= hi[2] + 0.15
                    and tap[1] - 0.4 <= hi[1] and lo[1] <= tap[1]):
                hosts.append((abs(hi[1] - tap[1]) if hi[1] < tap[1] + 0.3 else 1.0, p))
        if not hosts:
            continue
        host = min(hosts, key=lambda h: h[0])[1]
        if host["articulated"]:
            found = ao_geometry_spots(host["template"], host["world"], basins_only=True)
        else:
            found = rigid_geometry_spots(host["template"], host["world"],
                                         host["facts"]["category"], ("open",))
        found = [lv for lv in found if near(lv, 0.6)]
        if found:
            best = max(found, key=lambda lv: lv["area"])
            best = dict(best, geometry=best["geometry"] + f" near tap object_instances[{index}]")
            host["levels"].extend(_merge_basins(host["levels"], [best], "sink_basin"))
            continue
        lo, hi = _piece_bbox(host)
        tops = [lv["height_y"] for lv in host["levels"] if lv["kind"] == "surface" and near(lv, 0.8)]
        top = max(tops) if tops else min(hi[1], tap[1])
        centre = (lo + hi) / 2
        axis = 0 if (hi[0] - lo[0]) < (hi[2] - lo[2]) else 2   # the worktop's depth axis
        c = tap.copy()
        c[axis] += 0.15 * np.sign(centre[axis] - tap[axis])
        c[1] = top - 0.12
        lvl = {"height_y": float(c[1]), "area": 0.15, "center": c, "points": c[None]}
        host["levels"].append(_geo_level(
            lvl, "open", f"approximated 12 cm below the worktop at tap object_instances[{index}]",
            part="sink_basin"))


def extract(scene_id: str, drop_filters: Iterable[str] = DROP_FILTERS,
            min_area: float = MIN_SPOT_AREA, max_height: float = MAX_SPOT_HEIGHT,
            geometry: bool = True) -> dict:
    """Rooms, furniture and spots of one articulated HSSD scene. See the module docstring."""
    scene_id = str(scene_id)
    scene = _load_scene(scene_id)
    status, within_set, cook = _filter_status(scene, scene_id)
    drop_filters = set(drop_filters)
    rooms = _rooms(scene_id)

    pieces = []  # furniture before ids
    counters: Counter = Counter()
    for articulated, key in ((False, "object_instances"), (True, "articulated_object_instances")):
        for index, inst in enumerate(scene.get(key, [])):
            template = re.sub(r"\.(ao|object)_config\.json$", "",
                              inst["template_name"].split("/")[-1])
            counters[template] += 1
            handle = f"{template}_:{counters[template] - 1:04d}"
            facts = object_facts(template)
            if inst.get("is_instance_visible") is False:
                continue
            world = instance_matrix(inst, articulated)
            entries: Tuple[dict, ...] = ()
            urdf = None
            if articulated:
                urdf, ao_config = _urdf(template)
                if ao_config is not None:
                    entries = _receptacle_entries(ao_config)
            else:
                cfg = _object_config_path(template)
                if cfg is not None:
                    entries = _receptacle_entries(cfg)
                if facts["pickable"] is True:
                    continue  # clutter
            cat = facts["category"]
            geometry_mode = None  # how render geometry adds spots to this piece
            if not articulated and not entries:
                if cat in CHAIR_CATEGORIES:
                    geometry_mode = "chair"   # a seat spot only if the room has no other seat
                elif cat not in GEOMETRY_SKIP:
                    geometry_mode = "all"
                elif cat not in LANDMARK_CATEGORIES:
                    continue  # decoration: nothing to put things on
            levels = []
            boxes = _asset_boxes(template) if articulated else ()
            inv_world = np.linalg.inv(world)
            # Group receptacle meshes into the pieces that become spots. Articulated
            # receptacles are named by their authors ("drawer01", "inside_door02"), so each
            # keeps its own spots. A rigid object's receptacle .glb holds one mesh per
            # surface fragment with no names (a sofa seat can come as 18 cushion pieces),
            # so all fragments of one rigid object are pooled and split by height only.
            groups: Dict[str, dict] = {}
            for entry in entries:
                if articulated:
                    link = entry.get("parent_link")
                    if link not in urdf.links:
                        print(f"[hssd_layout] {handle}: receptacle {entry['name']} names "
                              f"unknown link {link}", file=sys.stderr)
                        continue
                    local = urdf.link_pose(link)
                    moving = urdf.moving(link)
                else:
                    link, local, moving = None, np.eye(4), False
                to_world = world @ local
                key = entry["name"] if articulated else "all"
                group = groups.setdefault(key, {"verts": [], "faces": [], "tags": [],
                                                "names": [], "link": link, "moving": moving,
                                                "receptacle": entry["name"]})
                for mix, (verts, faces) in enumerate(_mesh_cached(entry["path"])):
                    unique = f"{handle}|{entry['name']}.{mix:04d}"
                    filt = status.get(unique, "unlisted")
                    if filt == "unlisted" and unique in cook:
                        filt = "cook_surface"
                    if filt in drop_filters:
                        continue
                    offset = sum(len(v) for v in group["verts"])
                    group["verts"].append(verts @ to_world[:3, :3].T + to_world[:3, 3])
                    group["faces"].append(faces + offset)
                    group["tags"].append(np.full(len(faces), len(group["names"])))
                    group["names"].append((f"{entry['name']}.{mix:04d}", filt,
                                           unique in within_set))
            for group in groups.values():
                if not group["verts"]:
                    continue
                wverts = np.vstack(group["verts"])
                faces = np.vstack(group["faces"])
                tags = np.concatenate(group["tags"])
                for lvl in split_levels(wverts, faces, tags):
                    if lvl["area"] < min_area:
                        continue
                    parts = [group["names"][t] for t in lvl["tags"]]
                    filters = [f for _, f, _ in parts]
                    covered_by = None
                    if articulated and not group["moving"] and boxes:
                        # the door test runs in the asset's root-link frame (y up, unscaled)
                        cy = lvl["center"] @ inv_world[:3, :3].T + inv_world[:3, 3]
                        covered_by = _behind_door(cy, boxes)
                    levels.append({
                        "receptacle": group["receptacle"], "link": group["link"],
                        "meshes": [n for n, _, _ in parts],
                        "moving_link": group["moving"], "covered_by": covered_by,
                        "hssd_filter": "active" if "active" in filters else filters[0],
                        "within_set": any(w for _, _, w in parts),
                        "kind": _classify(group["receptacle"], cat, group["moving"],
                                          covered_by is not None), **lvl})
            chair_levels: List[dict] = []
            if geometry:
                levels.extend(_geometry_additions(
                    template, world, articulated, cat, facts.get("name") or "", entries,
                    levels, geometry_mode))
                if geometry_mode == "chair":
                    chair_levels = rigid_geometry_spots(template, world, cat, ("surface",))
            pieces.append({"template": template, "handle": handle, "articulated": articulated,
                           "instance_index": index, "inst": inst, "facts": facts,
                           "levels": levels, "world": world, "chair_levels": chair_levels})

    # ---- rooms of furniture
    for piece in pieces:
        if piece["levels"]:
            w = np.array([lv["area"] for lv in piece["levels"]])
            c = np.array([lv["center"] for lv in piece["levels"]])
            probe = (c * w[:, None]).sum(0) / w.sum()
        else:
            probe = piece["world"][:3, 3] + np.array([0, 0.3, 0])
        room, dist = room_of_point(rooms, probe)
        piece["room"] = room["id"] if room else None
        piece["room_distance"] = round(dist, 3)
        piece["probe"] = probe
        if room is None or dist > MAX_ROOM_DISTANCE or not _same_storey(room, probe[1]):
            piece["dropped"] = (f"{dist:.1f} m from the nearest room" if room is not None
                                and _same_storey(room, probe[1]) else
                                f"at height {probe[1]:.1f} m, outside every storey")
    dropped = [{"template": p["template"], "category": p["facts"]["category"],
                "instance_list": ("articulated_object_instances" if p["articulated"]
                                  else "object_instances"),
                "instance_index": p["instance_index"], "reason": p["dropped"],
                "position": [round(float(v), 3) for v in p["probe"]]}
               for p in pieces if p.get("dropped")]
    pieces = [p for p in pieces if not p.get("dropped")]
    if geometry:
        _sole_chair_seats(pieces)
        _basins_at_taps(scene, rooms, pieces)

    # ---- furniture ids, ordered room by room then by position for stable numbering
    room_order = {r["id"]: i for i, r in enumerate(rooms)}
    pieces.sort(key=lambda p: (room_order.get(p["room"], 999), p["facts"]["category"],
                               p["articulated"], p["instance_index"]))
    cat_seen: Counter = Counter()
    furniture, spots = [], []
    out_of_reach = 0
    rooms_by_id = {r["id"]: r for r in rooms}
    for piece in pieces:
        cat = _slug(piece["facts"]["category"])
        cat_seen[cat] += 1
        fid = f"{cat}_{cat_seen[cat]}"
        piece["id"] = fid
        inst = piece["inst"]
        furniture.append({
            "id": fid, "room": piece["room"], "category": piece["facts"]["category"].replace("_", " "),
            "name": piece["facts"].get("name", ""), "template": piece["template"],
            "instance_index": piece["instance_index"],
            "instance_list": ("articulated_object_instances" if piece["articulated"]
                              else "object_instances"),
            "articulated": piece["articulated"],
            "position": [round(float(v), 4) for v in inst.get("translation", [0, 0, 0])],
            "rotation": inst.get("rotation", [1.0, 0.0, 0.0, 0.0]),
            "rotation_format": "wxyz quaternion (habitat)",
            "scale": inst.get("non_uniform_scale", inst.get("uniform_scale", 1.0)),
            "room_distance": piece["room_distance"],
            "bbox": ([[round(float(v), 3) for v in b] for b in _piece_bbox(piece)]
                     if _piece_bbox(piece) is not None else None),
        })
        # spots of this piece
        raw = []
        for lv in piece["levels"]:
            kind = lv["kind"]
            room, dist = room_of_point(rooms, lv["center"], margin=ROOM_MARGIN, prefer=piece["room"])
            rid = room["id"] if room else piece["room"]
            floor = rooms_by_id[rid]["floor_height"] if rid in rooms_by_id else 0.0
            if not -0.05 <= lv["height_y"] - floor <= max_height:
                out_of_reach += 1  # above reach, or below the floor (a broken asset)
                continue
            raw.append({"lv": lv, "kind": kind, "room": rid, "floor": floor,
                        "room_distance": dist})
        _name_spots(fid, piece["articulated"], raw)
        for r in raw:
            lv = r["lv"]
            if lv.get("geometry"):
                source = "geometry"
            else:
                source = "+".join(lv["meshes"]) if len(lv["meshes"]) <= 3 else \
                    f"{lv['meshes'][0]} and {len(lv['meshes']) - 1} more meshes of the same file"
                if lv["link"]:
                    source += f" on link {lv['link']}"
            spots.append({
                "id": r["id"], "furniture": fid, "room": r["room"], "kind": r["kind"],
                "source": source, "height": round(lv["height_y"] - r["floor"], 3),
                "area": round(lv["area"], 3),
                "center": [round(float(v), 4) for v in lv["center"]],
                "index": r["index"], "of": r["of"],
                "hssd_filter": lv["hssd_filter"], "behind_door": lv["covered_by"],
                "room_distance": round(r["room_distance"], 3),
            })
            if lv.get("geometry"):
                spots[-1]["geometry_from"] = lv["geometry"]
            if lv.get("reclassified"):
                spots[-1]["reclassified"] = lv["reclassified"]

    # ---- floors
    for room in rooms:
        p = _interior_point(room["_poly"])
        spots.append({"id": f"{room['id']}_floor", "furniture": None, "room": room["id"],
                      "kind": "surface", "source": f"region '{room['name']}' floor polygon",
                      "height": 0.0, "area": round(room["_area"], 3),
                      "center": [round(float(p[0]), 4), room["floor_height"], round(float(p[1]), 4)],
                      "index": 1, "of": 1, "hssd_filter": None, "behind_door": None,
                      "room_distance": 0.0})

    # make spot ids unique (should already be)
    seen_ids: Counter = Counter()
    for s in spots:
        seen_ids[s["id"]] += 1
        if seen_ids[s["id"]] > 1:
            s["id"] = f"{s['id']}_{seen_ids[s['id']]}"

    fixtures = _kitchen_fixtures(scene, rooms, spots)
    return {
        "scene": scene_id,
        "dataset": DATASET_NAME,
        "kitchen_fixtures": fixtures,
        "rooms": [{k: v for k, v in r.items() if not k.startswith("_")} for r in rooms],
        "furniture": furniture,
        "spots": spots,
        "notes": {
            "coordinates": "habitat world, y up, metres; polygon points are [x, z]",
            "instance_index": "index into the scene file list named by instance_list",
            "spot_height": "metres above the floor of the spot's room",
            "spot_index_of": "k of n distinct heights among this furniture's spots of the "
                             "same kind, 1 = lowest",
            "dropped_hssd_filters": sorted(drop_filters),
            "min_spot_area_m2": min_area,
            "max_spot_height_m": max_height,
            "spots_dropped_out_of_reach": out_of_reach,
            "furniture_dropped": dropped,
            "joint_pose": "all drawers and doors closed (joint value 0)",
        },
    }


def _name_spots(fid: str, articulated: bool, raw: List[dict]) -> None:
    """Give each spot of one piece of furniture its id, index and count.

    index/of: rank of the spot's height among the distinct heights (3 cm apart) of this
    furniture's spots of the same kind, 1 = lowest. Part names: an articulated
    receptacle keeps its authored name ("drawer_1", "inside_door_2_shelf_1"), with
    "_level_k" added when one receptacle holds several heights. A receptacle named only
    after the asset ("Dresser0017_receptacle_mesh") is named from its link when that
    moves ("drawer_1"), else "inside" if closed, "basin" if open, "top" if it is the
    highest surface of the piece and "shelf" otherwise. Rigid furniture has unnamed fragments, so its
    spots are named by height: "top" when it has one level, else "shelf_1".."shelf_n"
    from the bottom ("inside" / "inside_k" for open containers)."""
    by_kind = defaultdict(list)
    for r in raw:
        by_kind[r["kind"]].append(r)
    for group in by_kind.values():
        levels: List[float] = []
        for h in sorted(r["lv"]["height_y"] for r in group):
            if not levels or h - levels[-1] > 0.03:
                levels.append(h)
        for r in group:
            r["index"] = 1 + min(range(len(levels)),
                                 key=lambda i: abs(levels[i] - r["lv"]["height_y"]))
            r["of"] = len(levels)
    by_rec = defaultdict(list)
    for r in raw:
        key = r["lv"]["receptacle"]
        if r["lv"].get("part"):
            key = ("part", r["lv"]["part"])
        by_rec[key].append(r)
    for rec, group in by_rec.items():
        group.sort(key=lambda r: r["lv"]["height_y"])
        if isinstance(rec, tuple):  # a part named when the spot was made (seat, basin, drawer_1)
            for k, r in enumerate(group):
                r["part"] = rec[1] if len(group) == 1 else f"{rec[1]}_{k + 1}"
        elif articulated and rec != "geometry":
            base = _part_from_receptacle(rec)
            if not base:  # receptacle named after the whole asset
                link = group[0]["lv"]["link"] or ""
                link_part = _part_from_receptacle(link)
                if group[0]["lv"]["moving_link"] and link_part:
                    base = link_part              # e.g. "drawer_1"
                elif group[0]["kind"] == "closed":
                    base = "inside"
                elif group[0]["kind"] == "open":
                    base = "basin"
                else:
                    tops = [x["lv"]["height_y"] for x in raw if x["kind"] == "surface"]
                    highest = group[-1]["lv"]["height_y"] >= max(tops) - 0.05
                    base = "top" if highest else "shelf"
            for k, r in enumerate(group):
                r["part"] = base if len(group) == 1 else f"{base}_level_{k + 1}"
        else:
            for r in group:
                if r["kind"] == "open":
                    r["part"] = "inside" if r["of"] == 1 else f"inside_{r['index']}"
                elif r["kind"] == "closed":
                    r["part"] = "compartment" if r["of"] == 1 else f"compartment_{r['index']}"
                else:
                    r["part"] = "top" if r["of"] == 1 else f"shelf_{r['index']}"
    counts = Counter(r["part"] for r in raw)
    seen: Counter = Counter()
    for r in sorted(raw, key=lambda r: (r["part"], round(r["lv"]["center"][0], 3),
                                        round(r["lv"]["center"][2], 3))):
        seen[r["part"]] += 1
        part = r["part"] if counts[r["part"]] == 1 else f"{r['part']}_{seen[r['part']]}"
        r["id"] = f"{fid}_{part}"


def _kitchen_fixtures(scene: dict, rooms: List[dict], spots: List[dict]) -> Dict[str, List[str]]:
    """Evidence of a sink and a cooker in the home's kitchen(s).

    HSSD has no "sink" or "stove" field. Evidence counted: any object instance (furniture
    or not) standing in a kitchen whose category or catalogue name names a sink, tap or
    cooker, and any kitchen spot whose part name does ("kitchen_cabinet_1_sink_basin",
    "kitchen_cabinet_1_stovetop") or that HSSD marks as a cook surface. An all-in-one kitchen unit modelled as one cabinet with no
    sink receptacle and no tap object gives no evidence, so False means "HSSD does not
    record one", not "none is visible"."""
    kitchens = {r["id"] for r in rooms if r["type"] == "kitchen"}
    found: Dict[str, List[str]] = {"sink": [], "stove": []}
    if not kitchens:
        return found
    for key in ("object_instances", "articulated_object_instances"):
        for index, inst in enumerate(scene.get(key, [])):
            template = re.sub(r"\.(ao|object)_config\.json$", "",
                              inst["template_name"].split("/")[-1])
            facts = object_facts(template)
            cat, name = facts["category"], (facts.get("name") or "").lower()
            p = np.array(inst.get("translation", [0, 0, 0]), dtype=float) + [0, 0.5, 0]
            room, dist = room_of_point(rooms, p)
            if room is None or room["id"] not in kitchens or dist > ROOM_MARGIN:
                continue
            label = f"{cat} '{facts.get('name', '')}' ({key}[{index}])"
            if cat in SINK_CATEGORIES or cat in ("tap", "faucet") or "sink" in cat \
                    or re.search(r"\b(sink|faucet)\b", name):
                found["sink"].append(label)
            if cat in STOVE_CATEGORIES or "stove" in cat or "cooker" in cat \
                    or (re.search(r"\b(stove|stoves|cooker|hob|cooktop)\b", name)
                        and "hood" not in name and "hood" not in cat):
                found["stove"].append(label)
    for spot in spots:
        if spot["room"] not in kitchens or not spot["furniture"]:
            continue
        part = spot["id"][len(spot["furniture"]) + 1:]  # the part name, not the asset name
        if "sink" in part or "basin" in part:
            found["sink"].append(f"spot {spot['id']}")
        if any(w in part for w in STOVE_NAME_WORDS) or spot.get("hssd_filter") == "cook_surface":
            found["stove"].append(f"spot {spot['id']}")
    return found


# ================================================================== survey
def articulated_scene_ids() -> List[str]:
    return sorted(p.name.split(".")[0] for p in (HSSD / "scenes-articulated")
                  .glob("*.scene_instance.json"))


def summarise(home: dict) -> dict:
    rooms = home["rooms"]
    types = Counter(r["type"] for r in rooms)
    kinds = Counter(s["kind"] for s in home["spots"])
    furniture_spots = [s for s in home["spots"] if s["furniture"]]
    return {
        "scene": home["scene"],
        "rooms": len(rooms),
        "kitchens": types["kitchen"], "living_rooms": types["living"],
        "bedrooms": types["bedroom"], "bathrooms": types["bathroom"], "toilets": types["toilet"],
        "other_rooms": types["other"],
        "room_labels": dict(Counter(r["label"] for r in rooms)),
        "storeys": len({round(r["floor_height"], 1) for r in rooms}),
        "floor_area": round(sum(r["area"] for r in rooms), 1),
        "furniture": len(home["furniture"]),
        "articulated_furniture": sum(f["articulated"] for f in home["furniture"]),
        "spots": len(home["spots"]),
        "furniture_spots": len(furniture_spots),
        "spots_surface": kinds["surface"], "spots_open": kinds["open"],
        "spots_closed": kinds["closed"],
        "spots_outside_room": sum(1 for s in home["spots"] if s.get("room_distance", 0) > ROOM_MARGIN),
        "furniture_dropped": len(home["notes"]["furniture_dropped"]),
        "kitchen_sink": bool(home["kitchen_fixtures"]["sink"]),
        "kitchen_stove": bool(home["kitchen_fixtures"]["stove"]),
        **liveability(home),
    }


EAT_TABLE_WORDS = ("table", "kitchen_island", "bar", "counter_table", "dining")
NOT_EAT_TABLE = ("coffee", "side", "end_table", "bed", "night", "console", "dressing",
                 "tv", "changing", "wall_table", "foosball", "pool", "massage", "display",
                 "lamp_table", "small_table", "sink_table")
ENTRANCE_LABELS = {"entryway/foyer/lobby", "hallway"}
BED_EXCLUDE = ("dog_bed", "bed_table", "bed_stand", "massage_bed", "bedframe", "bed_small",
               "crib", "children_bed")


def _box_distance(p: Sequence[float], bbox) -> float:
    lo, hi = np.array(bbox[0]), np.array(bbox[1])
    dx = max(lo[0] - p[0], 0, p[0] - hi[0])
    dz = max(lo[2] - p[2], 0, p[2] - hi[2])
    return math.hypot(dx, dz)


def liveability(home: dict) -> dict:
    """Can two adults live here? Each check is read off the extracted home:
    eat_table      a table (dining table, kitchen island, bar; not coffee/side/bedside)
                   in a kitchen, dining or living room with a surface spot 0.65-1.15 m
                   high and at least 0.4 m2;
    beds           a double bed (narrow side of its bounding box >= 1.3 m) or two beds;
    kitchen_basin  an open spot in a kitchen on a sink (part, category or name);
    bathroom_basin the same in a bathroom or toilet room (a bathtub does not count);
    entrance_surface a surface spot 0.4-1.3 m high in an entryway or hallway (HSSD does
                   not mark the front door, so "near the entrance" means these rooms);
    bedside        for every bed, a surface spot 0.35-0.9 m high on other furniture in
                   its room within 0.8 m of the bed's bounding box;
    spots_100_200  100-200 spots in all."""
    rooms = {r["id"]: r for r in home["rooms"]}
    furn = {f["id"]: f for f in home["furniture"]}
    spots_of = defaultdict(list)
    for s in home["spots"]:
        if s["furniture"]:
            spots_of[s["furniture"]].append(s)

    def cat(f):
        return f["category"].replace(" ", "_")

    def is_sinky(s):
        f = furn[s["furniture"]]
        part = s["id"][len(f["id"]) + 1:]
        return s["kind"] == "open" and "tub" not in part and (
            "sink" in part or "basin" in part or cat(f) in SINK_CATEGORIES
            or bool(BASIN_NAME.search(f.get("name") or "")) and "bath" not in part)

    eating_rooms = {rid for rid, r in rooms.items()
                    if r["type"] in ("kitchen", "living") or "dining" in r["label"]}
    tables = []
    for f in home["furniture"]:
        c = cat(f)
        if not any(w in c for w in EAT_TABLE_WORDS) or any(w in c for w in NOT_EAT_TABLE):
            continue
        if f["room"] not in eating_rooms:
            continue
        if any(s["kind"] == "surface" and 0.65 <= s["height"] <= 1.15 and s["area"] >= 0.4
               for s in spots_of[f["id"]]):
            tables.append(f["id"])
    beds = [f for f in home["furniture"] if "bed" in cat(f)
            and not any(w in cat(f) for w in BED_EXCLUDE) and cat(f) != "sofa_bed"]
    doubles = [f["id"] for f in beds if f.get("bbox") and min(
        f["bbox"][1][0] - f["bbox"][0][0], f["bbox"][1][2] - f["bbox"][0][2]) >= 1.3]
    kitchen_basins = [s["id"] for s in home["spots"] if s["furniture"]
                      and rooms[s["room"]]["type"] == "kitchen" and is_sinky(s)]
    bath_basins = [s["id"] for s in home["spots"] if s["furniture"]
                   and rooms[s["room"]]["type"] in ("bathroom", "toilet") and is_sinky(s)]
    entrance = [s["id"] for s in home["spots"] if s["furniture"] and s["kind"] == "surface"
                and rooms[s["room"]]["label"] in ENTRANCE_LABELS and 0.4 <= s["height"] <= 1.3]
    bedside = {}
    for b in beds:
        if not b.get("bbox"):
            bedside[b["id"]] = []
            continue
        bedside[b["id"]] = [s["id"] for s in home["spots"] if s["furniture"]
                            and s["furniture"] != b["id"] and s["room"] == b["room"]
                            and s["kind"] == "surface" and 0.35 <= s["height"] <= 0.9
                            and _box_distance(s["center"], b["bbox"]) <= 0.8]
    checks = {
        "eat_table": bool(tables),
        "beds": bool(doubles) or len(beds) >= 2,
        "kitchen_basin_and_cooker": bool(kitchen_basins) and bool(home["kitchen_fixtures"]["stove"]),
        "bathroom_basin": bool(bath_basins),
        "entrance_surface": bool(entrance),
        "bedside_each_bed": bool(beds) and all(bedside.values()),
        "spots_100_200": 100 <= len(home["spots"]) <= 200,
    }
    return {"live_checks": checks, "live_score": sum(checks.values()),
            "live_evidence": {"tables": tables, "beds": [b["id"] for b in beds],
                              "double_beds": doubles, "kitchen_basins": kitchen_basins,
                              "bathroom_basins": bath_basins, "entrance_surfaces": entrance[:5],
                              "bedside": {k: v[:3] for k, v in bedside.items()}}}


def fits_two_adults(row: dict) -> bool:
    return (row["kitchens"] >= 1 and row["living_rooms"] >= 1 and row["bedrooms"] >= 2
            and row["bathrooms"] >= 1 and 100 <= row["spots"] <= 200)


def survey(scene_ids: Optional[Sequence[str]] = None, verbose: bool = False) -> List[dict]:
    rows = []
    for sid in scene_ids or articulated_scene_ids():
        try:
            row = summarise(extract(sid))
        except Exception as exc:  # report, do not hide
            row = {"scene": sid, "error": f"{type(exc).__name__}: {exc}"}
            print(f"[hssd_layout] {sid}: {row['error']}", file=sys.stderr)
        if "error" not in row:
            row["fits_two_adults"] = fits_two_adults(row)
        rows.append(row)
        if verbose:
            print(json.dumps(row), flush=True)
    return rows


def best_for_two_adults(rows: List[dict], n: int = 10) -> List[dict]:
    """Homes ordered by how livable they are for two adults: the number of the seven
    liveability checks met (see liveability), then the room brief (kitchen, living
    room, >= 2 bedrooms, >= 1 bathroom), then one storey, no spot outside its room, no
    furniture parked outside the house, bedrooms closest to 2, fewest other rooms and a
    spot count closest to 150."""
    ok = [r for r in rows if "error" not in r]
    return sorted(ok, key=lambda r: (-r["live_score"],
                                     not (r["kitchens"] >= 1 and r["living_rooms"] >= 1
                                          and r["bedrooms"] >= 2 and r["bathrooms"] >= 1),
                                     r["storeys"] > 1,
                                     r["spots_outside_room"] > 0,
                                     r["furniture_dropped"] > 0,
                                     abs(r["bedrooms"] - 2),
                                     r["other_rooms"],
                                     abs(r["spots"] - 150)))[:n]


def main(argv: Optional[List[str]] = None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scene", nargs="?", help="extract one scene to JSON (stdout or --out)")
    ap.add_argument("--out", help="write the JSON here")
    ap.add_argument("--survey", action="store_true", help="survey every articulated scene")
    args = ap.parse_args(argv)
    if args.survey:
        rows = survey(verbose=True)
        out = pathlib.Path(args.out) if args.out else REPO_RESULTS / "hssd_survey.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rows, indent=1))
        print(f"wrote {out}")
        print("best for two adults:")
        for r in best_for_two_adults(rows):
            print(f"  {r['scene']}: kitchen {r['kitchens']} living {r['living_rooms']} "
                  f"bedrooms {r['bedrooms']} bathrooms {r['bathrooms']} toilets {r['toilets']} "
                  f"other {r['other_rooms']} | furniture {r['furniture']} | spots {r['spots']} "
                  f"(surface {r['spots_surface']}, open {r['spots_open']}, closed "
                  f"{r['spots_closed']}) | sink {r['kitchen_sink']} stove {r['kitchen_stove']}"
                  f" | storeys {r['storeys']} area {r['floor_area']} m2")
            missing = [k for k, v in r["live_checks"].items() if not v]
            print(f"      liveability {r['live_score']}/7"
                  + (f", missing: {', '.join(missing)}" if missing else ""))
        return
    if not args.scene:
        ap.error("give a scene id or --survey")
    home = extract(args.scene)
    text = json.dumps(home, indent=1)
    if args.out:
        pathlib.Path(args.out).write_text(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
