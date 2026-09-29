#!/usr/bin/env python3
"""How many questions each arm of one wave actually scored, and on which measure.

`found_at_step` and `found_it` exist for every row. `correct_place`/`correct_room` are None
when the arm produced no place at all - an unparsed completion, or last-seen never having seen
the object - so the denominator of exact-place accuracy is smaller than the denominator of
first-room-right, and it differs per arm.

    python3 results/self_improve/paper/scripts/scored_counts.py results/self_improve/overnight_wave
"""
import collections
import glob
import json
import sys


def main(argv) -> int:
    wave = argv[1] if len(argv) > 1 else "results/self_improve/overnight_wave"
    for arm in sorted(glob.glob(wave + "/cells/*")):
        rows = unscored = 0
        per_home = collections.Counter()
        homes = set()
        for f in glob.glob(arm + "/*/searches.jsonl"):
            home = f.split("/")[-2]
            homes.add(home)
            for line in open(f):
                r = json.loads(line)
                if r.get("kind") != "search":
                    continue
                rows += 1
                if r.get("correct_place") is None:
                    unscored += 1
                    per_home[home] += 1
        print(f"{arm.split('/')[-1]:44s} homes {len(homes):2d}  rows {rows:5d}  "
              f"no place answered {unscored:4d}  place-scored {rows - unscored:5d}  {dict(per_home)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
