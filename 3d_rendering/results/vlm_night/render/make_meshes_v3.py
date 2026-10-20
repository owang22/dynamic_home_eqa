"""Derived 3D models for v3, written as new GLB files (the source models are not changed).

    ~/miniconda3/envs/dynamic_eqa/bin/python make_meshes_v3.py

1. Folded cloth, tinted: every garment, napkin, pillowcase and throw in household A is drawn as one
   generic folded-cloth model (the plain cream folded towel, asked_about_models 'towel_35b76b'),
   with its fabric texture recoloured to the object's `color` from the positions file (COLOURS
   below; brightness pattern of the cloth kept). The T-pose garment meshes stood up as stiff hollow
   shells. One GLB per colour.
2. Several things as one model: an object that is several things ("three lemons", "three red
   tins", "a bunch of carrots") is one GLB holding that many copies of one model, lying side by
   side.
3. Laid flat: models that stood on an end (a glove on its cuff, a lemon on its tip) are turned so
   their shortest side is up (principal axes of the vertices); each copy in 2 is laid flat too.

Writes MESHES/<name>.glb and models_v3_built.json (rules in the models_v3.json format, applied
after models_v3.json: by_object > by_model > by_type). Re-run after changing anything here.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import trimesh
from PIL import Image

import lib

RENDER = pathlib.Path(__file__).resolve().parent
MESHES = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/meshes_v3")
OUT = RENDER / "models_v3_built.json"
OBJAVERSE = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/habitat_hssd/objaverse/hf-objaverse-v1/glbs")
TOWEL = pathlib.Path("/home/oliver/robot/dynamic_home_eqa_archive/data/objects/external_props/meshes/towel_35b76b90614d.glb")

COLOURS = {   # colour word in the positions file -> sRGB
    "black": (38, 38, 40), "white": (236, 234, 228), "gray": (140, 140, 140), "charcoal": (64, 66, 70),
    "blue": (90, 130, 190), "blue and white": (150, 175, 215), "blue gray": (120, 140, 160),
    "navy": (35, 45, 85), "indigo": (50, 60, 110), "dark indigo": (35, 42, 80), "faded blue": (120, 150, 185),
    "ivory": (240, 234, 214), "oatmeal": (205, 192, 168), "ochre": (200, 140, 50), "rust": (165, 75, 40),
    "rust orange": (190, 90, 45), "olive green": (110, 115, 60), "sage green": (150, 170, 135),
    "mustard yellow": (210, 165, 40), "dark brown": (75, 50, 35), "brown": (120, 80, 50), "red": (180, 40, 40),
    "green": (70, 130, 70), "yellow": (230, 200, 60), "pink": (225, 160, 170), "cream": (235, 225, 200),
}
# type -> longest side (m) of the folded cloth
CLOTH = {"sleep shirt": 0.32, "sleep pants": 0.32, "work blouse": 0.32, "work trousers": 0.36, "lounge pants": 0.34,
         "work cardigan": 0.34, "evening sweater": 0.34, "restaurant shirt": 0.32, "evening shirt": 0.32,
         "chef jacket": 0.36, "jacket": 0.38, "robe": 0.40, "dress": 0.34, "jeans": 0.36, "hoodie": 0.36,
         "linen scarf": 0.28, "apron": 0.30, "socks": 0.15, "wool socks": 0.16, "cloth napkin": 0.20,
         "napkins": 0.24, "pillowcase": 0.36, "throw blanket": 0.42}
# type -> (source glb, copies, longest side of the group (m), what)
GROUPS = {
    "lemons": (OBJAVERSE / "000-089/ed58014072a64680b0fe5ce4cac6234c.glb", 3, 0.17, "three lemons lying together"),
    "canned tomatoes": (OBJAVERSE / "000-103/640b0c8287274629a7f4ff3ce74a5999.glb", 3, 0.25, "three tins in a row"),
    "carrots": (OBJAVERSE / "000-115/583b980bb3c4432abe5422d8a54ffe99.glb", 4, 0.22, "a bunch of four carrots"),
}
# type -> (source glb, longest side (m), what): laid flat, one copy
FLAT = {
    "gardening gloves": (OBJAVERSE / "000-127/79a3902f37f2482c97520f3f19e419ab.glb", 0.25, "glove laid flat"),
    "rubber gloves": (OBJAVERSE / "000-127/79a3902f37f2482c97520f3f19e419ab.glb", 0.28, "glove laid flat"),
    "pruning shears": (pathlib.Path("/home/oliver/robot/dynamic_home_eqa_archive/data/objects/external_props/meshes/"
                                    "shears_0019c537f588.glb"), 0.20, "pruning shears laid flat"),
}


def find(path: pathlib.Path) -> pathlib.Path:
    if path.exists():
        return path
    hits = list(OBJAVERSE.glob(f"*/{path.name}"))
    if not hits:
        raise FileNotFoundError(path)
    return hits[0]


def load(path) -> trimesh.Scene:
    return trimesh.load(str(find(pathlib.Path(path))), force="scene")


def flat_transform(scene: trimesh.Scene) -> np.ndarray:
    """Rotation (4x4) that puts the vertices' smallest principal axis on +y and the largest on x."""
    v = np.vstack([g.vertices for g in scene.dump(concatenate=False)])
    v = v - v.mean(axis=0)
    _, _, vt = np.linalg.svd(v[np.random.default_rng(0).choice(len(v), min(len(v), 20000), replace=False)],
                             full_matrices=False)
    long_ax, mid_ax, short_ax = vt[0], vt[1], vt[2]
    R = np.vstack([long_ax, short_ax, np.cross(long_ax, short_ax)])     # rows: new x, y, z
    if np.linalg.det(R) < 0:
        R[2] *= -1
    T = np.eye(4)
    T[:3, :3] = R
    return T


def to_unit(scene: trimesh.Scene, longest: float) -> trimesh.Scene:
    lo, hi = scene.bounds
    s = longest / float(np.max(hi - lo))
    scene.apply_scale(s)
    lo, hi = scene.bounds
    scene.apply_translation([-(lo[0] + hi[0]) / 2, -lo[1], -(lo[2] + hi[2]) / 2])
    return scene


def tinted_cloth(rgb, name):
    out = MESHES / f"cloth_{name}.glb"
    s = load(TOWEL)
    for g in s.geometry.values():
        mat = g.visual.material
        tex = np.asarray(mat.baseColorTexture.convert("RGB"), float)
        lum = tex.mean(axis=2, keepdims=True)
        lum = lum / max(float(lum.mean()), 1e-3)
        # keep the fold shading but soften it so dark colours do not go black
        img = np.clip(np.array(rgb, float)[None, None, :] * (0.55 + 0.45 * lum), 0, 255).astype(np.uint8)
        mat.baseColorTexture = Image.fromarray(img)
        mat.baseColorFactor = None
    s.export(str(out))
    return out


def baked_group(src, n, longest, name):
    """Copies of a model, each with its node transforms baked into vertices, side by side."""
    out = MESHES / f"group_{name}.glb"
    base = load(src)
    meshes = base.dump(concatenate=False)                      # world-space meshes
    one = trimesh.Scene(meshes)
    T = flat_transform(one)
    if name == "canned_tomatoes":      # a can stands on its end: its longest axis up
        T = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]) @ T
    one.apply_transform(T)
    meshes = one.dump(concatenate=False)
    lo, hi = trimesh.Scene(meshes).bounds
    size = hi - lo
    parts = []
    for k in range(n):
        if name == "carrots":
            R = trimesh.transformations.rotation_matrix(np.radians(-10 + 7 * k), [0, 1, 0])
            T = trimesh.transformations.translation_matrix([0, 0, k * size[2] * 0.9])
            M = T @ R
        elif name == "lemons":
            dx, dz = [(0, 0), (size[0] * 0.92, 0), (size[0] * 0.46, size[2] * 0.85)][k]
            M = trimesh.transformations.translation_matrix([dx, 0, dz])
        else:
            M = trimesh.transformations.translation_matrix([k * size[0] * 1.03, 0, 0])
        for m in meshes:
            c = m.copy()
            c.apply_transform(M)
            parts.append(c)
    s = to_unit(trimesh.Scene(parts), longest)
    s.export(str(out))
    return out


def laid_flat(src, longest, name):
    out = MESHES / f"flat_{name}.glb"
    s = trimesh.Scene(load(src).dump(concatenate=False))
    s.apply_transform(flat_transform(s))
    to_unit(s, longest).export(str(out))
    return out


def main():
    MESHES.mkdir(parents=True, exist_ok=True)
    snap = json.load(lib.snapshot_path(4, "1000").open())
    rules = {"by_object": {}, "by_type": {}, "note": __doc__.split("\n\n")[0]}
    made = {}
    for oid, o in sorted(snap["objects"].items()):
        if o["type"] not in CLOTH:
            continue
        col = o.get("color") or "cream"
        rgb = COLOURS.get(col)
        if rgb is None:
            raise KeyError(f"no colour for {col!r} ({oid})")
        key = col.replace(" ", "_")
        if key not in made:
            made[key] = tinted_cloth(rgb, key)
        rules["by_object"][oid] = {
            "mesh": str(made[key]), "id": f"folded_cloth_{key}", "source": "built", "longest_m": CLOTH[o["type"]],
            "looks_like": f"folded cloth, {col}", "stand_in": True,
            "why": f"garment / cloth drawn as one generic folded cloth tinted {col} (the garment meshes were "
                   "stiff hollow shells standing up)", "found_by": "independent visual audit + look check"}
    for typ, (src, n, longest, what) in GROUPS.items():
        p = baked_group(src, n, longest, typ.replace(" ", "_"))
        rules["by_type"][typ] = {"mesh": str(p), "id": f"group_{typ.replace(' ', '_')}", "source": "built",
                                 "longest_m": longest, "looks_like": what, "stand_in": False,
                                 "why": f"the object is {what}; it was drawn as one", "found_by": "independent visual audit"}
    for typ, (src, longest, what) in FLAT.items():
        p = laid_flat(src, longest, typ.replace(" ", "_"))
        rules["by_type"][typ] = {"mesh": str(p), "id": f"flat_{typ.replace(' ', '_')}", "source": "built",
                                 "longest_m": longest, "looks_like": what, "stand_in": False,
                                 "why": f"the model stood on one end ({what})",
                                 "found_by": "independent visual audit"}
    lib.json_dump(rules, OUT)
    print(len(rules["by_object"]), "cloth objects,", len(made), "colours;", len(rules["by_type"]), "type rules ->", OUT)


if __name__ == "__main__":
    main()
