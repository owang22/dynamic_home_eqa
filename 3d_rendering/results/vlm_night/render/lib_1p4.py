"""Settings for the second picture set of household A with the camera eye at 1.4 m.

Import this before choose_views / render_snapshot: it changes four module values of lib and
nothing else, so placement, lens, picture size, scoring and file layout stay those of the
1.0 m set. The 1.0 m files (spot_views.json, logs/, the hssd_a picture folder) are not touched.

Environment overrides (used only for the same-code check): PICS_1P4 (picture folder),
SPOT_VIEWS_1P4 (spot-view file name in this folder).
"""
import os
import pathlib

import lib

RENDER = lib.CODE
lib.EYE_HEIGHT = 1.4
lib.PICS = pathlib.Path(os.environ.get("PICS_1P4", "/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_1p4"))
lib.SPOT_VIEWS = RENDER / os.environ.get("SPOT_VIEWS_1P4", "spot_views_1p4.json")
# render_snapshot.py appends to lib.CODE / "logs" / "render_times.jsonl"; send that to
# run_1p4/logs/ so the 1.0 m logs are not appended to.
lib.CODE = RENDER / "run_1p4"
(lib.CODE / "logs" / "snapshots").mkdir(parents=True, exist_ok=True)
