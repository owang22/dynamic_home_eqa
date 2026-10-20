# Go2 dog-height copy (2026-10-19 evidence-memory study), made from the 1p4 files with 1.4 -> 0.4.
"""Settings for the picture set of household A with the camera eye at 0.4 m
(near the Go2 camera height, 0.37 m).

Import this before choose_views / render_snapshot: it changes four module values of lib and
nothing else, so placement, lens, picture size, scoring and file layout stay those of the
1.0 m set. The 1.0 m files (spot_views.json, logs/, the hssd_a picture folder) are not touched.

Environment overrides (used only for the same-code check): PICS_0P4 (picture folder),
SPOT_VIEWS_0P4 (spot-view file name in this folder).
"""
import os
import pathlib

import lib

RENDER = lib.CODE
lib.EYE_HEIGHT = 0.4
lib.PICS = pathlib.Path(os.environ.get("PICS_0P4", "/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_0p4"))
lib.SPOT_VIEWS = RENDER / os.environ.get("SPOT_VIEWS_0P4", "spot_views_0p4.json")
# render_snapshot.py appends to lib.CODE / "logs" / "render_times.jsonl"; send that to
# run_0p4/logs/ so the 1.0 m logs are not appended to.
lib.CODE = RENDER / "run_0p4"
(lib.CODE / "logs" / "snapshots").mkdir(parents=True, exist_ok=True)
