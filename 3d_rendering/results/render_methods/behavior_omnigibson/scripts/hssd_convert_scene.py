"""Make plain-texture copies of every model one HSSD home uses (stage, static furniture,
articulated furniture with its URDF) under /mnt/nvme/.../behavior/hssd_import/<scene>/.

Files get a leading letter ("h" + hash) because OmniGibson's importer asserts that a file
name starts with a letter, and HSSD names are hex hashes.

Run with the tools venv python (has pygltflib):
  tools_venv/bin/python -I hssd_convert_scene.py 107734254_176000121
"""
import json
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hssd_unbasis import convert  # noqa: E402

HSSD = "/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab"
OUT = "/mnt/nvme/oliver/robot/render_methods/behavior/hssd_import"


def main(scene):
    out = os.path.join(OUT, scene)
    os.makedirs(os.path.join(out, "objects"), exist_ok=True)
    os.makedirs(os.path.join(out, "urdf"), exist_ok=True)
    inst = json.load(open(os.path.join(HSSD, "scenes-articulated", f"{scene}.scene_instance.json")))
    jobs = [(os.path.join(HSSD, "stages", f"{scene}.glb"), os.path.join(out, "stage.glb"))]
    for t in sorted({o["template_name"] for o in inst["object_instances"]}):
        sub = "openings" if "-" in t else t[0]  # doors and windows live in objects/openings
        jobs.append((os.path.join(HSSD, "objects", sub, f"{t}.glb"), os.path.join(out, "objects", f"h{t}.glb")))
    for t in sorted({o["template_name"] for o in inst["articulated_object_instances"]}):
        sdir, ddir = os.path.join(HSSD, "urdf", t), os.path.join(out, "urdf", f"h{t}")
        os.makedirs(ddir, exist_ok=True)
        for f in os.listdir(sdir):
            if f.endswith(".glb"):
                jobs.append((os.path.join(sdir, f), os.path.join(ddir, f)))
            elif f.endswith(".urdf"):
                txt = open(os.path.join(sdir, f)).read()
                open(os.path.join(ddir, f"h{t}.urdf"), "w").write(txt)
            else:
                shutil.copy(os.path.join(sdir, f), ddir)

    def run(j):
        try:
            return j[1], convert(*j), None
        except Exception as e:  # keep going, record the failure
            return j[1], 0, repr(e)

    with ThreadPoolExecutor(16) as ex:
        res = list(ex.map(run, jobs))
    fails = [r for r in res if r[2]]
    json.dump({"scene": scene, "files": len(res), "textures": sum(r[1] for r in res),
               "failures": fails}, open(os.path.join(out, "convert_summary.json"), "w"), indent=1)
    print(len(res), "files,", sum(r[1] for r in res), "textures,", len(fails), "failures")
    for f in fails[:10]:
        print("FAIL", f)


if __name__ == "__main__":
    main(sys.argv[1])
