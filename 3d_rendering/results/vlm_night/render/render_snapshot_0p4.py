# Go2 dog-height copy (2026-10-19 evidence-memory study), made from the 1p4 files with 1.4 -> 0.4.
"""render_snapshot.py with the 0.4 m stands (spot_views_0p4.json) into hssd_a_0p4/.
Same placement code, same snapshot files, same output layout and truth.json format.

    ~/miniconda3/envs/dynamic_eqa/bin/python render_snapshot_0p4.py <day> <HHMM> [--force]
"""
import sys

import lib_0p4  # noqa: F401
import render_snapshot

if __name__ == "__main__":
    sys.exit(render_snapshot.main())
