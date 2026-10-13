"""render_snapshot.py with the 1.4 m stands (spot_views_1p4.json) into hssd_a_1p4/.
Same placement code, same snapshot files, same output layout and truth.json format.

    ~/miniconda3/envs/dynamic_eqa/bin/python render_snapshot_1p4.py <day> <HHMM> [--force]
"""
import sys

import lib_1p4  # noqa: F401
import render_snapshot

if __name__ == "__main__":
    sys.exit(render_snapshot.main())
