"""Import HSSD furniture into OmniGibson's own object format with OmniGibson's custom-asset
tools (generate_urdf_for_mesh + import_og_asset_from_urdf), into the dataset "hssd-assets".

The shipped example `python -m omnigibson.examples.objects.import_custom_object` fails in
v3.9.3-post2 (it passes keep_instanceable=, which import_og_asset_from_urdf no longer takes),
so this calls the same two functions directly.

Input: a JSON list of jobs, each {"kind": "mesh"|"urdf", "path": ..., "category": ..., "model": ...}
(model: 6 lowercase letters, as OmniGibson requires).

  OMNIGIBSON_HEADLESS=1 conda_env/bin/python hssd_og_import.py jobs.json
"""
import json
import os
import sys
import tempfile
import time
import traceback

import omnigibson as og  # noqa: F401
from omnigibson.utils.asset_conversion_utils import generate_urdf_for_mesh, import_og_asset_from_urdf
from omnigibson.utils.asset_utils import get_dataset_path

DATASET = os.environ.get("HSSD_DATASET", "hssd-assets")


def main(jobs_path):
    jobs = json.load(open(jobs_path))
    os.makedirs(get_dataset_path(DATASET), exist_ok=True)
    out = []
    for j in jobs:
        t0 = time.time()
        rec = dict(j)
        try:
            usd = os.path.join(get_dataset_path(DATASET), "objects", j["category"], j["model"], "usd",
                               f"{j['model']}.usd")
            if os.path.exists(usd) or os.path.exists(usd.replace(".usd", ".encrypted.usd")):
                rec.update(status="exists")
            else:
                if j["kind"] == "mesh":
                    tmp = tempfile.mkdtemp()
                    urdf = generate_urdf_for_mesh(j["path"], tmp, j["category"], j["model"],
                                                  collision_method=j.get("collision", "convex"),  # None = visual only
                                                  up_axis="y", overwrite=True)
                    coll = None  # collision already made by generate_urdf_for_mesh
                else:
                    urdf = j["path"]
                    coll = j.get("collision", "convex")
                _, usd_path, _ = import_og_asset_from_urdf(category=j["category"], model=j["model"],
                                                           dataset_name=DATASET, urdf_path=str(urdf),
                                                           collision_method=coll, overwrite=True)
                rec.update(status="ok", usd=usd_path)
        except Exception as e:
            rec.update(status="fail", error=repr(e), tb=traceback.format_exc()[-1500:])
        rec["seconds"] = round(time.time() - t0, 1)
        print("IMPORT", json.dumps({k: rec[k] for k in ("model", "category", "status", "seconds")}), flush=True)
        out.append(rec)
        json.dump(out, open(jobs_path.replace(".json", "_result.json"), "w"), indent=1)
    og.shutdown()


if __name__ == "__main__":
    main(sys.argv[1])
