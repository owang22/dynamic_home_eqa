"""Step 1: load BEHAVIOR's house_single_floor with all its objects, record load time and GPU
memory, list every object with room, category and box, and render one test picture per room."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from og_common import OUT, PIC, aim, coverage, dump, gpu_mem_mib, make_env, render, save_png  # noqa: E402

import omnigibson as og  # noqa: E402

SCENE = sys.argv[1] if len(sys.argv) > 1 else "house_single_floor"
mem0 = gpu_mem_mib()
env, load_s = make_env({"type": "InteractiveTraversableScene", "scene_model": SCENE})
scene = env.scene
print("LOADED", SCENE, round(load_s, 1), "s", flush=True)
objs = []
for o in scene.objects:
    try:
        lo, hi = o.aabb
        objs.append(dict(name=o.name, category=o.category, rooms=getattr(o, "in_rooms", None),
                         model=getattr(o, "model", None), lo=lo.tolist(), hi=hi.tolist(),
                         openable="open" in [s.__name__.lower() for s in o.states]))
    except Exception as e:
        objs.append(dict(name=o.name, category=o.category, error=repr(e)))
dump(objs, f"{OUT}/mapping/{SCENE}_objects.json")
cam = env.external_sensors[0]["cam_1"] if env.external_sensors else None
cam = list(env.external_sensors[0].values())[1]
# One look per room: from the room's floor centre, 1.0 m up, toward its biggest piece of furniture.
import collections  # noqa: E402
import numpy as np  # noqa: E402
rooms = collections.defaultdict(list)
for o in objs:
    if o.get("rooms") and "lo" in o:
        rooms[o["rooms"][0]].append(o)
times = []
order = sorted(rooms.items())
first = os.environ.get("FIRST_ROOM")
if first:
    order = sorted(order, key=lambda kv: kv[0] != first)
for room, lst in order:
    floor = [o for o in lst if o["category"] == "floors"]
    furn = [o for o in lst if o["category"] not in ("floors", "ceilings", "walls", "downlight", "electric_switch",
                                                      "fixed_window", "baseboard", "room_light")]
    if not floor or not furn:
        continue
    c = (np.array(floor[0]["lo"]) + np.array(floor[0]["hi"])) / 2
    big = max(furn, key=lambda o: np.prod(np.array(o["hi"]) - np.array(o["lo"])))
    t = (np.array(big["lo"]) + np.array(big["hi"])) / 2
    eye = [c[0], c[1], floor[0]["hi"][2] + 1.0]
    print("AIM", room, [round(float(x), 2) for x in eye], [round(float(x), 2) for x in t], flush=True)
    aim(cam, eye, t)
    t0 = time.time()
    rgb, seg, idm, _ = render(cam)
    times.append(time.time() - t0)
    save_png(rgb, f"{PIC}/load_check/{SCENE}_{room}.png")
    cov = coverage(seg, idm)
    print("ROOM", room, "target", big["name"], "mean px", round(float(rgb.mean()), 1),
          "top", sorted(cov.items(), key=lambda x: -x[1])[:4], flush=True)
dump(dict(scene=SCENE, load_seconds=load_s, gpu_mib_before=mem0, gpu_mib_after=gpu_mem_mib(),
          render_seconds=times, n_objects=len(objs)), f"{OUT}/mapping/{SCENE}_load.json")
print("GPU", mem0, gpu_mem_mib(), "render s", [round(x, 3) for x in times], flush=True)
og.shutdown()
