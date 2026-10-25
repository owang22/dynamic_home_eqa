# navigation/localization/

**Owner: the control-PC agent (Z690).** Part of `navigation/`; same rules (see `../README.md`). Notes, results and
offline studies on where the dog is on the saved map: line-up, the drift tracker, heading drift, markers. The code
itself is flat in `../` (`go2_mapper.py`, `go2_markers.py`); full scripts and robot data stay on Z690.

| folder | what |
|---|---|
| `2026-10-25_overnight/` | Overnight offline study. Includes: the dog's `/point_cloud2` is a persistent voxel map (median voxel age 72 s); gyro bias while standing is +1.15 deg/min median (-4..+6); a replay harness of the deployed mapper over the 10-23 drive; a proposed patch (fresh-voxel tracking + heading hold) that holds 0.07-0.10 m / 1.4-1.9 deg where today's tracker ends 1.4-2.0 m off at +4..+6 deg/min drift; lost-flag delay; ArUco marker misses (overexposure, no hold), a fixed detector and gating for position fixes (`markers.md`). Proposed diffs, **not deployed**. |
