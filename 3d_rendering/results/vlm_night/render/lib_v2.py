"""Settings for the second placement of household A (hssd_a_v2): lib.SnapshotHomeV2.

Import this before render_snapshot: it changes three module values of lib and nothing else, so
the 1.0 m views (spot_views.json), lens, picture size and file layout stay those of hssd_a.
The hssd_a pictures and the 1.0 m logs are not touched.

Environment override (for checks): PICS_V2 (picture folder).
"""
import os
import pathlib

import lib

RENDER = lib.CODE
lib.HOME_CLASS = lib.SnapshotHomeV2
lib.PICS = pathlib.Path(os.environ.get("PICS_V2", "/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_v2"))
lib.SPOT_VIEWS = RENDER / "spot_views.json"
# render_snapshot.py appends to lib.CODE / "logs" / "render_times.jsonl": send that to run_v2/logs/
lib.CODE = RENDER / "run_v2"
(lib.CODE / "logs" / "snapshots").mkdir(parents=True, exist_ok=True)
