"""render_snapshot.py with the second placement (lib.SnapshotHomeV2) into hssd_a_v2/.
Same views, same snapshot files, same output layout; truth.json adds `repairs` (see README.md, "Second placement").

    ~/miniconda3/envs/dynamic_eqa/bin/python render_snapshot_v2.py <day> <HHMM> [--force]
"""
import sys

import lib_v2  # noqa: F401
import render_snapshot

if __name__ == "__main__":
    sys.exit(render_snapshot.main())
