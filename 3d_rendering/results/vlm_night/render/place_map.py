"""For each fixed view, which piece of furniture of the EMPTY home every pixel shows.

    ~/miniconda3/envs/dynamic_eqa/bin/python place_map.py

Used to file what the model lists in a patrol picture under the furniture it rests on, not
the furniture the camera points at. Only the empty home and the known camera poses are used
(no snapshot object is placed, no snapshot object id is read), so nothing about where things
are leaks in: this is the static map a robot would have of its home.

Per view, from the view's eye in the empty home:
  ids picture    each furniture mesh has its own id; a pixel showing a mesh that some place of
                 the household belongs to gets that furniture ("room|furniture", as world.py)
  depth picture  pixels showing the building (walls, floors) and lying within 10 cm of the
                 floor get "room|floor" for the room whose outline contains them
Everything else (walls, ceilings, furniture no place belongs to) is -1.

Writes ../questions/placed/maps/<spot>.npz with `label` (int16, -1 = none) and `keys`
(furniture keys), and a coloured preview <spot>.png for checking.
"""
from __future__ import annotations

import math
import sys
import time

import numpy as np
from matplotlib.path import Path as Poly
from PIL import Image

import lib

OUT = lib.CODE.parent / "questions" / "placed" / "maps"
FLOOR_Y = 0.10


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    views = lib.json.loads(lib.SPOT_VIEWS.read_text())["views"]
    cams = [dict(uuid="v_depth", kind="depth", width=lib.W, height=lib.H, hfov=lib.HFOV),
            dict(uuid="v_ids", kind="ids", width=lib.W, height=lib.H, hfov=lib.HFOV)]
    home = lib.open_home(lib.snapshot_path(7, "1800"), cams)      # the home is never populated
    places = home.snap["places"]
    keys, id_key, floors = [], {}, []
    def key_index(k):
        if k not in keys:
            keys.append(k)
        return keys.index(k)
    regions = {r["name"]: r for r in lib.scene.common_regions()}
    for p, v in places.items():
        k = f"{v['room']}|{v['furniture']}"
        src = v["geometry"].get("source", "")
        if v["furniture"] == "floor" and src.startswith("region"):
            poly = np.array(regions[src.split("'")[1]]["poly_loop"])[:, [0, 2]]
            floors.append((Poly(poly), key_index(k)))
            continue
        thing = home.furniture_of(p)
        if thing is None:
            continue
        for i in home.ids_of(thing):
            if i and i not in id_key:
                id_key[i] = key_index(k)
    print(f"{len(id_key)} furniture ids, {len(floors)} room floors, {len(keys)} keys ({time.time() - t0:.0f}s)", flush=True)
    f = (lib.W / 2) / math.tan(math.radians(lib.HFOV) / 2)
    cols, rows = np.meshgrid(np.arange(lib.W) + 0.5, np.arange(lib.H) + 0.5)
    palette = np.random.default_rng(0).integers(40, 255, size=(len(keys), 3)).astype(np.uint8)
    lut = np.full(max(id_key) + 1, -1, np.int16)
    for i, k in id_key.items():
        lut[i] = k
    for n, v in enumerate(views):
        eye = np.array(v["eye"])
        lib.common.look_from(home.sim, eye, np.array(v["target"]))
        seen = home.shoot("v_depth", "v_ids")
        depth, ids = seen["v_depth"], seen["v_ids"].astype(np.int64)
        label = np.where(ids <= max(id_key), lut[np.clip(ids, 0, max(id_key))], -1).astype(np.int16)
        turn = lib.camera_frame(home)
        local = np.stack([(cols - lib.W / 2) / f * depth, -(rows - lib.H / 2) / f * depth, -depth], -1)
        world = (local.reshape(-1, 3) @ turn.T + eye).reshape(lib.H, lib.W, 3)
        low = (label < 0) & (depth > 0.05) & (world[:, :, 1] < FLOOR_Y)
        rr, cc = np.nonzero(low)
        xz = world[rr, cc][:, [0, 2]]
        for poly, k in floors:
            inside = poly.contains_points(xz)
            label[rr[inside], cc[inside]] = k
        np.savez_compressed(OUT / f"{v['spot']}.npz", label=label, keys=np.array(keys))
        prev = np.full((lib.H, lib.W, 3), 20, np.uint8)
        prev[label >= 0] = palette[label[label >= 0]]
        Image.fromarray(prev).save(OUT / f"{v['spot']}.png")
        own = keys.index(f"{v['room']}|{v['furniture']}") if f"{v['room']}|{v['furniture']}" in keys else -2
        print(f"[{n + 1}/{len(views)}] {v['spot']}: {np.mean(label >= 0):.0%} of pixels on furniture or floor, "
              f"{np.mean(label == own):.0%} on its own furniture, {len(np.unique(label[label >= 0]))} pieces", flush=True)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    sys.exit(main())
